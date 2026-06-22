from __future__ import annotations
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from aqf_backend.config import DATASET_DIR
from aqf_backend.models import QueryCondition, QueryRequest
from aqf_backend.services.metadata_service import MetadataService
from aqf_backend.services.record_loader import RecordLoader

def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()

def normalize_operator(operator: str) -> str:
    op = norm(operator)
    return {
        "is": "=", "equals": "=", "=": "=",
        "is not": "!=", "not equal": "!=", "!=": "!=",
        "contains": "contains", "starts with": "startswith", "begins with": "startswith",
        "greater than": ">", "more than": ">", ">": ">",
        "less than": "<", "<": "<", "between": "between",
    }.get(op, op)

def parse_number(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    m = re.search(r"-?\d+(?:\.\d+)?", str(value))
    return float(m.group(0)) if m else None

def parse_date(value: Any) -> Optional[datetime]:
    text = str(value).strip()
    if not text:
        return None
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"):
        try:
            return datetime.strptime(text[: len(fmt.replace("%f", "ffffff"))], fmt)
        except Exception:
            pass
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except Exception:
        return None

@dataclass
class SearchableRecord:
    source_file: str
    semantic_map: Dict[str, List[str]]
    semantic_text: str
    raw: Dict[str, Any]

class QueryExecutor:
    def __init__(self, dataset_dir: str | Path = DATASET_DIR, metadata_service: MetadataService | None = None):
        self.dataset_dir = Path(dataset_dir)
        self.loader = RecordLoader()
        self.metadata_service = metadata_service or MetadataService(dataset_dir=self.dataset_dir)
        self.metadata_service.load()
        self.records: List[SearchableRecord] = [
            SearchableRecord(r.source_file, r.semantic_map, r.semantic_text, r.raw)
            for r in self.loader.load_semantic_records(self.dataset_dir)
        ]

    def execute(self, request: QueryRequest) -> Dict[str, Any]:
        rows: List[Dict[str, Any]] = []
        for rec in self.records:
            if all(self._matches_one(rec, c) for c in request.conditions):
                rows.append(self._project(rec, request.output_fields))
        return {
            "total_matches": len(rows),
            "rows": rows,
            "applied_conditions": [c.model_dump() for c in request.conditions],
            "output_fields": request.output_fields,
        }

    def _aliases(self, field: str) -> List[str]:
        entry = self.metadata_service.resolve_field_entry(field)
        out = {norm(field)}
        if entry:
            out.update(norm(a) for a in entry.get("aliases", []))
            out.add(norm(entry.get("concept_name", "")))
            out.add(norm(entry.get("composition", "")))
            out.add(norm(entry.get("section", "")))
            out.add(norm(entry.get("path", "")))
        return [a for a in out if a]

    def _candidate_values(self, rec: SearchableRecord, aliases: List[str]) -> List[str]:
        values: List[str] = []
        alias_set = set(aliases)
        for label, vals in rec.semantic_map.items():
            if norm(label) in alias_set:
                for v in vals:
                    s = str(v).strip()
                    if s and s not in values:
                        values.append(s)
        return values

    def _matches_one(self, rec: SearchableRecord, cond: QueryCondition) -> bool:
        op = normalize_operator(cond.operator)
        aliases = self._aliases(cond.field)
        values = self._candidate_values(rec, aliases)
        target = cond.value

        if op in {"=", "!="}:
            hit = any(norm(v) == norm(str(target)) for v in values) if values else norm(str(target)) in rec.semantic_text
            return (not hit) if op == "!=" else hit

        if op == "contains":
            t = norm(str(target))
            return any(t in norm(v) for v in values) if values else t in rec.semantic_text

        if op == "startswith":
            t = norm(str(target))
            return any(norm(v).startswith(t) for v in values) if values else rec.semantic_text.startswith(t)

        if op in {">", "<", "between"}:
            return self._numeric_or_date(values, target, op)

        return norm(str(target)) in rec.semantic_text

    def _numeric_or_date(self, values: List[str], target: Any, op: str) -> bool:
        tnum = parse_number(target)
        if tnum is not None:
            nums = [n for n in (parse_number(v) for v in values) if n is not None]
            if not nums:
                return False
            if op == ">":
                return any(n > tnum for n in nums)
            if op == "<":
                return any(n < tnum for n in nums)
            if op == "between":
                parts = [p.strip() for p in str(target).split(",") if p.strip()]
                if len(parts) == 2:
                    low, high = parse_number(parts[0]), parse_number(parts[1])
                    if low is not None and high is not None:
                        return any(low <= n <= high for n in nums)
            return False

        tdt = parse_date(target)
        if tdt is not None:
            dts = [d for d in (parse_date(v) for v in values) if d is not None]
            if not dts:
                return False
            if op == ">":
                return any(d > tdt for d in dts)
            if op == "<":
                return any(d < tdt for d in dts)
            if op == "between":
                parts = [p.strip() for p in str(target).split(",") if p.strip()]
                if len(parts) == 2:
                    low, high = parse_date(parts[0]), parse_date(parts[1])
                    if low and high:
                        return any(low <= d <= high for d in dts)
        return False

    def _project(self, rec: SearchableRecord, output_fields: List[str]) -> Dict[str, Any]:
        projected: Dict[str, Any] = {}
        for field in output_fields:
            projected[field] = self._resolve_value(rec, field)
        return {
            "source_file": rec.source_file,
            "fields": projected,
        }

    def _resolve_value(self, rec: SearchableRecord, field: str) -> Any:
        aliases = set(self._aliases(field))
        for label, values in rec.semantic_map.items():
            if norm(label) in aliases:
                return values[0] if len(values) == 1 else values
        return field if norm(field) in rec.semantic_text else None
