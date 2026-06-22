from __future__ import annotations
from typing import Any, Dict, List

def render_demo_preview(graph_summary: Dict[str, Any], node_scores: List[Dict[str, Any]], top_candidates: List[Dict[str, Any]], canonical_form: Dict[str, Any], adaptive_form: Dict[str, Any]) -> str:
    lines = []
    lines.append("AQF Demo Preview")
    lines.append("=" * 18)
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
        lines.append(f"- {row.get('concept_name')} | q={row.get('queriability', 0):.4f} | cov={row.get('coverage', row.get('coverage_local', 0)):.4f} | distinct={row.get('distinct_count', 0)} | widget={row.get('recommended_widget', 'text_input')}")
    lines.append("")
    lines.append("Candidate fields:")
    for row in top_candidates[:10]:
        lines.append(f"- {row.get('concept_name')} | {row.get('path')} | widget={row.get('recommended_widget', 'text_input')}")
    lines.append("")
    lines.append("Canonical groups:")
    for grp in canonical_form.get("groups", [])[:10]:
        lines.append(f"- {grp.get('label')} ({len(grp.get('fields', []))} fields)")
    lines.append("")
    lines.append("Adaptive form:")
    lines.append(f"- Elements: {len(adaptive_form.get('elements', []))}")
    lines.append(f"- Complexity: {adaptive_form.get('complexity', 0)}")
    return "\n".join(lines)
