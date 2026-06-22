from __future__ import annotations
from aqf_runtime.models import SchemaGraph

class CoverageEngine:
    def __init__(self, global_weight: float = 0.20, local_weight: float = 0.80):
        self.global_weight = global_weight
        self.local_weight = local_weight

    def score(self, graph: SchemaGraph) -> SchemaGraph:
        root_counts = graph.metadata.get("root_record_counts", {})
        total = max(graph.record_count, 1)

        for node in graph.nodes.values():
            occ = node.occurrence_count or 0
            root_count = max(root_counts.get(node.root_name, total), 1)

            node.coverage_global = occ / total
            node.coverage_local = occ / root_count
            node.coverage = (self.global_weight * node.coverage_global) + (self.local_weight * node.coverage_local)

        return graph
