from __future__ import annotations
from typing import Any

def infer_datatype(value: Any, field_name: str = "") -> str:
    name = (field_name or "").lower()
    # if value is None:
    #     return "unknown"
    if isinstance(value, bool):
        return "DV_BOOLEAN"
    if isinstance(value, int) and not isinstance(value, bool):
        return "DV_COUNT"
    if isinstance(value, float):
        return "DV_QUANTITY"
    if isinstance(value, str):
        if any(tok in name for tok in ["date", "birth", "discharge", "start", "issue"]):
            return "DV_DATE"
        if any(tok in name for tok in ["gender", "nationality", "race", "level", "problem", "procedure", "state", "schema", "diagnosis", "admission", "discharge"]):
            return "DV_CODED_TEXT"
        return "DV_TEXT"
    return "unknown"
