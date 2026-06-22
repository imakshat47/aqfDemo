from __future__ import annotations
import argparse
from aqf_runtime.pipeline import AQFPipeline

def main():
    p = argparse.ArgumentParser(description="AQF Runtime Semantic V3 - Phase 1")
    p.add_argument("--input-dir", required=True)
    p.add_argument("--output-dir", default="output")
    p.add_argument("--max-depth", type=int, default=10)
    p.add_argument("--config", default=None)
    a = p.parse_args()
    pipeline = AQFPipeline(max_depth=a.max_depth, config_path=a.config)
    graph, units = pipeline.run_phase1(a.input_dir, a.output_dir)
    print(f"[OK] Loaded record units: {len(units)}")
    print(f"[OK] Schema nodes: {len(graph.nodes)}")
    print(f"[OK] Schema edges: {len(graph.edges)}")
    print(f"[OK] Outputs written to: {a.output_dir}")

if __name__ == "__main__":
    main()
