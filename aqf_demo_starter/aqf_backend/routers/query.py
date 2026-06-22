from fastapi import APIRouter, HTTPException
from aqf_runtime.services.query_realizer import QueryRealizer
from aqf_backend.routers.aqf import LAST_RESULT

router = APIRouter()
realizer = QueryRealizer()


@router.post("/explain")
def explain(payload: dict):
    selected = payload.get("selected", [])
    return realizer.explain(selected).to_dict()


@router.post("/run")
def run_query(payload: dict):
    # Starter implementation: return the query explanation and selected rows placeholder
    selected = payload.get("selected", [])
    if not selected:
        raise HTTPException(status_code=400, detail="No selected fields provided.")
    explanation = realizer.explain(selected).to_dict()
    return {
        "query": explanation["generated_aql"],
        "predicates": explanation["predicates"],
        "results": [],
        "message": "Query execution is a placeholder in the starter. Connect this to your data source."
    }
