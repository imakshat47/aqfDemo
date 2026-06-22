from __future__ import annotations
from pathlib import Path
import json

from aqf_runtime.services.schema_graph import SchemaGraphBuilder
from aqf_runtime.services.queriability import QueriabilityEngine
from aqf_runtime.services.candidate_selection import CandidateSelector
from aqf_runtime.services.canonical_structure import CanonicalStructureBuilder
from aqf_runtime.services.operator_awareness import OperatorAwareness
from aqf_runtime.services.adaptive_forms import AdaptiveFormGenerator
from aqf_runtime.services.query_realizer import QueryRealizer


class AQFPipeline:
    def __init__(self):
        self.schema_builder = SchemaGraphBuilder()
        self.queriability = QueriabilityEngine()
        self.selector = CandidateSelector()
        self.canonical_builder = CanonicalStructureBuilder()
        self.operator_awareness = OperatorAwareness()
        self.form_generator = AdaptiveFormGenerator()
        self.query_realizer = QueryRealizer()

    def generate(self, dataset_path: str, theta: float = 0.10, complexity_budget: float = 53.0):
        graph = self.schema_builder.build(dataset_path)
        graph = self.queriability.score(graph)
        reduced = self.selector.select(graph, theta=theta)
        canonical = self.canonical_builder.build(reduced)
        canonical = self.operator_awareness.annotate(canonical)
        adaptive_form = self.form_generator.generate(canonical, complexity_budget=complexity_budget)
        return {
            "schema_graph": graph.to_dict(),
            "reduced_graph": reduced.to_dict(),
            "canonical_form": canonical.to_dict(),
            "adaptive_form": adaptive_form.to_dict(),
        }

    def export_json(self, payload: dict, out_path: str | Path):
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return str(out_path)
