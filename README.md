# Zenkai Rainwater Intelligence

Zenkai combines household demand, roof runoff, nearby Bengaluru rainfall and groundwater observations, and hydrogeology checks to recommend a rainwater storage or recharge system. The web app is a React/Vite interface with custom CSS, Three.js visuals, Motion transitions, and Lucide icons. The API is FastAPI; trained scikit-learn models contribute classifier and dimension-estimate signals, while water-balance and site constraints determine the final recommendation and sizing.

## Run locally

Use Python 3.10–3.12 and Node.js 20 or newer.

1. Create and activate a Python virtual environment from the repository root, then install `backend/requirements.txt`.
2. Start the API from the repository root:

   ```powershell
   python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
   ```

   The API serves `GET /health` and `POST /predict` at `http://127.0.0.1:8000`.
3. In a second terminal, install and start the frontend:

   ```powershell
   cd frontend/rain-water
   npm install
   npm run dev
   ```

   To use a different API origin, create `frontend/rain-water/.env.local` with `VITE_API_URL=http://127.0.0.1:8000` and restart Vite. No Clerk account or key is required.

The models and Bengaluru observation dataset are loaded from `AI_ML/models/` and `AI_ML/data/processed/wells_with_rainfall.csv`. Leave the roof-area field blank to detect it automatically; place the coordinate directly on the roof. Detection first uses an OpenStreetMap building footprint, then falls back to an OpenCV mask on a rendered OpenStreetMap tile when the footprint API is unavailable. The result displays its detected area, highlighted image, and map attribution. If the coordinate is not mapped as a building, enter the area manually.

## Input and output

The planner accepts latitude/longitude, roof and open-ground areas, one of four roof types, household size, daily per-person demand, and a storage period. The response includes annual harvest potential, design demand, local rainfall, recommended structure and dimensions, indicative Bengaluru cost, nearest observation point, and model diagnostics. Cost figures are planning estimates, not contractor quotes.

More detail on the model workflow is in [AI_ML/README.md](AI_ML/README.md), and the API setup notes are in [backend/README.md](backend/README.md).
