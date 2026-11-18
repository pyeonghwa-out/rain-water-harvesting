# FastAPI service

## Start

From the repository root, install the pinned runtime dependencies and start the API:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

The API loads model artifacts and Bengaluru well observations from `AI_ML/` at startup. `GET /health` reports service/model availability. `POST /predict` accepts latitude, longitude, optional roof area, open area, roof type, household count, per-person daily demand, and storage period. Leave `rooftop_area_m2` null to request the OpenStreetMap/OpenCV detector. Put the coordinate on the target roof: it uses a building footprint when available, then segments an OpenStreetMap rendered tile if Overpass is down. The response contains the detected area and highlighted image. Enter the area manually if that roof is not mapped.

The classifier provides a model suggestion and confidence, and the dimension regressors estimate structure dimensions where a trained regressor exists. Physical water balance and local hydrogeology select the final structure; dimensions are recalculated and bounded against site inputs before cost estimation. See the repository [README](../README.md) for the full-stack startup steps.
