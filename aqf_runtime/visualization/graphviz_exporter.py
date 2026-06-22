from __future__ import annotations
from pathlib import Path

class GraphVizExporter:
    def export_dot(self, graph, output_file):
        output_file = Path(output_file)
        with open(output_file, "w", encoding="utf-8") as fp:
            fp.write("digraph AQF {\n")
            fp.write('rankdir="LR";\n')
            fp.write('node [shape=box, style="rounded,filled", fillcolor="#E8F0FE"];\n')
            for node in graph.nodes.values():
                fp.write(f'"{node.node_id}" [label="{node.concept_name}\\n{node.datatype}"];\n')
            for edge in graph.edges:
                if edge.edge_type == "containment":
                    fp.write(f'"{edge.source}" -> "{edge.target}";\n')
            fp.write("}\n")
        return output_file
