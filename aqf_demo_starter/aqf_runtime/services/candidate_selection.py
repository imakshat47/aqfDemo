from __future__ import annotations
from typing import List
from copy import deepcopy

from aqf_runtime.models.schema import SchemaGraph, SchemaNode, SchemaEdge


class CandidateSelector:
    def select(self, graph: SchemaGraph, theta: float = 0.10) -> SchemaGraph:
        if not graph.nodes:
            return graph
        maxscore = max(n.queriability for n in graph.nodes.values())
        keep = {nid for nid, n in graph.nodes.items() if n.queriability >= theta * maxscore}

        reduced = SchemaGraph(record_count=graph.record_count)
        reduced.nodes = {nid: deepcopy(n) for nid, n in graph.nodes.items() if nid in keep}
        for edge in graph.edges:
            if edge.source in keep and edge.target in keep:
                reduced.edges.append(deepcopy(edge))
        return reduced
