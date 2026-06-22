from __future__ import annotations
from typing import Any, Dict, List

class ResultFormatter:
    def project(self, row: Dict[str, Any], output_fields: List[str]) -> Dict[str, Any]:
        return {field: row.get(field) for field in output_fields}
