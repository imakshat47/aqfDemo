from __future__ import annotations
from collections import defaultdict
from typing import Any, Dict, List

def build_report_data(graph_summary: Dict[str, Any], node_scores: List[Dict[str, Any]], top_candidates: List[Dict[str, Any]], canonical_form: Dict[str, Any], adaptive_form: Dict[str, Any], selection_summary: Dict[str, Any] | None = None) -> Dict[str, Any]:
    roots = defaultdict(list)
    for row in node_scores:
        path = row.get("path", "")
        root = row.get("root_name") or (path.split(" / ", 1)[0] if " / " in path else row.get("concept_name", "root"))
        roots[root].append(row)

    return {
        "graph_summary": graph_summary,
        "node_scores": node_scores,
        "top_candidates": top_candidates,
        "canonical_form": canonical_form,
        "adaptive_form": adaptive_form,
        "selection_summary": selection_summary or {},
        "root_groups": {k: v[:10] for k, v in roots.items()},
    }

def build_report(graph_summary: Dict[str, Any], node_scores: List[Dict[str, Any]], top_candidates: List[Dict[str, Any]], canonical_form: Dict[str, Any], adaptive_form: Dict[str, Any], selection_summary: Dict[str, Any] | None = None) -> str:
    data = build_report_data(graph_summary, node_scores, top_candidates, canonical_form, adaptive_form, selection_summary)

    lines = []
    lines.append("AQF Demo Report")
    lines.append("=" * 16)
    lines.append("")
    lines.append("Repository summary:")
    lines.append(f"- Records: {graph_summary.get('records', graph_summary.get('record_count', 0))}")
    lines.append(f"- Nodes: {graph_summary.get('node_count', 0)}")
    lines.append(f"- Edges: {graph_summary.get('edge_count', 0)}")
    lines.append(f"- Demographic units: {graph_summary.get('demographic_units', 0)}")
    lines.append(f"- Composition-like units: {graph_summary.get('composition_like_units', 0)}")
    lines.append("")

    lines.append("Top scored fields:")
    for row in node_scores[:10]:
        lines.append(
            f"- {row.get('concept_name')} | q={row.get('queriability', 0):.4f} | "
            f"loc={row.get('coverage_local', row.get('coverage', 0)):.4f} | "
            f"glob={row.get('coverage_global', row.get('coverage', 0)):.4f}"
        )
    lines.append("")

    lines.append("Candidate fields:")
    for row in top_candidates[:10]:
        lines.append(f"- {row.get('concept_name')} | {row.get('path')}")
    lines.append("")

    lines.append("Canonical groups:")
    for grp in canonical_form.get("groups", [])[:10]:
        lines.append(f"- {grp.get('label')} ({len(grp.get('fields', []))} fields)")
    lines.append("")

    if selection_summary:
        lines.append("Selection summary:")
        for root, info in selection_summary.items():
            lines.append(f"- {root}: available={info.get('available', 0)}, selected={info.get('selected', 0)}")
    lines.append("")

    lines.append("Adaptive form:")
    lines.append(f"- Elements: {len(adaptive_form.get('elements', []))}")
    lines.append(f"- Complexity: {adaptive_form.get('complexity', 0)}")

    return "\n".join(lines)
