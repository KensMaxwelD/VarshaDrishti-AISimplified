from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parents[1]
app = FastAPI(title="VarshaDrishti AI API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health():
    return {"status": "ok", "mode": "prototype", "scientific_pipeline": "not yet connected"}

@app.get("/api/study-area")
def study_area():
    return {
        "name": "Chennai pilot study area",
        "status": "configured",
        "data_layers": ["IMERG rainfall", "Copernicus DEM", "slope"],
        "planned_layers": ["Sentinel-1 flood labels", "historical inundation labels"],
    }

app.mount("/", StaticFiles(directory=ROOT / "frontend", html=True), name="frontend")
