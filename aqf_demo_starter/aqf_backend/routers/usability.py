from fastapi import APIRouter
from pathlib import Path
import csv
from datetime import datetime

router = APIRouter()

USABILITY_LOG = Path("aqf_runtime/exports/usability_log.csv")
USABILITY_LOG.parent.mkdir(parents=True, exist_ok=True)


@router.post("/event")
def log_event(payload: dict):
    header = ["timestamp", "participant_id", "task_id", "event_type", "value"]
    write_header = not USABILITY_LOG.exists()
    with USABILITY_LOG.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(header)
        writer.writerow([
            datetime.utcnow().isoformat(),
            payload.get("participant_id", ""),
            payload.get("task_id", ""),
            payload.get("event_type", ""),
            payload.get("value", "")
        ])
    return {"status": "ok"}


@router.get("/log")
def get_log():
    return {"path": str(USABILITY_LOG), "exists": USABILITY_LOG.exists()}
