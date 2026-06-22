from __future__ import annotations

from fastapi import APIRouter

from aqf_backend.config import DATASET_DIR
from aqf_backend.models import QueryRequest, QueryResponse, QueryRow
from aqf_backend.services.query_executor import QueryExecutor

router = APIRouter(prefix="/query", tags=["query"])

@router.post("/search", response_model=QueryResponse)
def search_records(request: QueryRequest):
    executor = QueryExecutor(dataset_dir=DATASET_DIR)
    payload = executor.execute(request)

    rows = []
    for row in payload["rows"]:
        if isinstance(row, QueryRow):
            rows.append(row)
            continue
        if isinstance(row, dict):
            if "fields" in row:
                rows.append(QueryRow(**row))
            else:
                rows.append(QueryRow(
                    source_file=str(row.get("source_file", "")),
                    fields={k: v for k, v in row.items() if k != "source_file"},
                ))
    return QueryResponse(
        total_matches=payload["total_matches"],
        rows=rows,
        applied_conditions=request.conditions,
        output_fields=request.output_fields,
    )
