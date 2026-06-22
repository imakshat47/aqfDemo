from __future__ import annotations
import csv, json
from pathlib import Path

class SchemaGraphExporter:
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_nodes_csv(self, graph):
        path = self.output_dir / "schema_nodes.csv"
        with open(path, "w", newline="", encoding="utf-8") as fp:
            w = csv.writer(fp)
            w.writerow(["node_id","concept_name","path","datatype","node_type","coverage_global","coverage_local","coverage","child_count","queriability","distinct_count","recommended_widget"])
            for n in graph.nodes.values():
                w.writerow([n.node_id, n.concept_name, n.path, n.datatype, n.node_type, round(n.coverage_global, 4), round(n.coverage_local, 4), round(n.coverage, 4), n.child_count, round(n.queriability, 4), n.distinct_count, n.recommended_widget])
        return path

    def export_edges_csv(self, graph):
        path = self.output_dir / "schema_edges.csv"
        with open(path, "w", newline="", encoding="utf-8") as fp:
            w = csv.writer(fp)
            w.writerow(["source","target","edge_type","weight","count","containment_connectivity","cooccurrence_connectivity","structural_connectivity"])
            for e in graph.edges:
                w.writerow([e.source, e.target, e.edge_type, e.weight, e.count, e.containment_connectivity, e.cooccurrence_connectivity, e.structural_connectivity])
        return path

    def export_top_nodes(self, graph, top_k=100):
        nodes = sorted(graph.nodes.values(), key=lambda x: (x.queriability, x.coverage_local, x.coverage_global), reverse=True)
        payload = [{"path": n.path, "label": n.concept_name, "datatype": n.datatype, "coverage_global": n.coverage_global, "coverage_local": n.coverage_local, "coverage": n.coverage, "queriability": n.queriability, "node_type": n.node_type, "distinct_count": n.distinct_count, "distinct_values": n.distinct_values[:20], "recommended_widget": n.recommended_widget} for n in nodes[:top_k]]
        path = self.output_dir / "top_nodes.json"
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    def export_summary(self, graph, summary):
        path = self.output_dir / "schema_graph_summary.json"
        payload = dict(summary)
        payload.update({"record_count": graph.record_count, "node_count": len(graph.nodes), "edge_count": len(graph.edges), "repository_types": graph.repository_types})
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return path
