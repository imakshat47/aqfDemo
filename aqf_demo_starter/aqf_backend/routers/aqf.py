from fastapi import APIRouter, HTTPException
from pathlib import Path
from aqf_runtime.pipeline import AQFPipeline
from aqf_backend.routers.repository import DATASET_STATE

router = APIRouter()
pipeline = AQFPipeline()
LAST_RESULT = None


@router.post("/generate")
def generate(theta: float = 0.10, complexity_budget: float = 53.0):
    global LAST_RESULT
    dataset_path = DATASET_STATE.get("dataset_path")
    if not dataset_path or not Path(dataset_path).exists():
        raise HTTPException(status_code=400, detail="Load a JSON dataset first.")
    LAST_RESULT = pipeline.generate(dataset_path, theta=theta, complexity_budget=complexity_budget)
    return LAST_RESULT


@router.get("/latest")
def latest():
    return LAST_RESULT or {}
