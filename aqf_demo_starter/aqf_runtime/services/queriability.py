from __future__ import annotations
from collections import defaultdict
from typing import Dict, List

from aqf_runtime.models.schema import SchemaGraph, SchemaEdge


class QueriabilityEngine:
    """Assign queriability scores using coverage, diversity, and neighborhood influence."""

    def score(self, graph: SchemaGraph, lambda_sc: float = 0.25, mu: float = 0.25) -> SchemaGraph:
        adjacency = defaultdict(list)
        edge_weight = {}

        for edge in graph.edges:
            adjacency[edge.source].append(edge.target)
            adjacency[edge.target].append(edge.source)
            edge_weight[(edge.source, edge.target)] = edge.weight
            edge_weight[(edge.target, edge.source)] = edge.weight

        for node_id, node in graph.nodes.items():
            lu = node.coverage * node.diversity

            neighborhood_score = 0.0
            for neighbor in adjacency.get(node_id, []):
                n = graph.nodes[neighbor]
                cc = 1.0 if any(e.source == node_id and e.target == neighbor and e.edge_type == "containment" for e in graph.edges) else 0.0
                co = 0.0
                sc = lambda_sc * cc + (1 - lambda_sc) * co
                neighborhood_score += sc * (n.coverage * n.diversity)

            node.queriability = lu + mu * neighborhood_score
            node.metadata["local_utility"] = lu
            node.metadata["neighborhood_score"] = neighborhood_score
        return graph
