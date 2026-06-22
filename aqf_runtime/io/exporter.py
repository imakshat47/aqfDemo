from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List
from aqf_runtime.models import RecordUnit, SchemaGraph, CanonicalForm, AdaptiveForm

class Exporter:
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    def _save_json(self, obj, filename):
        path = self.output_dir / filename
        path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")
        return path
    def save_record_units(self, units: List[RecordUnit]): return self._save_json([u.to_dict() for u in units], "normalized_records.json")
    def save_schema_graph(self, graph: SchemaGraph): return self._save_json(graph.to_dict(), "schema_graph.json")
    def save_canonical_form(self, canonical_form: CanonicalForm): return self._save_json(canonical_form.to_dict(), "canonical_form.json")
    def save_adaptive_form(self, adaptive_form: AdaptiveForm): return self._save_json(adaptive_form.to_dict(), "adaptive_form.json")
    def save_summary(self, summary: Dict): return self._save_json(summary, "schema_graph_summary.json")
    def save_json(self, payload, filename: str): return self._save_json(payload, filename)
    def save_field_statistics(self, rows): return self._save_json(rows, "field_statistics.json")
    def save_candidate_fields(self, rows): return self._save_json(rows, "candidate_fields.json")
    def save_report(self, text: str): 
        path = self.output_dir / "aqf_report.txt"
        path.write_text(text, encoding="utf-8")
        return path
