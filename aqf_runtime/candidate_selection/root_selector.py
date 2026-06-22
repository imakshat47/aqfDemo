from __future__ import annotations
from collections import defaultdict

class RootSelector:
    def __init__(self, top_k_per_root: int = 20):
        self.top_k_per_root = top_k_per_root

    def select(self, graph):
        groups = defaultdict(list)
        # for node in graph.nodes.values():
        #     root = node.path.split(" / ", 1)[0]
        #     groups[root].append(node)
        for node in graph.nodes.values():

            if node.node_type != "field":
                continue
            
            root = node.path.split(" / ", 1)[0]
        
            groups[root].append(node)

        keep = set()
        for root, nodes in groups.items():
            ranked = sorted(nodes, key=lambda n: (n.queriability, n.coverage_local, n.coverage_global), reverse=True)
            for node in ranked[: self.top_k_per_root]:
                keep.add(node.node_id)
        return keep
