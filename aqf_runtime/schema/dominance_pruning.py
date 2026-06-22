from __future__ import annotations
from copy import deepcopy
from aqf_runtime.models import SchemaGraph

class DominancePruner:
    def __init__(self, theta: float = 0.10, min_coverage: float = 0.0):
        self.theta = theta
        self.min_coverage = min_coverage

    def prune(self, graph: SchemaGraph) -> SchemaGraph:
        if not graph.nodes:
            return graph
        scores = [n.queriability or n.local_utility or n.coverage or 0.0 for n in graph.nodes.values()]
        maxscore = max(scores) if scores else 0.0
        if maxscore <= 0:
            return graph
        keep = {
            nid for nid, node in graph.nodes.items()
            if (node.queriability or node.local_utility or node.coverage or 0.0) >= self.theta * maxscore
            and (node.coverage_local or node.coverage or 0.0) >= self.min_coverage
        }
        pruned = SchemaGraph(record_count=graph.record_count, repository_types=list(graph.repository_types), metadata=dict(graph.metadata))
        pruned.nodes = {nid: deepcopy(node) for nid, node in graph.nodes.items() if nid in keep}
        pruned.edges = [deepcopy(e) for e in graph.edges if e.source in keep and e.target in keep]
        return pruned
