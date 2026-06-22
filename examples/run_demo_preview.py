from __future__ import annotations
import argparse
from pathlib import Path

from aqf_runtime.pipeline import AQFPipeline
from aqf_runtime.io.demo_report import render_demo_preview
from aqf_runtime.io.exporter import Exporter

def main():
    p = argparse.ArgumentParser(description="AQF Runtime Semantic V3 - Demo Preview")
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

    preview_text = render_demo_preview(
        graph_summary={**pipeline.builder.summary(), "records": len(units)},
        node_scores=node_scores,
        top_candidates=top_candidates,
        canonical_form=canonical_form.to_dict(),
        adaptive_form=adaptive_form.to_dict(),
    )
    (Path(a.output_dir) / "demo_preview.txt").write_text(preview_text, encoding="utf-8")
    print(preview_text)

if __name__ == "__main__":
    main()
