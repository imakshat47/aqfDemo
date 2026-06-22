from __future__ import annotations
from collections import defaultdict
from statistics import pstdev
from typing import Any, Dict, Iterable, List

from aqf_runtime.models import SchemaGraph, SchemaNode

from collections import Counter


class FieldStatisticsEngine:
    """
    Computes basic field statistics used by AQF scoring.

    Current metrics:
    - occurrence count
    - distinct values
    - diversity score
    - sample values

    Later:
    - datatype-aware diversity
    - widget recommendations
    - operator recommendations
    """

    def __init__(self, max_examples=25):
        self.max_examples = max_examples

    def compute(self, field_values):
        """
        field_values:
            {
                "gender": ["Male", "Female", ...],
                "race": ["White", "Asian", ...]
            }
        """

        stats = {}

        for field_name, values in field_values.items():

            clean_values = [
                str(v).strip()
                for v in values
                if v is not None and str(v).strip()
            ]

            total = len(clean_values)

            if total == 0:
                stats[field_name] = {
                    "count": 0,
                    "distinct_count": 0,
                    "diversity": 0.0,
                    "distinct_values": []
                }
                continue

            counter = Counter(clean_values)

            distinct_values = sorted(counter.keys())

            diversity = len(distinct_values) / total

            stats[field_name] = {
                "count": total,
                "distinct_count": len(distinct_values),
                "diversity": round(diversity, 4),
                "distinct_values": distinct_values[: self.max_examples]
            }

        return stats

LOW_CARDINALITY_THRESHOLD = 20
MEDIUM_CARDINALITY_THRESHOLD = 100

def _str_value(v: Any) -> str | None:
    if v is None:
        return None
    if isinstance(v, bool):
        return "True" if v else "False"
    return str(v)

def distinct_values_for_node(node: SchemaNode) -> List[Any]:
    values = []
    seen = set()
    for v in node.distinct_values:
        sv = _str_value(v)
        if sv is None:
            continue
        if sv not in seen:
            seen.add(sv)
            values.append(v)
    return values

def infer_widget(datatype: str, distinct_count: int, total_records: int) -> str:
    dt = (datatype or "").upper()
    if "DATE" in dt:
        return "date_picker"
    if "BOOLEAN" in dt:
        return "checkbox"
    if dt in {"DV_COUNT", "DV_QUANTITY", "DV_DURATION", "DV_PROPORTION"}:
        return "number_input"
    if distinct_count == 0:
        return "text_input"
    if distinct_count <= LOW_CARDINALITY_THRESHOLD:
        return "dropdown"
    if distinct_count <= MEDIUM_CARDINALITY_THRESHOLD:
        return "autocomplete"
    return "text_input"

def build_field_statistics(graph: SchemaGraph) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for node in sorted(graph.nodes.values(), key=lambda n: (n.queriability, n.coverage), reverse=True):
        if node.node_type != "field":
            continue
        values = distinct_values_for_node(node)
        row = {
            "node_id": node.node_id,
            "concept_name": node.concept_name,
            "path": node.path,
            "datatype": node.datatype,
            "node_type": node.node_type,
            "coverage_global": node.coverage_global,
            "coverage_local": node.coverage_local,
            "coverage": node.coverage,
            "diversity": node.diversity,
            "distinct_count": len(values),
            "distinct_values": values,
            "total_records": node.total_records,
            "queriability": node.queriability,
            "recommended_widget": node.recommended_widget or infer_widget(node.datatype, len(values), node.total_records),
        }
        rows.append(row)
    return rows

def build_candidate_fields(graph: SchemaGraph, top_k: int = 50, max_distinct_values: int = 20) -> List[Dict[str, Any]]:
    rows = build_field_statistics(graph)[:top_k]
    output = []
    for row in rows:
        values = row["distinct_values"][:max_distinct_values]
        row = dict(row)
        row["distinct_values"] = values
        row["recommended_widget"] = infer_widget(row["datatype"], len(values), row["total_records"])
        output.append(row)
    return output
