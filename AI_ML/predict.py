import joblib
import pandas as pd
import os
import math
from logic import _pick_nearest_record, assess_rwh, compute_tank_dimensions
from estimate_cost import estimate_cost
from rooftopDetector import getRooftopDetailed

BASE_DIR = os.path.dirname(__file__)

clf = joblib.load(os.path.join(BASE_DIR, "models/structure_classifier.pkl"))
dimension_models = joblib.load(os.path.join(BASE_DIR, "models/dimension_regressors.pkl"))

db = pd.read_csv(os.path.join(BASE_DIR, "data/processed/wells_with_rainfall.csv"))

_RUNOFF_COEFF = {'gi':0.9, 'asbestos':0.8, 'tiled':0.75, 'concrete':0.7}

_PERMEABLE_KWS = ['sand','sandy','gravel','alluv','alluvial']
_HARDROCK_KWS = ['basalt','granite','gneiss','hard rock','rock','fracture']

dimension_map = {
    'store_on_roof': ['tank_height_m','tank_diameter_m','tank_volume_l'],
    'recharge_well_or_injection': ['well_depth_m','well_diameter_m','injection_capacity_lps'],
    'recharge_on_site_pit': ['pit_depth_m','pit_diameter_m'],
    'recharge_shaft': ['shaft_depth_m','shaft_diameter_m'],
    'community_recharge_or_combination': ['comm_structure_depth_m','comm_structure_diameter_m'],
    'recharge_shaft_or_community': ['comm_structure_depth_m','comm_structure_diameter_m']
}

def _estimate_design_inflow_lps(rooftop_area_m2: float, roof_type: str) -> float:
    coeff = _RUNOFF_COEFF.get(str(roof_type).lower(), 0.7)
    return max(0.0, rooftop_area_m2 * coeff * (0.05 * 1000.0 / 3600.0))

def _is_permeable(soil: str, lith: str) -> bool:
    s = (soil or '').lower(); l = (lith or '').lower()
    return any(k in s for k in _PERMEABLE_KWS) or any(k in l for k in _PERMEABLE_KWS)

def _is_hardrock(lith: str) -> bool:
    l = (lith or '').lower()
    return any(k in l for k in _HARDROCK_KWS)

def _clamp_dimensions(structure: str, dims: dict, enriched: dict, rec: pd.Series) -> dict:
    rooftop_area = float(enriched['rooftop_area_m2'])
    open_area = float(enriched['open_area_m2'])
    roof_type = enriched['roof_type']
    depth_mbgl = rec.get('depth_mbgl', None)
    inflow_lps = _estimate_design_inflow_lps(rooftop_area, roof_type)

    out = dict(dims) if isinstance(dims, dict) else {}

    if structure == 'recharge_well_or_injection':
        # Depth: 6–15 m typical, not deeper than water level + 2 m if available
        if 'well_depth_m' in out:
            min_depth = 6.0
            max_depth = 15.0
            if depth_mbgl and pd.notna(depth_mbgl):
                max_depth = min(max_depth, float(depth_mbgl) + 2.0)
            out['well_depth_m'] = float(max(min_depth, min(max_depth, out['well_depth_m'])))
        if 'well_diameter_m' in out:
            out['well_diameter_m'] = float(max(0.2, min(0.3, out['well_diameter_m'])))
        if 'injection_capacity_lps' in out:
            cap_small_roof = 1.0 if rooftop_area < 100 else inflow_lps
            cap = max(0.2, min(cap_small_roof, inflow_lps if inflow_lps > 0 else cap_small_roof))
            out['injection_capacity_lps'] = float(max(0.2, min(cap, out['injection_capacity_lps'])))

    elif structure == 'recharge_on_site_pit':
        if 'pit_depth_m' in out:
            out['pit_depth_m'] = float(max(1.5, min(3.5, out['pit_depth_m'])))
        if 'pit_diameter_m' in out:
            out['pit_diameter_m'] = float(max(1.0, min(3.0, out['pit_diameter_m'])))

    elif structure == 'recharge_shaft':
        if 'shaft_depth_m' in out:
            # Typical 2–8 m, avoid deeper than water level + 2 m if available
            min_d = 2.0
            max_d = 8.0
            if depth_mbgl and pd.notna(depth_mbgl):
                max_d = min(max_d, float(depth_mbgl) + 2.0)
            out['shaft_depth_m'] = float(max(min_d, min(max_d, out['shaft_depth_m'])))
        if 'shaft_diameter_m' in out:
            out['shaft_diameter_m'] = float(max(0.8, min(1.5, out['shaft_diameter_m'])))

    elif structure == 'store_on_roof':
        # Keep volume practical; if present ensure positive
        if 'tank_volume_l' in out:
            out['tank_volume_l'] = float(max(500.0, out['tank_volume_l']))
        if 'tank_height_m' in out:
            out['tank_height_m'] = float(max(1.0, min(2.0, out['tank_height_m'])))
        if 'tank_diameter_m' in out:
            out['tank_diameter_m'] = float(max(0.8, min(3.0, out['tank_diameter_m'])))

    return out

def _heuristic_dimensions(structure: str, enriched: dict, rec: pd.Series) -> dict:
    rooftop_area = float(enriched['rooftop_area_m2'])
    open_area = float(enriched['open_area_m2'])
    roof_type = enriched['roof_type']
    depth_mbgl = rec.get('depth_mbgl', None)
    inflow_lps = _estimate_design_inflow_lps(rooftop_area, roof_type)

    if structure == 'recharge_shaft':
        depth = 3.0
        if depth_mbgl and pd.notna(depth_mbgl):
            depth = max(2.0, min(6.0, float(depth_mbgl)))
        return {'shaft_depth_m': depth, 'shaft_diameter_m': 1.0}
    if structure == 'recharge_on_site_pit':
        diameter = max(1.0, min(3.0, (open_area ** 0.5) if open_area > 0 else 2.0))
        return {'pit_depth_m': 2.5, 'pit_diameter_m': round(diameter, 2)}
    if structure == 'recharge_well_or_injection':
        depth = 8.0
        if depth_mbgl and pd.notna(depth_mbgl):
            depth = max(6.0, min(12.0, float(depth_mbgl) + 1.0))
        cap = min(1.0 if rooftop_area < 100 else inflow_lps, max(0.2, inflow_lps))
        return {'well_depth_m': depth, 'well_diameter_m': 0.25, 'injection_capacity_lps': round(max(0.2, cap),2)}
    if structure == 'store_on_roof':
        # Very rough: 1500–5000 L small household tank
        return {'tank_height_m': 1.4, 'tank_diameter_m': 1.6, 'tank_volume_l': 3000.0}
    return {}

def _postprocess_structure(pred_type: str, enriched: dict, rec: pd.Series) -> str:
    rooftop_area = float(enriched['rooftop_area_m2'])
    open_area = float(enriched['open_area_m2'])
    soil = rec.get('soil_type', '')
    lith = rec.get('lithology_type', '')

    if pred_type == 'recharge_well_or_injection':
        # Avoid recommending injection for small roofs or tiny plots
        if rooftop_area < 80 or open_area < 4.0:
            if _is_hardrock(lith):
                return 'recharge_shaft'
            elif _is_permeable(soil, lith) and open_area >= 4.0:
                return 'recharge_on_site_pit'
            else:
                return 'store_on_roof'
    return pred_type

def predict_structure_and_dimensions(user_input: dict, db: pd.DataFrame):
    """
    Predicts structure type & dimensions for given user input.
    user_input keys:
        - lat, lon (floats)
        - rooftop_area_m2 (float)
        - open_area_m2 (float)
        - roof_type (str)
        - num_persons (int)
        - per_capita (optional, lpcd)
        - period_days (optional)
    All other hydrogeology parameters are looked up from nearest well in DB.
    """
    lat = float(user_input['lat'])
    lon = float(user_input['lon'])
    rec = _pick_nearest_record(db, lat, lon)
    if rec is None:
        raise ValueError("No nearby well found in DB.")
    record_distance = float(rec.get('_distance_km', 0.0))
    if record_distance > 50:
        raise ValueError(f"The groundwater dataset is Bengaluru-focused; the nearest observation is {record_distance:.1f} km away. Use a Bengaluru location or load local groundwater data.")

    # Softer defaults if not provided or provided as None by caller
    per_capita = user_input.get('per_capita') if user_input.get('per_capita') is not None else 35
    period_days = user_input.get('period_days') if user_input.get('period_days') is not None else 90
    # If no area is supplied, ask the optional imagery/footprint detector.
    provided_roof_area = user_input.get('rooftop_area_m2')
    rooftop_detection_data = None
    if provided_roof_area is None:
        try:
            detected_area, marked_image, detection_source = getRooftopDetailed(lat, lon, zoom=19)
        except Exception as exc:
            raise ValueError(f"Automatic roof detection is unavailable ({exc}). Enter the roof area manually and retry.") from exc
        if not detected_area or detected_area <= 0:
            raise ValueError("No mapped roof footprint was found at this location. Enter the roof area manually and retry.")
        rooftop_area_value = detected_area
        # Convert image to base64 for frontend display
        import base64
        import cv2
        from io import BytesIO
        if marked_image is not None:
            # Convert BGR to RGB for web display
            marked_image_rgb = cv2.cvtColor(marked_image, cv2.COLOR_RGB2BGR)
            # Encode as JPEG
            _, buffer = cv2.imencode('.jpg', marked_image_rgb)
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            rooftop_detection_data = {
                'detected_area_m2': detected_area,
                'detection_image': f"data:image/jpeg;base64,{img_base64}",
                'source': detection_source,
                'attribution': 'Map data © OpenStreetMap contributors' if 'OpenStreetMap' in detection_source else 'Satellite imagery © Esri',
                'coordinates': {
                    'lat': user_input.get('lat'),
                    'lon': user_input.get('lon')
                }
            }
    else:
        rooftop_area_value = provided_roof_area
    enriched = {
        'rooftop_area_m2': rooftop_area_value,
        'open_area_m2': user_input['open_area_m2'],
        'roof_type': str(user_input['roof_type']).strip().lower(),
        'num_persons': user_input['num_persons'],
        'per_capita': per_capita,
        'period_days': period_days,
        'rainfall_mm': rec['mean_annual_rainfall'],
        'soil_type': rec['soil_type'],
        'lithology_type': rec['lithology_type'],
        'depth_mbgl': rec['depth_mbgl']
    }

    # Rule-based assessment for explanation
    rule_assess = assess_rwh(
        db=db,
        rooftop_area=enriched['rooftop_area_m2'],
        lat=user_input['lat'], lon=user_input['lon'],
        open_area=enriched['open_area_m2'],
        roof_type=enriched['roof_type'],
        num_persons=enriched['num_persons'],
        per_capita=enriched['per_capita'],
        period_days=enriched['period_days']
    )

    sample = pd.DataFrame([enriched])

    # The classifier is retained as a model signal, while physical water balance
    # and the same hydrogeology rules used to create labels make the final choice.
    # This avoids synthetic-label bias swamping the user's actual inputs.
    pred_type_raw = str(clf.predict(sample)[0])
    try:
        model_confidence = float(max(clf.predict_proba(sample)[0]))
    except (AttributeError, ValueError, TypeError):
        model_confidence = None

    raw_rule_action = rule_assess['recommended_action']
    pred_type = 'recharge_shaft' if raw_rule_action == 'recharge_shaft_or_community' else raw_rule_action

    # Run the dimension regressors for diagnostics when that model supports the
    # selected class. Final dimensions are physically recalculated from inputs.
    model_dimension_estimates = {}
    if pred_type in dimension_models:
        try:
            estimates = dimension_models[pred_type].predict(sample)[0]
            model_dimension_estimates = dict(zip(dimension_map[pred_type], map(float, estimates)))
        except (ValueError, KeyError, TypeError):
            model_dimension_estimates = {}

    roof_area = float(enriched['rooftop_area_m2'])
    open_area = float(enriched['open_area_m2'])
    rainfall = float(enriched['rainfall_mm'] or 0)
    runoff = _RUNOFF_COEFF.get(enriched['roof_type'], 0.7)
    annual_harvest = rainfall * roof_area * runoff
    demand = float(enriched['num_persons']) * float(enriched['per_capita']) * float(enriched['period_days'])
    depth = float(rec.get('depth_mbgl') or 0) if pd.notna(rec.get('depth_mbgl')) else 0.0
    if pred_type == 'store_on_roof':
        preferred_height = min(2.0, max(1.0, model_dimension_estimates.get('tank_height_m', 1.4)))
        tank = compute_tank_dimensions(demand, preferred_height)
        dimensions = {'tank_height_m': round(tank['height_m'], 2), 'tank_diameter_m': tank['diameter_m'], 'tank_volume_l': round(demand)}
    elif pred_type == 'recharge_on_site_pit':
        pit_depth = model_dimension_estimates.get('pit_depth_m', depth - 0.5 if depth > 1 else 2.5)
        pit_diameter = model_dimension_estimates.get('pit_diameter_m', math.sqrt(max(open_area, 1)))
        dimensions = {'pit_depth_m': round(min(3.5, max(1.5, pit_depth)), 2), 'pit_diameter_m': round(min(3.0, max(1.0, min(pit_diameter, math.sqrt(max(open_area, 1))))), 2)}
    elif pred_type == 'recharge_shaft':
        shaft_depth = model_dimension_estimates.get('shaft_depth_m', min(depth, 6.0) if depth else 3.0)
        dimensions = {'shaft_depth_m': round(min(8.0, max(2.0, shaft_depth)), 2), 'shaft_diameter_m': round(min(1.5, max(0.8, model_dimension_estimates.get('shaft_diameter_m', 1.0))), 2)}
    elif pred_type == 'recharge_well_or_injection':
        inflow = _estimate_design_inflow_lps(roof_area, enriched['roof_type'])
        well_depth = model_dimension_estimates.get('well_depth_m', min(depth + 1.0, 15.0) if depth else 8.0)
        capacity = min(inflow, model_dimension_estimates.get('injection_capacity_lps', inflow))
        dimensions = {'well_depth_m': round(min(15.0, max(6.0, well_depth)), 2), 'well_diameter_m': round(min(0.3, max(0.2, model_dimension_estimates.get('well_diameter_m', 0.25))), 2), 'injection_capacity_lps': round(max(0.2, min(2.0, capacity)), 2)}
    elif pred_type == 'community_recharge_or_combination':
        dimensions = {'comm_structure_depth_m': round(min(6.0, max(3.0, model_dimension_estimates.get('comm_structure_depth_m', 4.0))), 2), 'comm_structure_diameter_m': round(min(5.0, max(3.0, model_dimension_estimates.get('comm_structure_diameter_m', math.sqrt(max(open_area, 9))))), 2)}
    else:
        dimensions = {'comm_structure_depth_m': 4.0, 'comm_structure_diameter_m': round(min(5.0, max(3.0, math.sqrt(max(open_area, 9)))), 2)}

    # Explanation
    explanation = rule_assess.get('reason') or ''
    if pred_type != pred_type_raw:
        explanation += (" " if explanation else "") + f"The trained classifier suggested '{pred_type_raw}', while water-balance and site constraints selected '{pred_type}'."

    # Cost estimate context from geology
    lith = rec.get('lithology_type', '')
    soil = rec.get('soil_type', '')
    cost_context = {
        'hard_rock': _is_hardrock(lith),
        'soil_is_rocky': _is_hardrock(lith),
        'prefer_plastic_tank': False
    }
    cost_estimate = estimate_cost(pred_type, dimensions, cost_context)

    result = {
        "predicted_structure": pred_type,
        "predicted_dimensions": dimensions,
        "nearest_well_record": rec.to_dict(),
        "explanation": explanation,
        "cost_estimate": cost_estimate,
        "water_balance": {
            "rainfall_mm": round(rainfall, 2),
            "runoff_coefficient": runoff,
            "annual_harvest_l": round(annual_harvest, 2),
            "demand_l": round(demand, 2),
            "storage_feasible": bool(rule_assess['feasible_for_storage'])
        },
        "model_diagnostics": {
            "classifier_suggestion": pred_type_raw,
            "classifier_confidence": model_confidence,
            "dimension_model_estimates": model_dimension_estimates
        }
    }

    # Include rooftop detection data if available
    if rooftop_detection_data is not None:
        result["rooftop_detection"] = rooftop_detection_data

    return result

if __name__ == "__main__":
    print("=== Rooftop Rainwater Harvesting Predictor (Bengaluru) ===")

    user_input = {}
    user_input['lat'] = float(input("Enter location latitude: "))
    user_input['lon'] = float(input("Enter location longitude: "))
    user_input['rooftop_area_m2'] = float(input("Enter rooftop area (m²): "))
    user_input['open_area_m2'] = float(input("Enter open ground area (m²): "))
    user_input['roof_type'] = input("Enter roof type (concrete/tiled/gi/asbestos): ").lower()
    user_input['num_persons'] = int(input("Enter number of persons in household: "))

    # Optional softer defaults
    try:
        pc_in = input("Enter per-capita demand lpcd [default 35]: ").strip()
        if pc_in:
            user_input['per_capita'] = float(pc_in)
    except Exception:
        pass
    try:
        pd_in = input("Enter design period (days) [default 90]: ").strip()
        if pd_in:
            user_input['period_days'] = int(pd_in)
    except Exception:
        pass

    result = predict_structure_and_dimensions(user_input, db)

    print("\n=== Prediction Result ===")
    print("Recommended Structure:", result["predicted_structure"])
    print("Suggested Dimensions:")
    for k,v in result["predicted_dimensions"].items():
        try:
            print(f"  - {k}: {round(float(v),2)}")
        except Exception:
            print(f"  - {k}: {v}")

    if result.get("explanation"):
        print("\nReason:")
        print(" ", result["explanation"])

    # Print cost estimate
    if result.get("cost_estimate"):
        ce = result["cost_estimate"]
        print("\nEstimated Cost (Bengaluru): Rs", ce.get("total_cost_inr"))
        print("Breakdown:")
        for item in ce.get("breakdown", []):
            print(f"  - {item['item']}: Rs {item['cost_inr']}")

    print("\nNearest Well Record Used:")
    for k,v in result["nearest_well_record"].items():
        print(f"  {k}: {v}")
