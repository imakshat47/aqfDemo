from __future__ import annotations
import argparse
from pathlib import Path
from aqf_runtime.pipeline import AQFPipeline
from aqf_runtime.io.exporter import Exporter

def main():
    p = argparse.ArgumentParser(description="AQF Runtime Semantic V3 - Full Demo")
    p.add_argument("--input-dir", required=True)
    p.add_argument("--output-dir", default="output")
    p.add_argument("--max-depth", type=int, default=10)
    p.add_argument("--lambda-cc", type=float, default=0.25)
    p.add_argument("--mu", type=float, default=0.25)
    p.add_argument("--theta", type=float, default=0.03)
    p.add_argument("--config", default=None)
    a = p.parse_args()
    pipeline = AQFPipeline(max_depth=a.max_depth, lambda_cc=a.lambda_cc, mu=a.mu, theta=a.theta, config_path=a.config)
    graph, units = pipeline.run_phase1(a.input_dir, a.output_dir)
    graph, pruned, selected, canonical_form, field_stats, node_scores, top_candidates = pipeline.run_phase2(a.input_dir, a.output_dir)
    adaptive_form = pipeline.build_adaptive_form(canonical_form)
    exporter = Exporter(Path(a.output_dir))
    exporter.save_adaptive_form(adaptive_form)
    preview = {
        "records": len(units),
        "nodes": len(graph.nodes),
        "pruned_nodes": len(pruned.nodes),
        "selected_nodes": len(selected.nodes),
        "canonical_groups": len(canonical_form.groups),
        "adaptive_elements": len(adaptive_form.elements),
        "top_5_candidates": top_candidates[:5],
    }
    exporter.save_json(preview, "demo_preview.json")
    print(f"[OK] Loaded record units: {len(units)}")
    print(f"[OK] Schema nodes: {len(graph.nodes)}")
    print(f"[OK] Pruned nodes: {len(pruned.nodes)}")
    print(f"[OK] Selected nodes: {len(selected.nodes)}")
    print(f"[OK] Canonical groups: {len(canonical_form.groups)}")
    print(f"[OK] Adaptive elements: {len(adaptive_form.elements)}")
    print(f"[OK] Outputs written to: {a.output_dir}")

if __name__ == "__main__":
    main()
