from __future__ import annotations
from collections import defaultdict
from pathlib import Path

class TreeExporter:
    def export(self, graph, output_file):
        children = defaultdict(list)
        nodes = {n.node_id: n for n in graph.nodes.values()}
        for e in graph.edges:
            if e.edge_type == "containment":
                children[e.source].append(e.target)
        with open(output_file, "w", encoding="utf-8") as fp:
            roots = [n.node_id for n in graph.nodes.values() if n.node_type == "root"]
            for root in roots:
                self._walk(root, children, nodes, fp, 0, None)
                fp.write("\n")
        return output_file

    def _walk(self, nid, children, nodes, fp, depth, parent_label):
        node = nodes[nid]
        if parent_label and node.concept_name == parent_label and node.node_type == "root":
            return
        fp.write("    " * depth + node.concept_name + "\n")
        for c in sorted(children.get(nid, [])):
            self._walk(c, children, nodes, fp, depth + 1, node.concept_name)
