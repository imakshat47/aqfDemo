from __future__ import annotations
from pathlib import Path
from uuid import uuid4
from typing import Any, Dict

from aqf_runtime.canonical.canonical_structure_generator import CanonicalStructureGenerator
from aqf_runtime.candidate_selection.clinical_filter import ClinicalFilter
from aqf_runtime.candidate_selection.root_selector import RootSelector
from aqf_runtime.io.exporter import Exporter
from aqf_runtime.models import AdaptiveForm, FormElement
from aqf_runtime.schema.dominance_pruning import DominancePruner
from aqf_runtime.schema.field_statistics import build_field_statistics, build_candidate_fields
from aqf_runtime.schema.schema_graph_builder import SchemaGraphBuilder
from aqf_runtime.scoring.queriability import QueriabilityEngine
from aqf_runtime.visualization.graphviz_exporter import GraphVizExporter
from aqf_runtime.visualization.schema_graph_exporter import SchemaGraphExporter
from aqf_runtime.visualization.tree_exporter import TreeExporter
from aqf_runtime.settings import load_config, deep_update

class AQFPipeline:
    def __init__(self, max_depth: int = 10, lambda_cc: float = 0.25, mu: float = 0.25, theta: float = 0.10, config_path: str | Path | None = None):
        defaults = load_config(config_path)
        self.config = defaults

        coverage_cfg = defaults.get("coverage", {})
        diversity_cfg = defaults.get("diversity", {})
        pruning_cfg = defaults.get("pruning", {})
        scoring_cfg = defaults.get("scoring", {})

        self.builder = SchemaGraphBuilder(max_depth=max_depth if max_depth is not None else defaults.get("schema", {}).get("max_depth", 10))
        self.scorer = QueriabilityEngine(
            lambda_cc=scoring_cfg.get("lambda_cc", lambda_cc),
            mu=scoring_cfg.get("mu", mu),
            coverage_global_weight=coverage_cfg.get("global_weight", 0.2),
            coverage_local_weight=coverage_cfg.get("local_weight", 0.8),
            diversity_weight=diversity_cfg.get("weight", 0.25),
        )
        self.pruner = DominancePruner(theta=pruning_cfg.get("theta_global", theta), min_coverage=pruning_cfg.get("min_coverage_local", 0.0))
        self.canonical_gen = CanonicalStructureGenerator()
        self.theta = pruning_cfg.get("theta_global", theta)
        self.top_k_per_root = pruning_cfg.get("top_k_per_root", 20)
        self.max_distinct_values = diversity_cfg.get("max_dropdown_values", 20)
        self.clinical_filter = ClinicalFilter()
        self.root_selector = RootSelector(top_k_per_root=self.top_k_per_root)

    def run_phase1(self, input_dir, output_dir):
        output_dir = Path(output_dir)
        exporter = Exporter(output_dir)
        graph, units = self.builder.build_from_folder(input_dir)
        exporter.save_record_units(units)
        exporter.save_schema_graph(graph)
        exporter.save_summary(self.builder.summary())
        viz = SchemaGraphExporter(output_dir)
        viz.export_nodes_csv(graph)
        viz.export_edges_csv(graph)
        viz.export_top_nodes(graph)
        viz.export_summary(graph, self.builder.summary())
        TreeExporter().export(graph, output_dir / "schema_graph_tree.txt")
        GraphVizExporter().export_dot(graph, output_dir / "schema_graph.dot")
        return graph, units

    def run_phase2(self, input_dir, output_dir):
        output_dir = Path(output_dir)
        exporter = Exporter(output_dir)
        graph, units = self.builder.build_from_folder(input_dir)
        graph = self.scorer.score(graph)

        # clinical filter first
        clinical_nodes = {nid: node for nid, node in graph.nodes.items() if self.clinical_filter.keep(node)}
        graph.nodes = clinical_nodes
        graph.edges = [e for e in graph.edges if e.source in clinical_nodes and e.target in clinical_nodes]

        # global pruning
        pruned = self.pruner.prune(graph)

        # per-root candidate selection for demo and form generation
        keep_ids = self.root_selector.select(pruned)
        selected = type(pruned)(record_count=pruned.record_count, repository_types=list(pruned.repository_types), metadata=dict(pruned.metadata))
        selected.nodes = {nid: node for nid, node in pruned.nodes.items() if nid in keep_ids}
        selected.edges = [e for e in pruned.edges if e.source in keep_ids and e.target in keep_ids]

        canonical_form = self.canonical_gen.build(selected)

        exporter.save_record_units(units)
        exporter.save_schema_graph(graph)
        exporter.save_canonical_form(canonical_form)
        exporter.save_json({
            "node_count_before": len(graph.nodes),
            "node_count_after_clinical_filter": len(clinical_nodes),
            "node_count_after_global_prune": len(pruned.nodes),
            "node_count_after_root_select": len(selected.nodes),
            "edge_count_before": len(graph.edges),
            "edge_count_after": len(selected.edges),
            "theta_global": self.theta,
            "top_k_per_root": self.top_k_per_root,
        }, "pruned_graph_summary.json")

        field_stats = build_field_statistics(selected)
        candidate_fields = build_candidate_fields(selected, top_k=self.top_k_per_root, max_distinct_values=self.max_distinct_values)
        exporter.save_field_statistics(field_stats)
        exporter.save_candidate_fields(candidate_fields)

        viz = SchemaGraphExporter(output_dir)
        viz.export_nodes_csv(selected)
        viz.export_edges_csv(selected)
        viz.export_top_nodes(selected)
        viz.export_summary(selected, self.builder.summary())
        TreeExporter().export(selected, output_dir / "schema_graph_tree.txt")
        GraphVizExporter().export_dot(selected, output_dir / "schema_graph.dot")

        node_scores = [{
            "node_id": n.node_id,
            "concept_name": n.concept_name,
            "path": n.path,
            "coverage_global": n.coverage_global,
            "coverage_local": n.coverage_local,
            "coverage": n.coverage,
            "diversity": n.diversity,
            "local_utility": n.local_utility,
            "queriability": n.queriability,
            "distinct_count": n.distinct_count,
            "distinct_values": n.distinct_values[:self.max_distinct_values],
            "recommended_widget": n.recommended_widget
        } for n in sorted(graph.nodes.values(), key=lambda x: x.queriability, reverse=True)]
        exporter.save_json(node_scores, "node_scores.json")
        maxscore = max([n["queriability"] for n in node_scores], default=0)
        top_candidates = [x for x in node_scores if x["queriability"] >= self.theta * maxscore] if maxscore > 0 else []
        exporter.save_json(top_candidates, "top_candidates.json")
        return graph, pruned, selected, canonical_form, field_stats, node_scores, top_candidates

    def build_adaptive_form(self, canonical_form):
        elements = []
        for group in canonical_form.groups:
            for field in group.fields:
                elements.append(FormElement(
                    field_id=field.field_id,
                    label=field.label,
                    path=field.path,
                    datatype=field.datatype,
                    allowed_operators=field.allowed_operators,
                    queriability=field.queriability,
                    role="filter",
                    distinct_values=field.distinct_values[:self.max_distinct_values],
                    recommended_widget=field.recommended_widget,
                    metadata=field.metadata,
                ))
        return AdaptiveForm(form_id=str(uuid4()), title="AQF Adaptive Form", complexity=float(len(elements)), elements=elements, metadata={"source": "canonical_form"})
