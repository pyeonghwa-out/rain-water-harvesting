import math
from typing import Dict, Any, List, Optional

UNIT_RATES_INR = {
	# Tanks
	"rcc_tank_cost_per_litre": 1.2,                # Rs per litre for small RCC/ferrocement tanks (fabrication, fittings)
	"plastic_tank_cost_per_litre": 0.7,            # if opting for HDPE/LLDPE tank instead of RCC
	"tank_civil_platform_lump_sum": 12000,         # basic platform/stands, plumbing allowances

	# Excavation and backfill
	"manual_excavation_per_m3": 450,               # excavation in soil (Rs/m3)
	"rock_excavation_per_m3": 1200,                # if hard rock encountered (Rs/m3)
	"backfill_gravel_per_m3": 1800,                # graded gravel supply & fill (Rs/m3)
	"filter_sand_per_m3": 1400,                    # river sand for filter layers (Rs/m3)

	# Drilling / shafts / wells
	"drilling_soft_rock_per_m": 1200,              # Rs per metre (down to ~100–150 mm dia)
	"drilling_hard_rock_per_m": 1800,              # hard rock rates (Rs/m)
	"casing_uPVC_per_m": 900,                      # uPVC casing/screen 160–200 mm (Rs/m)
	"gravel_pack_per_m": 300,                      # pea gravel pack per metre annulus (approx)
	"well_headworks_lump_sum": 25000,              # headworks: chamber, cap, valve, apron

	# Civil works
	"brick_lining_per_m2": 950,                    # lining of pits/shafts (Rs/m2)
	"rcc_cover_slab_per_m2": 1800,                 # cover slabs (Rs/m2)
	"silt_trap_chamber_lump_sum": 6000,            # silt trap/settling chamber

	# Plumbing / fittings
	"pvc_pipes_and_fittings_lump_sum": 8000,       # downpipes, first-flush, screens, valves
	"first_flush_assembly": 4000,
	"leaf_guard_and_screen": 3000,
}

DEFAULTS = {
	"pit_depth_m": 2.5,
	"pit_diameter_m": 2.0,
	"shaft_depth_m": 4.0,
	"shaft_diameter_m": 1.0,
	"well_depth_m": 10.0,
	"well_diameter_m": 0.25,
}

def _circle_volume_m3(diameter_m: float, depth_m: float) -> float:
	radius = max(0.0, diameter_m) / 2.0
	return math.pi * radius * radius * max(0.0, depth_m)

def _cylindrical_surface_area_m2(diameter_m: float, height_m: float) -> float:
	# Lateral surface area (no base/cover)
	radius = max(0.0, diameter_m) / 2.0
	return 2 * math.pi * radius * max(0.0, height_m)


def _round_currency(x: float) -> int:
	return int(round(max(0.0, x)))


def estimate_tank_cost(dimensions: Dict[str, Any], prefer_plastic: bool = False) -> Dict[str, Any]:
	V_l = float(dimensions.get("tank_volume_l", 3000))
	height_m = float(dimensions.get("tank_height_m", 1.4))
	diameter_m = float(dimensions.get("tank_diameter_m", 1.6))

	if prefer_plastic:
		material_cost = V_l * UNIT_RATES_INR["plastic_tank_cost_per_litre"]
		material_note = "HDPE/LLDPE tank"
	else:
		material_cost = V_l * UNIT_RATES_INR["rcc_tank_cost_per_litre"]
		material_note = "RCC/ferrocement tank"

	platform = UNIT_RATES_INR["tank_civil_platform_lump_sum"]
	plumbing = UNIT_RATES_INR["pvc_pipes_and_fittings_lump_sum"] + UNIT_RATES_INR["first_flush_assembly"] + UNIT_RATES_INR["leaf_guard_and_screen"]

	total = material_cost + platform + plumbing
	return {
		"structure": "store_on_roof",
		"dimensions_used": {"tank_volume_l": V_l, "tank_height_m": height_m, "tank_diameter_m": diameter_m},
		"total_cost_inr": _round_currency(total),
		"breakdown": [
			{"item": material_note, "qty": f"{int(V_l)} L", "rate": f"Rs/L", "cost_inr": _round_currency(material_cost)},
			{"item": "Platform/stand and basic civil", "qty": 1, "rate": "lump sum", "cost_inr": _round_currency(platform)},
			{"item": "Downpipes + first flush + screens", "qty": 1, "rate": "lump sum", "cost_inr": _round_currency(plumbing)},
		],
		"assumptions": [
			"Retail supply and small works rates, Bengaluru 2024–25.",
			"Includes basic plumbing components; excludes long distribution lines and booster pumps.",
		]
	}


def estimate_pit_cost(dimensions: Dict[str, Any], soil_is_rocky: bool = False) -> Dict[str, Any]:
	depth_m = float(dimensions.get("pit_depth_m", DEFAULTS["pit_depth_m"]))
	diameter_m = float(dimensions.get("pit_diameter_m", DEFAULTS["pit_diameter_m"]))

	vol_m3 = _circle_volume_m3(diameter_m, depth_m)
	exc_rate = UNIT_RATES_INR["rock_excavation_per_m3"] if soil_is_rocky else UNIT_RATES_INR["manual_excavation_per_m3"]
	exc_cost = vol_m3 * exc_rate

	# Assume 60% gravel backfill volume, 10% sand filter
	gravel_m3 = vol_m3 * 0.6
	sand_m3 = vol_m3 * 0.1
	gravel_cost = gravel_m3 * UNIT_RATES_INR["backfill_gravel_per_m3"]
	sand_cost = sand_m3 * UNIT_RATES_INR["filter_sand_per_m3"]

	# Simple lining/cover slab allowances
	lateral_area_m2 = _cylindrical_surface_area_m2(diameter_m, depth_m)
	lining_cost = lateral_area_m2 * UNIT_RATES_INR["brick_lining_per_m2"]
	cover_slab_m2 = (math.pi * (diameter_m/2) ** 2)
	cover_cost = cover_slab_m2 * UNIT_RATES_INR["rcc_cover_slab_per_m2"]

	silt_trap = UNIT_RATES_INR["silt_trap_chamber_lump_sum"]
	plumbing = UNIT_RATES_INR["pvc_pipes_and_fittings_lump_sum"]

	total = exc_cost + gravel_cost + sand_cost + lining_cost + cover_cost + silt_trap + plumbing
	return {
		"structure": "recharge_on_site_pit",
		"dimensions_used": {"pit_depth_m": depth_m, "pit_diameter_m": diameter_m},
		"total_cost_inr": _round_currency(total),
		"breakdown": [
			{"item": "Excavation", "qty": round(vol_m3,2), "rate": f"Rs/m3 ({'rock' if soil_is_rocky else 'soil'})", "cost_inr": _round_currency(exc_cost)},
			{"item": "Gravel backfill (60%)", "qty": round(gravel_m3,2), "rate": "Rs/m3", "cost_inr": _round_currency(gravel_cost)},
			{"item": "Filter sand (10%)", "qty": round(sand_m3,2), "rate": "Rs/m3", "cost_inr": _round_currency(sand_cost)},
			{"item": "Lining (optional)", "qty": round(lateral_area_m2,2), "rate": "Rs/m2", "cost_inr": _round_currency(lining_cost)},
			{"item": "RCC cover slab", "qty": round(cover_slab_m2,2), "rate": "Rs/m2", "cost_inr": _round_currency(cover_cost)},
			{"item": "Silt trap chamber", "qty": 1, "rate": "lump sum", "cost_inr": _round_currency(silt_trap)},
			{"item": "Plumbing/fittings", "qty": 1, "rate": "lump sum", "cost_inr": _round_currency(plumbing)},
		],
		"assumptions": [
			"Pit with gravel-sand filter; lining used where side stability needed.",
			"Rates typical for Bengaluru small works; exclude dewatering if water table shallow.",
		]
	}


def estimate_shaft_cost(dimensions: Dict[str, Any], hard_rock: bool = True) -> Dict[str, Any]:
	depth_m = float(dimensions.get("shaft_depth_m", DEFAULTS["shaft_depth_m"]))
	diameter_m = float(dimensions.get("shaft_diameter_m", DEFAULTS["shaft_diameter_m"]))

	# Treat as drilled/excavated vertical shaft with lining and cover
	vol_m3 = _circle_volume_m3(diameter_m, depth_m)
	exc_rate = UNIT_RATES_INR["rock_excavation_per_m3"] if hard_rock else UNIT_RATES_INR["manual_excavation_per_m3"]
	exc_cost = vol_m3 * exc_rate

	lateral_area_m2 = _cylindrical_surface_area_m2(diameter_m, depth_m)
	lining_cost = lateral_area_m2 * UNIT_RATES_INR["brick_lining_per_m2"]
	cover_slab_m2 = (math.pi * (diameter_m/2) ** 2)
	cover_cost = cover_slab_m2 * UNIT_RATES_INR["rcc_cover_slab_per_m2"]
	gravel_cost = vol_m3 * 0.2 * UNIT_RATES_INR["backfill_gravel_per_m3"]   # pea gravel around lateral perforations
	plumbing = UNIT_RATES_INR["pvc_pipes_and_fittings_lump_sum"]

	total = exc_cost + lining_cost + cover_cost + gravel_cost + plumbing
	return {
		"structure": "recharge_shaft",
		"dimensions_used": {"shaft_depth_m": depth_m, "shaft_diameter_m": diameter_m},
		"total_cost_inr": _round_currency(total),
		"breakdown": [
			{"item": "Shaft excavation/drilling", "qty": round(vol_m3,2), "rate": f"Rs/m3 ({'hard rock' if hard_rock else 'soil'})", "cost_inr": _round_currency(exc_cost)},
			{"item": "Lining (brick/RCC rings)", "qty": round(lateral_area_m2,2), "rate": "Rs/m2", "cost_inr": _round_currency(lining_cost)},
			{"item": "RCC cover slab", "qty": round(cover_slab_m2,2), "rate": "Rs/m2", "cost_inr": _round_currency(cover_cost)},
			{"item": "Gravel pack/local filter", "qty": round(vol_m3*0.2,2), "rate": "Rs/m3", "cost_inr": _round_currency(gravel_cost)},
			{"item": "Plumbing/fittings", "qty": 1, "rate": "lump sum", "cost_inr": _round_currency(plumbing)},
		],
		"assumptions": [
			"Compact footprint shaft for hard-rock Bengaluru settings.",
			"Includes lining and cover; excludes dewatering and traffic diversion costs.",
		]
	}


def estimate_injection_well_cost(dimensions: Dict[str, Any], hard_rock: bool = True) -> Dict[str, Any]:
	depth_m = float(dimensions.get("well_depth_m", DEFAULTS["well_depth_m"]))
	diameter_m = float(dimensions.get("well_diameter_m", DEFAULTS["well_diameter_m"]))
	inj_lps = float(dimensions.get("injection_capacity_lps", 0.5))

	# Convert diameter to drilling/casing category (assume 200–250 mm typical)
	drill_rate = UNIT_RATES_INR["drilling_hard_rock_per_m"] if hard_rock else UNIT_RATES_INR["drilling_soft_rock_per_m"]
	drilling = depth_m * drill_rate
	casing = depth_m * UNIT_RATES_INR["casing_uPVC_per_m"]
	gravel_pack = depth_m * UNIT_RATES_INR["gravel_pack_per_m"]
	headworks = UNIT_RATES_INR["well_headworks_lump_sum"]
	plumbing = UNIT_RATES_INR["pvc_pipes_and_fittings_lump_sum"]

	# Development/cleaning allowance proportional to capacity
	development = max(15000.0, inj_lps * 8000.0)

	total = drilling + casing + gravel_pack + headworks + plumbing + development
	return {
		"structure": "recharge_well_or_injection",
		"dimensions_used": {"well_depth_m": depth_m, "well_diameter_m": diameter_m, "injection_capacity_lps": inj_lps},
		"total_cost_inr": _round_currency(total),
		"breakdown": [
			{"item": "Drilling", "qty": round(depth_m,1), "rate": f"Rs/m ({'hard rock' if hard_rock else 'soft'} rock)", "cost_inr": _round_currency(drilling)},
			{"item": "uPVC casing & screen", "qty": round(depth_m,1), "rate": "Rs/m", "cost_inr": _round_currency(casing)},
			{"item": "Gravel pack", "qty": round(depth_m,1), "rate": "Rs/m", "cost_inr": _round_currency(gravel_pack)},
			{"item": "Headworks (chamber, apron, valves)", "qty": 1, "rate": "lump sum", "cost_inr": _round_currency(headworks)},
			{"item": "Plumbing/fittings", "qty": 1, "rate": "lump sum", "cost_inr": _round_currency(plumbing)},
			{"item": "Well development & cleaning", "qty": 1, "rate": "capacity-based", "cost_inr": _round_currency(development)},
		],
		"assumptions": [
			"Rates suit 200–250 mm injection wells typical in Bengaluru hard rock.",
			"Excludes power supply/pumps; assumes reasonable site access.",
		]
	}


def estimate_community_cost(dimensions: Dict[str, Any]) -> Dict[str, Any]:
	depth_m = float(dimensions.get("comm_structure_depth_m", 4.0))
	diameter_m = float(dimensions.get("comm_structure_diameter_m", 4.0))

	vol_m3 = _circle_volume_m3(diameter_m, depth_m)
	exc_cost = vol_m3 * UNIT_RATES_INR["manual_excavation_per_m3"]
	gravel_cost = vol_m3 * 0.5 * UNIT_RATES_INR["backfill_gravel_per_m3"]
	sand_cost = vol_m3 * 0.1 * UNIT_RATES_INR["filter_sand_per_m3"]
	lateral_area_m2 = _cylindrical_surface_area_m2(diameter_m, depth_m)
	lining_cost = lateral_area_m2 * UNIT_RATES_INR["brick_lining_per_m2"]
	cover_cost = (math.pi * (diameter_m/2) ** 2) * UNIT_RATES_INR["rcc_cover_slab_per_m2"]
	chambers = UNIT_RATES_INR["silt_trap_chamber_lump_sum"] * 2

	total = exc_cost + gravel_cost + sand_cost + lining_cost + cover_cost + chambers
	return {
		"structure": "community_recharge_or_combination",
		"dimensions_used": {"comm_structure_depth_m": depth_m, "comm_structure_diameter_m": diameter_m},
		"total_cost_inr": _round_currency(total),
		"breakdown": [
			{"item": "Excavation", "qty": round(vol_m3,2), "rate": "Rs/m3", "cost_inr": _round_currency(exc_cost)},
			{"item": "Gravel backfill (50%)", "qty": round(vol_m3*0.5,2), "rate": "Rs/m3", "cost_inr": _round_currency(gravel_cost)},
			{"item": "Filter sand (10%)", "qty": round(vol_m3*0.1,2), "rate": "Rs/m3", "cost_inr": _round_currency(sand_cost)},
			{"item": "Lining", "qty": round(lateral_area_m2,2), "rate": "Rs/m2", "cost_inr": _round_currency(lining_cost)},
			{"item": "RCC cover slab", "qty": round(math.pi*(diameter_m/2)**2,2), "rate": "Rs/m2", "cost_inr": _round_currency(cover_cost)},
			{"item": "Inlet/outlet chambers", "qty": 2, "rate": "lump sum", "cost_inr": _round_currency(chambers)},
		],
		"assumptions": [
			"Community-scale pit/pond style structure; excludes land and approvals.",
		]
	}


STRUCTURE_COST_DISPATCH = {
	"store_on_roof": estimate_tank_cost,
	"recharge_on_site_pit": estimate_pit_cost,
	"recharge_shaft": estimate_shaft_cost,
	"recharge_well_or_injection": estimate_injection_well_cost,
	"community_recharge_or_combination": estimate_community_cost,
}


def estimate_cost(structure: str, dimensions: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
	"""
	Return a Bengaluru-relative INR cost estimate and breakdown for a predicted structure.

	Parameters:
	- structure: predicted structure key
	- dimensions: dict of predicted dimensions for that structure
	- context: optional dict with hints, e.g., {"soil_is_rocky": bool, "hard_rock": bool, "prefer_plastic_tank": bool}
	"""
	context = context or {}
	key = (structure or "").strip()
	fn = STRUCTURE_COST_DISPATCH.get(key)
	if fn is None:
		return {
			"structure": key,
			"dimensions_used": dimensions,
			"total_cost_inr": 0,
			"breakdown": [],
			"assumptions": ["Unknown structure type; no cost model available."],
		}

	if key == "store_on_roof":
		return fn(dimensions, prefer_plastic=bool(context.get("prefer_plastic_tank", False)))
	if key == "recharge_on_site_pit":
		return fn(dimensions, soil_is_rocky=bool(context.get("soil_is_rocky", False)))
	if key in ("recharge_shaft", "recharge_well_or_injection"):
		return fn(dimensions, hard_rock=bool(context.get("hard_rock", True)))
	return fn(dimensions)


if __name__ == "__main__":
	# Simple manual test
	samples = [
		("store_on_roof", {"tank_volume_l": 3000, "tank_height_m": 1.4, "tank_diameter_m": 1.6}, {"prefer_plastic_tank": False}),
		("recharge_on_site_pit", {"pit_depth_m": 2.5, "pit_diameter_m": 2.0}, {}),
		("recharge_shaft", {"shaft_depth_m": 6.0, "shaft_diameter_m": 1.0}, {"hard_rock": True}),
		("recharge_well_or_injection", {"well_depth_m": 12.0, "well_diameter_m": 0.25, "injection_capacity_lps": 0.8}, {"hard_rock": True}),
	]
	for s, d, ctx in samples:
		res = estimate_cost(s, d, ctx)
		print("\n===", s, "===")
		print("Total (INR):", res["total_cost_inr"])
		for it in res["breakdown"]:
			print(" -", it["item"], ":", it["cost_inr"])
