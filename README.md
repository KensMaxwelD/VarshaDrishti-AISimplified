# VarshaDrishti AI

Deployable prototype for rainfall-driven inundation risk research.

## Current status

- Frontend: existing HTML prototype copied to `frontend/index.html`.
- Backend: FastAPI scaffold with health and study-area endpoints.
- Scientific pipeline: raster inspection utility only; no trained model yet.
- Pilot area: Chennai, Tamil Nadu.

## Run locally

```bash
python -m venv .venv
# Activate the environment for your operating system
pip install -r requirements.txt
uvicorn backend.api:app --reload
```

Open `http://127.0.0.1:8000`.

Health endpoint: `http://127.0.0.1:8000/api/health`

## Scientific implementation order

1. Reproject and align rainfall, DEM, and slope layers.
2. Create rainfall accumulation features.
3. Add Sentinel-1-derived flood labels.
4. Train and evaluate a baseline classifier by historical event.
5. Connect model outputs to the frontend.
