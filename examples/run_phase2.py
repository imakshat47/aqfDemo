from __future__ import annotations
import argparse
from pathlib import Path
from aqf_runtime.pipeline import AQFPipeline
from aqf_runtime.io.exporter import Exporter

def main():
    p = argparse.ArgumentParser(description="AQF Runtime Semantic V3 - Phase 2")
    p.add_argument("--input-dir", required=True)
    p.add_argument("--output-dir", default="output")
    p.add_argument("--max-depth", type=int, default=10)
    p.add_argument("--lambda-cc", type=float, default=0.25)
    p.add_argument("--mu", type=float, default=0.25)
    p.add_argument("--theta", type=float, default=0.03)
    p.add_argument("--config", default=None)
    a = p.parse_args()
    pipeline = AQFPipeline(max_depth=a.max_depth, lambda_cc=a.lambda_cc, mu=a.mu, theta=a.theta, config_path=a.config)
    graph, pruned, selected, canonical_form, field_stats, node_scores, top_candidates = pipeline.run_phase2(a.input_dir, a.output_dir)
    adaptive_form = pipeline.build_adaptive_form(canonical_form)
    exporter = Exporter(Path(a.output_dir))
    exporter.save_adaptive_form(adaptive_form)
    print(f"[OK] Scored nodes: {len(graph.nodes)}")
    print(f"[OK] Pruned nodes: {len(pruned.nodes)}")
    print(f"[OK] Selected nodes: {len(selected.nodes)}")
    print(f"[OK] Canonical groups: {len(canonical_form.groups)}")
    print(f"[OK] Adaptive elements: {len(adaptive_form.elements)}")
    print(f"[OK] Top candidates: {len(top_candidates)}")
    print(f"[OK] Outputs written to: {a.output_dir}")

if __name__ == "__main__":
    main()
