from __future__ import annotations
from collections import defaultdict
from aqf_runtime.models import SchemaGraph

class QueriabilityEngine:
    def __init__(self, lambda_cc: float = 0.25, mu: float = 0.25, coverage_global_weight: float = 0.10, coverage_local_weight: float = 0.6, diversity_weight: float = 0.30):
        self.lambda_cc = lambda_cc
        self.mu = mu
        self.coverage_global_weight = coverage_global_weight
        self.coverage_local_weight = coverage_local_weight
        self.diversity_weight = diversity_weight

    def score(self, graph: SchemaGraph) -> SchemaGraph:
        adjacency = defaultdict(list)
        by_edge = {}
        for edge in graph.edges:
            adjacency[edge.source].append(edge.target)
            by_edge[(edge.source, edge.target)] = edge

        for node_id, node in graph.nodes.items():
            coverage = self.coverage_global_weight * (node.coverage_global or node.coverage or 0.0) + self.coverage_local_weight * (node.coverage_local or node.coverage or 0.0)
            diversity = node.diversity if node.diversity is not None else self._diversity_from_values(node)
            local_utility = coverage * (1.0 + self.diversity_weight * diversity)

            neighborhood_score = 0.0
            for neighbor in adjacency.get(node_id, []):
                n = graph.nodes.get(neighbor)
                if not n:
                    continue
                e = by_edge.get((node_id, neighbor))
                cc = e.containment_connectivity if e else 0.0
                co = e.cooccurrence_connectivity if e else 0.0
                sc = self.lambda_cc * cc + (1.0 - self.lambda_cc) * co
                neighborhood_score += sc * (((n.coverage_local or n.coverage or 0.0) * self.coverage_local_weight) + ((n.coverage_global or n.coverage or 0.0) * self.coverage_global_weight))

            node.local_utility = local_utility
            node.queriability = local_utility + self.mu * neighborhood_score
        return graph

    def _diversity_from_values(self, node):
        vals = [v for v in (node.distinct_values or []) if v is not None]
        if not vals:
            return 0.0
        return min(len(set(str(v) for v in vals)) / max(node.total_records or len(vals), 1), 1.0)
