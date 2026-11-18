# 🌧️ Rooftop Rainwater Harvesting (RWH) Feasibility Predictor


uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload


## 📌 Overview
This project is a prototype built for the **Smart India Hackathon (SIH) 2025** problem statement on **Rainwater Harvesting (RWH)**.  
The aim is to develop a machine learning model that can:

1. Take **user input** (location, rooftop area, open ground area, roof type, household size).  
2. Combine this with **local hydrogeological data** (rainfall, soil, lithology, aquifer depth, etc.).  
3. Predict whether **rooftop rainwater harvesting is feasible**.  
4. If feasible, recommend the **type of structure** (e.g., rooftop storage tank, recharge well, pit, shaft, etc.).  
5. Suggest **design dimensions** of the chosen structure (tank diameter, pit depth, shaft size, etc.).  
6. Provide a **concise explanation** of why the recommendation was made.  
7. Return a **Bengaluru-relative cost estimate (INR)** for the structure.

---

## 📊 Dataset Sources
Since the project focuses on **Bengaluru prototype**, we restricted our data to **36 observation wells** in Bengaluru district. These were compiled from:

- **Central Ground Water Board (CGWB) reports**  
- **India-WRIS / CGWB Groundwater Data Portal**  
- **Bengaluru Urban and Rural hydrogeological reports**  
- Rainfall datasets from **IMD & Karnataka State Natural Disaster Monitoring Centre (KSNDMC)**  

👉 The file `data/processed/wells_with_rainfall.csv` contains these **36 well points** with:  
- Location (`lat`, `long`)  
- Rainfall (`mean_annual_rainfall`)  
- Soil type  
- Lithology type  
- Depth to water table (`depth_mbgl`)  
- Aquifer tapped  

This well DB serves as the **knowledge base** for enriching user input.

---

## 🎯 Why Bengaluru for Prototype?
- Bengaluru faces **acute water scarcity** despite receiving **~1100 mm annual rainfall**.  
- High dependence on **groundwater** + rapid urbanization makes RWH critical.  
- Availability of **reliable well monitoring data (36 sites)** makes Bengaluru a **practical starting point**.  
- Once validated, the approach can be **scaled to other cities/districts** with updated well datasets.

---

## 🧭 Project Structure (key files)
- `logic.py` — rule-based assessment, synthetic dataset generator, helper functions
- `build_dataset.py` — cleaning of raw well/rainfall inputs (Bengaluru-specific)
- `train_model.py` — trains classifier and dimension regressors on synthetic dataset
- `predict.py` — end-to-end prediction with guardrails, explanation, and cost estimate
- `estimate_cost.py` — Bengaluru-relative cost estimation per structure (INR)
- `testcases.py` — curated scenarios to verify practical recommendations
- `data/` — raw and processed datasets
- `models/` — trained model artifacts (`*.pkl`)
- `plots/` — training diagnostics (confusion matrix, feature importance, regressions)

---

## ⚙️ End-to-End Workflow (Step-by-step)

### 1) Data preparation
- Clean raw data to `data/processed/` (Bengaluru wells + rainfall, soils, lithology, depth).  
- The enriched well DB is used as a spatial knowledge base during generation and prediction.

### 2) Synthetic dataset generation (`logic.py`)
- Randomly sample Bengaluru lat/lon within bounds.  
- For each sample: pick the **nearest well** (Haversine distance) to inherit rainfall, soil, lithology, depth.  
- Draw household/demand settings: `num_persons`, `per_capita`, `period_days`.  
- Apply the **rulebook** (`assess_rwh`) to produce a label: structure type and indicative dimensions.  
- Balance classes across structure types to avoid bias.  
- Save to `data/processed/synthetic_dataset.csv`.

### 3) Model training (`train_model.py`)
- Features: `rooftop_area_m2`, `open_area_m2`, `roof_type`, `num_persons`, `per_capita`, `period_days`, `rainfall_mm`, `soil_type`, `lithology_type`, `depth_mbgl`.  
- Targets: `recommended_action` (classification) and structure-specific dimensions (regression).  
- Models:  
  - RandomForestClassifier for structure selection (with preprocessing: OneHotEncoder + StandardScaler).  
  - RandomForestRegressor per structure for dimensions.  
- Save models to `models/structure_classifier.pkl` and `models/dimension_regressors.pkl`.  
- Plots saved to `plots/`.

### 4) Prediction (`predict.py`)
- Inputs: `lat`, `lon`, `rooftop_area_m2`, `open_area_m2`, `roof_type`, `num_persons`, optional `per_capita` (default 35 lpcd), `period_days` (default 90).  
- Enrich with nearest-well hydrogeology.  
- Classifier predicts structure; regressor predicts dimensions.  
- Apply **guardrails** (post-processing):
  - Avoid injection wells for very small roofs or tiny open areas; prefer shafts or pits where appropriate.
  - Clamp impractical dimensions (e.g., injection capacity ≤ roof inflow; limit well depth and diameters; typical pit/shaft bounds).
- Generate **explanation** string:
  - Outputs reason from `assess_rwh` and notes any structure adjustment relative to the raw model output.
- Compute **cost estimate (INR)** using `estimate_cost.py` with geology-informed context (hard rock vs permeable).
- Output: structure, dimensions, explanation, cost estimate, and the nearest-well record used.

### 5) Validation (`testcases.py`)
- Contains Bengaluru scenarios with comments describing the practical advice expected.  
- Runs through the pipeline and prints: recommendation, dimensions, reasoning, and cost (INR).

---

## 📖 Rulebook (engineering logic distilled)
High-level rules used both in generation and for explanations:
- Compute annual harvest from rooftop: rainfall × area × runoff coefficient.  
- If harvest ≥ design demand → choose `store_on_roof` (size tank to demand).  
- Else consider recharge, informed by hydrogeology and site constraints:
  - **Permeable soils + adequate open area** → `recharge_on_site_pit` (2–3.5 m depth, 1–3 m dia).
  - **Hard rock**:
    - If water table deep (> ~10 m) AND inflow sufficient AND roof not too small → `recharge_well_or_injection`.
    - Otherwise → `recharge_shaft` (compact footprint) instead of injection.
  - **Limited space** and no strong permeability signal → `recharge_shaft_or_community` or community connection.

Guardrails at inference ensure practical outputs even if the ML boundary is imperfect.

---

## 💡 Explainability
- `predict.py` prints a short, human-readable reason (e.g., “Storage feasible: harvest ≥ demand”, or “Hard rock + deep WL but small inflow → prefer shaft over injection”).  
- If the model’s raw choice is overridden by guardrails, this is explicitly stated.

---

## 💰 Cost Estimation (Bengaluru-relative, INR)
Implemented in `estimate_cost.py` using 2024–25 ballpark unit rates for small works:
- Tanks (RCC/ferrocement or plastic), platforms, and basic plumbing/fittings.  
- Pits: excavation, gravel/sand filter, lining, cover slab, silt trap.  
- Shafts: excavation/drilling, lining, gravel pack, cover, fittings.  
- Injection wells: drilling, casing/screen, gravel pack, headworks, development/cleaning.  
- Community structures: scaled pit-like works.  

Outputs total and a breakdown per line item, with clear assumptions.

---

## 🚀 How to Run (Bengaluru prototype)

### 0) Environment
- Python 3.10 (or project’s `myenv`).  
- Install dependencies:
```bash
pip install -r requirements.txt
```

### 1) Build/refresh processed data (optional if already present)
```bash
python build_dataset.py
```

### 2) Generate synthetic dataset (uses rules + well DB)
```bash
python logic.py
```

### 3) Train models
```bash
python train_model.py
```
Models saved to `models/`.

### 4) Predict (interactive CLI)
```bash
python predict.py
```
Follow prompts; output includes: structure, dimensions, explanation, and cost (INR).

### 5) Run curated test cases
```bash
python testcases.py
```
Prints multiple Bengaluru scenarios with expected practical behavior.

---

## 🔍 Design Choices That Ensure Practicality
- Training labels come from an engineering **rulebook**, not arbitrary guesses.  
- **Guardrails** at inference prevent impractical injection wells for small roofs or tiny plots.  
- **Dimension clamping** keeps outputs within typical engineering ranges.  
- **Explainability strings** clarify why the choice was made and whether any adjustment occurred.  
- **Cost estimates** help users understand feasibility and budgeting in Bengaluru conditions.

---

## ⚠️ Scope & Limitations
- Prototype trained for **Bengaluru** only; will generalize by swapping the well DB.  
- Unit rates are **ballpark** and can vary by locality, access, and market conditions.  
- Does not replace detailed site investigation, statutory approvals, or detailed engineering design.

---

## 🗺️ Roadmap
- Add taluk/ward-level calibration data and real labeled case studies.  
- Improve rainfall temporal modeling (design storms) for peak inflow sizing.  
- Add simple hydraulic checks (first flush sizing, filter sizing calculators).  
- Build a minimal web UI showing map context, alternatives, and costs.

