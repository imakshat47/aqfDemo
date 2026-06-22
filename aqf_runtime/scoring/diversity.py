from __future__ import annotations
from aqf_runtime.models import SchemaGraph

def _normalize_value(v):
    if v is None:
        return None
    if isinstance(v, bool):
        return str(v).lower()
    return str(v).strip().lower()

class DiversityEngine:
    def score(self, graph: SchemaGraph) -> SchemaGraph:
        for node in graph.nodes.values():
            vals = [_normalize_value(v) for v in (node.value_examples or [])]
            vals = [v for v in vals if v is not None]
            node.total_value_count = len(vals)
            distinct = list(dict.fromkeys(vals))
            node.distinct_value_count = len(distinct)

            if node.total_value_count == 0:
                node.diversity = 0.0
                continue

            node.diversity = min(node.distinct_value_count / node.total_value_count, 1.0)

        return graph
