from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import json

router = APIRouter()

DATASET_STATE = {"dataset_path": None, "summary": None}


@router.post("/load")
async def load_dataset(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".json"):
        raise HTTPException(status_code=400, detail="Only JSON datasets are supported in the starter.")
    content = await file.read()
    path = Path("datasets") / "sample" / file.filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    data = json.loads(content.decode("utf-8"))
    records = data["records"] if isinstance(data, dict) and "records" in data else data
    DATASET_STATE["dataset_path"] = str(path)
    DATASET_STATE["summary"] = {
        "records": len(records) if isinstance(records, list) else 0,
        "source_file": file.filename,
    }
    return DATASET_STATE["summary"]


@router.get("/summary")
def summary():
    return DATASET_STATE
