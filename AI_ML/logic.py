import math
import os
import numpy as np
import pandas as pd
import random

def _estimate_design_inflow_lps(rooftop_area_m2: float, roof_type: str) -> float:
	coeff_map = {'gi':0.9, 'asbestos':0.8, 'tiled':0.75, 'concrete':0.7}
	rc = coeff_map.get(str(roof_type).lower(), 0.7)
	return max(0.0, rooftop_area_m2 * rc * (0.05 * 1000.0 / 3600.0))

def _is_permeable(soil: str, lith: str) -> bool:
	s = (soil or '').lower(); l = (lith or '').lower()
	permeable_keywords = ['sand','sandy','gravel','alluv','alluvial']
	return any(k in s for k in permeable_keywords) or any(k in l for k in permeable_keywords)

def _is_hardrock(lith: str) -> bool:
	l = (lith or '').lower()
	hardrock_keywords = ['basalt','granite','gneiss','hard rock','rock','fracture']
	return any(k in l for k in hardrock_keywords)

def haversine_km(lat1, lon1, lat2, lon2):
	R = 6371.0
	phi1 = math.radians(lat1); phi2 = math.radians(lat2)
	dphi = math.radians(lat2 - lat1); dlambda = math.radians(lon2 - lon1)
	a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
	return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

_RUNOFF_COEFF = {'gi':0.9, 'asbestos':0.8, 'tiled':0.75, 'concrete':0.7}

def _pick_nearest_record(db, lat, lon, max_km=50):
	if db is None or len(db)==0:
		return None
	dists = db.apply(lambda r: haversine_km(lat, lon, r['lat'], r['long']), axis=1)
	idx = dists.idxmin()
	if dists.loc[idx] > max_km:
		rec = db.loc[idx].copy()
		rec['_distance_km'] = dists.loc[idx]
		return rec
	rec = db.loc[idx].copy()
	rec['_distance_km'] = dists.loc[idx]
	return rec

def compute_tank_dimensions(volume_liters, preferred_height_m = None):
	V_m3 = volume_liters / 1000.0
	if preferred_height_m is None:
		h = 1.4
	else:
		h = preferred_height_m
	r = math.sqrt(V_m3 / (math.pi * h))
	diameter = 2 * r
	return {'volume_liters': volume_liters, 'height_m': h, 'diameter_m': round(diameter,3)}

def assess_rwh(db, rooftop_area, lat, lon, open_area=None,
		       roof_type='concrete', num_persons=4, per_capita=6, period_days=120,
		       preferred_tank_height_m=None):

	rec = _pick_nearest_record(db, lat, lon)
	if rec is None:
		raise ValueError("Local DB empty or missing location columns")
	rainfall_mm = float(rec.get('mean_annual_rainfall', np.nan) if not pd.isna(rec.get('mean_annual_rainfall', np.nan)) else 900.0)
	rc = _RUNOFF_COEFF.get(roof_type.lower(), 0.7)

	water_available_l = (rainfall_mm/1000.0) * rooftop_area * rc * 1000.0
	demand_l = num_persons * per_capita * period_days

	feasible_for_storage = water_available_l >= demand_l

	soil = str(rec.get('soil_type', '')).lower()
	lith = str(rec.get('lithology_type', '')).lower()
	aquifer = str(rec.get('aquifer_tapped', '')).lower()
	depth_mbgl = rec.get('depth_mbgl', None)

	rainfall_adequate = rainfall_mm >= 1000.0
	design_inflow_lps = _estimate_design_inflow_lps(rooftop_area, roof_type)
	small_roof = rooftop_area < 80.0
	reason = None

	recommended_action = None
	structure = None
	dimensions = {}

	if feasible_for_storage:
		recommended_action = 'store_on_roof'
		tank = compute_tank_dimensions(volume_liters = demand_l, preferred_height_m = preferred_tank_height_m)
		structure = 'subsurface storage tank (masonry/ferrocement/RCC as applicable)'
		dimensions = {'tank': tank}
		reason = f"Rooftop storage feasible: annual harvest {round(water_available_l)} L >= demand {round(demand_l)} L."
	else:
		open_area_m2 = open_area if open_area is not None else 0.0

		soil_is_permeable = _is_permeable(soil, lith)
		hardrock = _is_hardrock(lith)

		if soil_is_permeable and open_area_m2 >= 4.0:
			recommended_action = 'recharge_on_site_pit'
			# pit sizing heuristics
			suggested_diameter = round(min(max(1.0, math.sqrt(open_area_m2)), 3.0),3) if open_area_m2>0 else 2.0
			suggested_depth_m = 2.5 if not depth_mbgl else min(3.5, max(1.5, (depth_mbgl - 0.5) if depth_mbgl>1.0 else 2.5))
			structure = 'percolation / recharge pit with gravel/sand filter at bottom'
			dimensions = {'pit_diameter_m': suggested_diameter,
					  'pit_depth_m': round(suggested_depth_m,3)}
			reason = "Permeable soils and adequate open area: on-site recharge pit preferred over deep structures."
		elif hardrock:
			# Hard rock handling with inflow/area guardrail before injection
			if depth_mbgl and depth_mbgl > 10:
				if small_roof or design_inflow_lps < 0.5:
					recommended_action = 'recharge_shaft'
					structure = 'recharge shaft (small footprint) to intersect fractures'
					dimensions = {'shaft_diameter_m': 1.0,
							  'shaft_depth_m': round(max(2.0, min(6.0, depth_mbgl)),3)}
					reason = f"Hard rock with deep water level (~{depth_mbgl} m), but small roof/inflow (design {round(design_inflow_lps,2)} l/s): prefer recharge shaft over injection well."
				else:
					recommended_action = 'recharge_well_or_injection'
					structure = 'injection / recharge well (sealed annulus, screen at target fractures)'
					dimensions = {'recommended_injection_rate_lps_example': max(0.5, min(2.0, design_inflow_lps))}
					reason = f"Hard rock with deeper water level (~{depth_mbgl} m) and sufficient inflow: injection well is suitable."
			else:
				recommended_action = 'recharge_shaft'
				structure = 'recharge shaft (drilled/excavated to reach fractured zone)'
				dimensions = {'shaft_diameter_m': 1.0, 'shaft_depth_m': round(max(2.0, depth_mbgl if depth_mbgl else 3.0),3)}
				reason = "Hard rock with shallower water table: recharge shaft is adequate; injection not necessary."
		else:
			if rainfall_adequate and open_area_m2 < 4.0:
				recommended_action = 'recharge_shaft_or_community'
				structure = 'small recharge shaft or connect to nearest public recharge structure'
				dimensions = {'shaft_diameter_m':1.0, 'shaft_depth_m':2.0}
				reason = "Limited space; prefer compact shaft or community recharge connection."
			else:
				recommended_action = 'community_recharge_or_combination'
				structure = 'connect to community percolation structures / combined pit+shaft system'
				dimensions = {}
				reason = "Site constraints; suggest community/combination approach to increase recharge."

	numbers = {
		'rainfall_mm': round(rainfall_mm,2),
		'runoff_coeff': rc,
		'water_available_l_per_year': round(water_available_l,2),
		'household_demand_l_for_period': round(demand_l,2),
		'feasible_for_storage': feasible_for_storage,
		'nearest_record_distance_km': round(float(rec.get('_distance_km', 0.0)),3),
		'soil_type': rec.get('soil_type', None),
		'lithology_type': rec.get('lithology_type', None),
		'aquifer_tapped': rec.get('aquifer_tapped', None),
		'depth_mbgl': rec.get('depth_mbgl', None),
		'rainfall_adequate_flag': rainfall_adequate,
		'design_inflow_lps': round(design_inflow_lps,3)
	}

	return {
		'feasible_for_storage': feasible_for_storage,
		'recommended_action': recommended_action,
		'structure': structure,
		'dimensions': dimensions,
		'numbers': numbers,
		'reason': reason,
		'used_site_record': rec.to_dict() if isinstance(rec, pd.Series) else rec
	}

def generate_structure_dimensions(action, demand_l, open_area, depth_mbgl=None):
	if action == "store_on_roof":
		h = 1.4
		V_m3 = demand_l / 1000
		r = np.sqrt(V_m3 / (np.pi * h))
		diameter = 2*r + np.random.uniform(-0.2,0.2)
		return {"tank_height_m": round(h,2), "tank_diameter_m": round(diameter,2),
				"tank_volume_l": round(demand_l)}

	elif action == "recharge_on_site_pit":
		depth = min(3.5, (depth_mbgl-0.5) if depth_mbgl else 2.5)
		depth += np.random.uniform(-0.2,0.2)
		diameter = min(3, max(1, np.sqrt(max(1e-6, open_area)))) + np.random.uniform(-0.1,0.1)
		return {"pit_depth_m": round(depth,2), "pit_diameter_m": round(diameter,2),
				"side_slope": "2:1"}

	elif action == "recharge_shaft":
		depth = min(8, depth_mbgl if depth_mbgl else 6) + np.random.uniform(-0.5,0.5)
		diameter = np.random.uniform(0.9,1.2)
		return {"shaft_depth_m": round(depth,2), "shaft_diameter_m": round(diameter,2)}

	elif action == "recharge_well_or_injection":
		assumed_area = 80.0
		assumed_rc = 0.7
		design_inflow = assumed_area * assumed_rc * (0.05 * 1000.0 / 3600.0)
		depth = (depth_mbgl if depth_mbgl else 12)
		depth = max(6.0, min(15.0, depth + np.random.uniform(-1.0,1.0)))
		diameter = np.random.uniform(0.22,0.28)
		inj_rate = max(0.2, min(2.0, design_inflow + np.random.uniform(-0.2,0.2)))
		return {"well_depth_m": round(depth,2), "well_diameter_m": round(diameter,2),
				"injection_capacity_lps": round(inj_rate,2)}

	elif action in ["community_recharge_or_combination","recharge_shaft_or_community"]:
		depth = np.random.uniform(3,6)
		diameter = np.random.uniform(3,5)
		return {"comm_structure_depth_m": round(depth,2), "comm_structure_diameter_m": round(diameter,2)}

	else:
		return {}


def generate_synthetic_dataset(db, n_samples=1000, seed=42,
								lat_range=(12.7,13.2), lon_range=(77.3,77.9),
								rooftop_range=(20,200), open_area_range=(0,100)):

	random.seed(seed)
	np.random.seed(seed)

	roof_types = ['concrete','tiled','gi','asbestos']
	data = []

	for i in range(n_samples):
		rooftop_area = np.random.uniform(*rooftop_range)
		open_area = np.random.uniform(*open_area_range)
		roof_type = random.choice(roof_types)

		num_persons = np.random.randint(2, 20)
		per_capita = np.random.choice([6, 25, 70, 100])
		period_days = np.random.randint(90, 366)

		lat = np.random.uniform(*lat_range)
		lon = np.random.uniform(*lon_range)
		rec = _pick_nearest_record(db, lat, lon)
		if rec is None:
			continue

		base_rainfall = float(rec.get('mean_annual_rainfall', 900.0))
		rainfall_mm = base_rainfall * np.random.uniform(0.6, 1.4)
		rec['mean_annual_rainfall'] = rainfall_mm

		try:
			result = assess_rwh(db=db,
								rooftop_area=rooftop_area,
								lat=lat, lon=lon,
								open_area=open_area,
								roof_type=roof_type,
								num_persons=num_persons,
								per_capita=per_capita,
								period_days=period_days)

			row = {
				'lat': lat, 'lon': lon,
				'rooftop_area_m2': rooftop_area,
				'open_area_m2': open_area,
				'roof_type': roof_type,
				'num_persons': num_persons,
				'per_capita': per_capita,
				'period_days': period_days,
				'rainfall_mm': result['numbers']['rainfall_mm'],
				'soil_type': result['numbers']['soil_type'],
				'lithology_type': result['numbers']['lithology_type'],
				'aquifer_tapped': result['numbers']['aquifer_tapped'],
				'depth_mbgl': result['numbers']['depth_mbgl'],

				# labels
				'feasible_for_storage': result['feasible_for_storage'],
				'recommended_action': result['recommended_action'],
				'structure': result['structure']
			}
			data.append(row)
			dims = generate_structure_dimensions(result['recommended_action'],
										 demand_l=result['numbers']['household_demand_l_for_period'],
										 open_area=open_area,
										 depth_mbgl=result['numbers']['depth_mbgl'])
			row.update(dims)

		except Exception:
			continue

	df = pd.DataFrame(data)

	if 'recommended_action' in df.columns:
		counts = df['recommended_action'].value_counts()
		max_count = counts.max()
		balanced = []
		for label, group in df.groupby('recommended_action'):
			balanced.append(group.sample(max_count, replace=True, random_state=seed))
		df = pd.concat(balanced).reset_index(drop=True)

	return df

if __name__ == "__main__":
	# Generate synthetic dataset only when executed directly, not on import
	base_dir = os.path.dirname(__file__) if '__file__' in globals() else "."
	db = pd.read_csv(os.path.join(base_dir, "data/processed/wells_with_rainfall.csv"))
	synthetic_df = generate_synthetic_dataset(db, n_samples=900)
	synthetic_df.to_csv(os.path.join(base_dir, "data/processed/synthetic_dataset.csv"), index=False)
