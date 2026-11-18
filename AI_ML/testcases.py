import pandas as pd
from predict import predict_structure_and_dimensions, db
from estimate_cost import estimate_cost

# Bengaluru prototype test cases
# Each case includes: lat, lon, rooftop_area_m2, open_area_m2, roof_type, num_persons, per_capita, period_days
# For each scenario, comments describe the practical advice to cross-check model outputs.

TEST_CASES = [
	{
		# Case 1: Small roof in hard rock area, limited open space.
		# Practical advice: Avoid deep injection well; prefer recharge shaft (2–6 m) or small tank.
		"name": "Small roof, hard rock, tiny plot",
		"input": {
			"lat": 12.97, "lon": 77.59,
			"rooftop_area_m2": 50.0,
			"open_area_m2": 2.0,
			"roof_type": "concrete",
			"num_persons": 4,
			"per_capita": 35,
			"period_days": 90
		}
	},
	{
		# Case 2: Medium roof, permeable soils, adequate open area.
		# Practical advice: Prefer on-site percolation pit (2–3 m depth, 1.5–3 m diameter).
		"name": "Medium roof, permeable soil, open plot",
		"input": {
			"lat": 13.02, "lon": 77.70,
			"rooftop_area_m2": 120.0,
			"open_area_m2": 30.0,
			"roof_type": "tiled",
			"num_persons": 6,
			"per_capita": 35,
			"period_days": 120
		}
	},
	{
		# Case 3: Large roof, urban demand; storage feasible.
		# Practical advice: Rooftop storage tank sized to demand; recharge optional as secondary.
		"name": "Large roof, storage feasible",
		"input": {
			"lat": 12.92, "lon": 77.58,
			"rooftop_area_m2": 200.0,
			"open_area_m2": 10.0,
			"roof_type": "gi",
			"num_persons": 5,
			"per_capita": 40,
			"period_days": 90
		}
	},
	{
		# Case 4: Small roof but high rainfall pocket; compact site.
		# Practical advice: If storage near-feasible, recommend small tank; otherwise compact shaft.
		"name": "Small roof, higher rainfall pocket",
		"input": {
			"lat": 13.10, "lon": 77.65,
			"rooftop_area_m2": 60.0,
			"open_area_m2": 3.0,
			"roof_type": "concrete",
			"num_persons": 3,
			"per_capita": 30,
			"period_days": 60
		}
	},
	{
		# Case 5: Hard rock, deeper water level, but very small roof; enough backyard.
		# Practical advice: Recharge shaft over injection; pit if soil shows permeability.
		"name": "Hard rock deep WL, small roof, some backyard",
		"input": {
			"lat": 12.85, "lon": 77.50,
			"rooftop_area_m2": 70.0,
			"open_area_m2": 15.0,
			"roof_type": "asbestos",
			"num_persons": 4,
			"per_capita": 35,
			"period_days": 90
		}
	},
	{
		# Case 6: Community-likely setting: tiny plots, adequate rainfall.
		# Practical advice: Recommend small shaft or community recharge connection.
		"name": "Tiny plots, consider community",
		"input": {
			"lat": 12.98, "lon": 77.62,
			"rooftop_area_m2": 40.0,
			"open_area_m2": 1.0,
			"roof_type": "concrete",
			"num_persons": 4,
			"per_capita": 35,
			"period_days": 90
		}
	},
	{
		# Case 7: Force non-storage in hard rock with small roof via high demand.
		# Practical advice: Recommend recharge shaft (compact) instead of injection due to small inflow.
		"name": "High demand, hard rock, small roof -> shaft",
		"input": {
			"lat": 12.97, "lon": 77.59,
			"rooftop_area_m2": 60.0,
			"open_area_m2": 6.0,
			"roof_type": "concrete",
			"num_persons": 12,
			"per_capita": 100,
			"period_days": 180
		}
	},
	{
		# Case 8: Hard rock, deeper WL expected; larger roof and very high demand to avoid storage.
		# Practical advice: Injection well acceptable if inflow is sufficient; else shaft.
		"name": "High demand, hard rock, large roof -> injection",
		"input": {
			"lat": 12.95, "lon": 77.55,
			"rooftop_area_m2": 180.0,
			"open_area_m2": 12.0,
			"roof_type": "concrete",
			"num_persons": 15,
			"per_capita": 100,
			"period_days": 200
		}
	},
	{
		# Case 9: Permeable soils with good open area, but storage made infeasible by very high demand.
		# Practical advice: On-site percolation pit should be suggested.
		"name": "Permeable soil, open area, non-storage -> pit",
		"input": {
			"lat": 13.12, "lon": 77.72,
			"rooftop_area_m2": 90.0,
			"open_area_m2": 40.0,
			"roof_type": "tiled",
			"num_persons": 12,
			"per_capita": 100,
			"period_days": 180
		}
	}
]

def run_tests():
	results = []
	for case in TEST_CASES:
		name = case["name"]
		user_input = case["input"].copy()
		try:
			res = predict_structure_and_dimensions(user_input, db)
			results.append((name, res))
		except Exception as e:
			results.append((name, {"error": str(e)}))

	# Pretty print
	for name, res in results:
		print("\n===", name, "===")
		if "error" in res:
			print("Error:", res["error"])
			continue
		print("Recommended:", res["predicted_structure"])
		print("Dimensions:")
		for k,v in res["predicted_dimensions"].items():
			try:
				print(f"  - {k}: {round(float(v),2)}")
			except Exception:
				print(f"  - {k}: {v}")
		if res.get("explanation"):
			print("Reason:", res["explanation"])
		# Cost estimate
		cost_ctx = {
			"hard_rock": str(res["nearest_well_record"].get("lithology_type", "")).lower().find("rock") != -1 or \
					  str(res["nearest_well_record"].get("lithology_type", "")).lower().find("gneiss") != -1,
			"soil_is_rocky": str(res["nearest_well_record"].get("lithology_type", "")).lower().find("rock") != -1,
			"prefer_plastic_tank": False
		}
		ce = estimate_cost(res["predicted_structure"], res["predicted_dimensions"], cost_ctx)
		print("Estimated Cost (Bengaluru): Rs", ce.get("total_cost_inr"))
		for item in ce.get("breakdown", [])[:4]:
			print(f"  - {item['item']}: Rs {item['cost_inr']}")
		print("Nearest well lithology/soil/depth:",
			  res["nearest_well_record"].get("lithology_type"),
			  res["nearest_well_record"].get("soil_type"),
			  res["nearest_well_record"].get("depth_mbgl"))

if __name__ == "__main__":
	print("Running tests...")
	run_tests()
