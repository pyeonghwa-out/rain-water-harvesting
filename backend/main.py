from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, Literal
import os
import sys

# Ensure AI_ML is importable regardless of where the server is started from
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
AI_ML_DIR = os.path.join(PROJECT_ROOT, "AI_ML")
if AI_ML_DIR not in sys.path:
    sys.path.insert(0, AI_ML_DIR)

from predict import predict_structure_and_dimensions, db, clf, dimension_models
from fastapi.middleware.cors import CORSMiddleware


class PredictRequest(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    rooftop_area_m2: Optional[float] = Field(None, gt=0, le=100000)
    open_area_m2: float = Field(..., ge=0, le=100000)
    roof_type: Literal["concrete", "tiled", "gi", "asbestos"]
    num_persons: int = Field(..., ge=1, le=1000)
    per_capita: Optional[float] = Field(None, gt=0, le=1000)
    period_days: Optional[int] = Field(None, ge=1, le=3650)


app = FastAPI(title="RWH Feasibility API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> Dict[str, Any]:
    return {"status": "ok", "service": "rwh-feasibility-api", "models_loaded": clf is not None and dimension_models is not None}

@app.post("/predict")
def predict(req: PredictRequest) -> Dict[str, Any]:
    try:
        # Use the in-memory DB loaded by predict.py
        result = predict_structure_and_dimensions(req.model_dump(), db)
        return result
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Prediction failed. Check server logs for model or data errors.") from e
