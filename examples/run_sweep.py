from __future__ import annotations
import argparse
import csv
from pathlib import Path

from aqf_runtime.pipeline import AQFPipeline

def _parse_list(s: str):
    return [x.strip() for x in s.split(",") if x.strip()]

def main():
    p = argparse.ArgumentParser(description="AQF Runtime Semantic V3 - Parameter Sweep")
    p.add_argument("--input-dir", required=True)
    p.add_argument("--output-dir", default="sweep_output")
    p.add_argument("--theta-global", default="0.01,0.03,0.05,0.10")
    p.add_argument("--top-k-per-root", default="10,15,20,25")
    p.add_argument("--lambda-cc", default="0.25")
    p.add_argument("--mu", default="0.25")
    p.add_argument("--max-depth", type=int, default=10)
    a = p.parse_args()

    out_dir = Path(a.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "sweep_results.csv"

    thetas = [float(x) for x in _parse_list(a.theta_global)]
    top_ks = [int(x) for x in _parse_list(a.top_k_per_root)]
    lambda_cc = float(a.lambda_cc)
    mu = float(a.mu)

    rows = []
    for theta in thetas:
        for top_k in top_ks:
            pipeline = AQFPipeline(max_depth=a.max_depth, lambda_cc=lambda_cc, mu=mu, theta=theta)
            pipeline.top_k_per_root = top_k
            pipeline.root_selector.top_k_per_root = top_k
            _, _, selected, canonical_form, field_stats, node_scores, top_candidates = pipeline.run_phase2(a.input_dir, out_dir / f"theta_{theta}_k_{top_k}")
            rows.append({
                "theta_global": theta,
                "top_k_per_root": top_k,
                "selected_nodes": len(selected.nodes),
                "canonical_groups": len(canonical_form.groups),
                "adaptive_fields": sum(len(g.fields) for g in canonical_form.groups),
                "top_candidates": len(top_candidates),
            })

    with open(csv_path, "w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=list(rows[0].keys()) if rows else ["theta_global", "top_k_per_root", "selected_nodes", "canonical_groups", "adaptive_fields", "top_candidates"])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print(f"[OK] Sweep written to: {csv_path}")

if __name__ == "__main__":
    main()
