
from __future__ import annotations
from collections import defaultdict
from itertools import combinations
from typing import Any, Dict, List, Optional, Set

from aqf_runtime.models import RecordUnit, SchemaEdge, SchemaGraph, SchemaNode
from aqf_runtime.normalization.record_loader import RepositoryNormalizer
from aqf_runtime.schema.schema_statistics import infer_datatype

IGNORE_KEYS = {
    "uid", "external_ref", "defining_code", "terminology_id", "code_string",
    "archetype_details", "language", "territory", "category", "composer",
    "lifecycle_state", "owner_id", "versions", "commit_audit", "time_created",
    "encoding", "subject", "time",
}
ENTRY_TYPES = {"ADMIN_ENTRY", "EVALUATION", "ACTION", "OBSERVATION", "INSTRUCTION"}
CONTAINER_TYPES = {"CLUSTER", "ITEM_TREE", "ITEM_LIST", "ITEM_TABLE", "ITEM_SINGLE"}
LEAF_TYPES = {"ELEMENT"}
NODE_SKIP_LABELS = {"components", "structure", "tree"}
QUERYABLE_NODE_TYPES = {"field"}
RECURSE_KEYS = {"content", "data", "description", "context", "ism_transition", "items", "events", "state", "protocol"}

def _ensure_list(x):
    if x is None:
        return []
    if isinstance(x, list):
        return x
    if isinstance(x, dict):
        return [x]
    return []

def _extract_label(obj: Dict[str, Any], fallback: str = "") -> str:
    name = obj.get("name")
    if isinstance(name, dict):
        label = name.get("value")
        if label:
            return str(label)
    if isinstance(name, str) and name.strip():
        return name.strip()
    typ = obj.get("type") or obj.get("_type")
    if isinstance(typ, str) and typ.strip():
        return typ.strip().replace("_", " ").title()
    return fallback or "unknown"

# def _extract_value(obj: Dict[str, Any]) -> Any:
#     if obj.get("value") is not None and not isinstance(obj.get("value"), dict):
#         return obj.get("value")
#     nf = obj.get("null_flavour")
#     if isinstance(nf, dict):
#         return nf.get("value")
#     return None

def _extract_value(obj):
    """
    Extract a representative scalar value from openEHR DV_* structures.

    Priority:

    DV_TEXT
    DV_CODED_TEXT
    DV_DATE
    DV_DATE_TIME

        -> value

    DV_COUNT
    DV_QUANTITY

        -> magnitude

    null_flavour

        -> value

    fallback

        -> None
    """

    value_obj = obj.get("value")

    #
    # primitive value
    #
    if value_obj is not None and not isinstance(value_obj, dict):
        return value_obj

    #
    # DV_* object
    #
    if isinstance(value_obj, dict):

        #
        # DV_COUNT / DV_QUANTITY
        #
        if "magnitude" in value_obj:
            return value_obj.get("magnitude")

        #
        # DV_TEXT
        # DV_CODED_TEXT
        # DV_DATE
        # DV_DATE_TIME
        #
        if "value" in value_obj:
            return value_obj.get("value")

    #
    # null flavour
    #
    nf = obj.get("null_flavour")

    if isinstance(nf, dict):
        return nf.get("value")

    return None

class SchemaGraphBuilder:
    def __init__(self, max_depth: int = 10):
        self.max_depth = max_depth
        self._summary = {
            "records": 0,
            "repository_types": [],
            "node_count": 0,
            "edge_count": 0,
            "composition_like_units": 0,
            "ehr_index_units": 0,
            "demographic_units": 0,
            "composition_types": {},
        }

    def build_from_folder(self, folder):
        units = RepositoryNormalizer().load_folder(folder)
        graph = self.build_from_units(units)
        return graph, units

    def build_from_units(self, units: List[RecordUnit]) -> SchemaGraph:
        graph = SchemaGraph(record_count=len(units))
        graph.repository_types = sorted({u.repository_type for u in units})

        path_records: Dict[str, Set[str]] = defaultdict(set)
        path_values: Dict[str, List[Any]] = defaultdict(list)
        path_meta: Dict[str, Dict[str, Any]] = defaultdict(lambda: {"archetype_ids": set(), "repository_types": set(), "node_type": None, "root": None})
        unit_paths: Dict[str, Set[str]] = defaultdict(set)
        root_counts: Dict[str, int] = defaultdict(int)

        for unit in units:
            root_label = self._unit_root_label(unit)
            root_counts[root_label] += 1
            self._count_unit(unit)
            self._walk_record(
                unit=unit,
                obj=unit.raw_document,
                parent_path="",
                graph=graph,
                path_records=path_records,
                path_values=path_values,
                path_meta=path_meta,
                unit_paths=unit_paths,
                depth=0,
                context="root",
                root_label=root_label,
            )

        for path, records in path_records.items():
            meta = path_meta[path]
            node_id = self._node_id(path)
            values = path_values[path]
            label = path.split(" / ")[-1]
            root_label = meta.get("root") or path.split(" / ", 1)[0]
            total_records = root_counts.get(root_label, len(units))
            distinct_values = self._distinct_list(values)

            coverage_global = len(records) / max(len(units), 1)
            coverage_local = len(records) / max(total_records, 1)
            coverage = 0.2 * coverage_global + 0.8 * coverage_local
            diversity = len(distinct_values) / max(total_records, 1)
            recommended_widget = self._recommend_widget(
                node_type=meta["node_type"] or "subgroup",
                datatype=self._infer_datatype_from_values(values, label),
                distinct_count=len(distinct_values),
            )

            node = SchemaNode(
                node_id=node_id,
                concept_name=label,
                path=path,
                datatype=self._infer_datatype_from_values(values, label),
                node_type=meta["node_type"] or "subgroup",
                repository_types=sorted(meta["repository_types"]),
                archetype_ids=sorted(meta["archetype_ids"]),
                occurrence_count=len(records),
                record_count=len(records),
                coverage_global=coverage_global,
                coverage_local=coverage_local,
                coverage=coverage,
                diversity=diversity,
                local_utility=coverage * diversity,
                queriability=0.0,
                distinct_count=len(distinct_values),
                distinct_values=distinct_values,
                total_records=total_records,
                value_examples=distinct_values[:5],
                recommended_widget=recommended_widget,
            )
            graph.nodes[node_id] = node

        self._add_containment_edges(graph)
        self._add_cooccurrence_edges(graph, unit_paths, len(units))

        child_counts = defaultdict(int)
        for e in graph.edges:
            if e.edge_type == "containment":
                child_counts[e.source] += 1
        for node in graph.nodes.values():
            node.child_count = child_counts.get(node.node_id, 0)

        self._summary["records"] = len(units)
        self._summary["repository_types"] = graph.repository_types
        self._summary["node_count"] = len(graph.nodes)
        self._summary["edge_count"] = len(graph.edges)
        return graph

    def summary(self):
        return dict(self._summary)

    def _unit_root_label(self, unit: RecordUnit) -> str:
        if unit.composition_name:
            return unit.composition_name.strip()
        if unit.archetype_id:
            return unit.archetype_id.split(".")[-1]
        return "unknown"

    def _count_unit(self, unit: RecordUnit):
        if unit.json_type == "ehr_index_reference":
            self._summary["ehr_index_units"] += 1
        elif unit.archetype_id == "openEHR-EHR-COMPOSITION.demographic_data.v1":
            self._summary["demographic_units"] += 1
        else:
            self._summary["composition_like_units"] += 1

    def _node_id(self, path: str) -> str:
        return path.replace(" / ", "__").replace("/", "_").replace(" ", "_").replace(".", "__").replace("[", "_").replace("]", "_")

    def _infer_datatype_from_values(self, values: List[Any], field_name: str) -> str:
        for v in values:
            if isinstance(v, bool):
                return "DV_BOOLEAN"
            if isinstance(v, int) and not isinstance(v, bool):
                return "DV_COUNT"
            if isinstance(v, float):
                return "DV_QUANTITY"
            try:
                if isinstance(v, str) and v.replace(".", "", 1).isdigit():                    
                    if "." in v:
                        return "DV_QUANTITY"
                    return "DV_COUNT"
            except:
                pass
            if isinstance(v, str):               
                if len(v) >= 8 and any(ch.isdigit() for ch in v):
                    if ("-" in v and len(v[:10]) >= 10) or "T" in v:
                        return "DV_DATE"
                return infer_datatype(v, field_name)
        return infer_datatype(values[0] if values else None, field_name)

    def _recommend_widget(self, node_type: str, datatype: str, distinct_count: int) -> str:
        if node_type != "field":
            return "group"
        dt = (datatype or "").upper()
        if "DATE" in dt:
            return "date_picker"
        if "BOOLEAN" in dt:
            return "checkbox"
        if dt in {
            "DV_COUNT",
            "DV_QUANTITY",
            "DV_DURATION",
            "DV_PROPORTION",
        }:
            return "number_input"

        if distinct_count <= 20:
            return "dropdown"
        if distinct_count <= 100:
            return "autocomplete"

        return "text_input"

    def _distinct_list(self, values: List[Any], limit: int = 5000) -> List[Any]:
        seen = set()
        out = []
        for v in values:
            if isinstance(v, (dict, list)):
                continue
            key = str(v)
            if key in seen:
                continue
            seen.add(key)
            out.append(v)
            if len(out) >= limit:
                break
        return out

    def _sample_values(self, values: List[Any], limit: int = 5) -> List[Any]:
        out = []
        for v in values:
            if isinstance(v, (str, int, float, bool)) or v is None:
                out.append(v)
            if len(out) >= limit:
                break
        return out

    def _walk_record(self, unit, obj, parent_path, graph, path_records, path_values, path_meta, unit_paths, depth, context, root_label, fallback_label=""):
        if depth > self.max_depth:
            return

        if isinstance(obj, dict):
            typ = str(obj.get("type") or obj.get("_type") or "").upper()
            label = _extract_label(obj, fallback_label)
            create_node = False
            node_type = None

            if context == "root" and unit.composition_name:
                label = unit.composition_name
                typ = "COMPOSITION"
                create_node = True
                node_type = "composition"

            elif typ in ENTRY_TYPES:
                create_node = True
                node_type = "section"
                label = f"{typ.replace('_', ' ').title()}: {label}" if label else typ.title()

            elif typ in CONTAINER_TYPES:
                create_node = True
                node_type = "subgroup"

            elif typ in LEAF_TYPES:
                create_node = True
                node_type = "field"

            current_path = parent_path
            if create_node:
                current_path = f"{parent_path} / {label}" if parent_path else label
                path_records[current_path].add(unit.unit_id)
                unit_paths[unit.unit_id].add(current_path)
                meta = path_meta[current_path]
                meta["node_type"] = meta["node_type"] or node_type
                meta["repository_types"].add(unit.repository_type)
                meta["root"] = root_label
                if unit.archetype_id:
                    meta["archetype_ids"].add(unit.archetype_id)

                # Only store values for actual queryable fields; this avoids
                # wrapper/container values polluting distinct value examples.
                if node_type in QUERYABLE_NODE_TYPES:
                    val = _extract_value(obj)
                    if val is not None:
                        path_values[current_path].append(val)

            # recurse into semantic children
            for key, value in obj.items():
                if key.startswith("_"):
                    continue
                if key in IGNORE_KEYS or key in NODE_SKIP_LABELS:
                    continue
                if key in RECURSE_KEYS:
                    for child in _ensure_list(value):
                        self._walk_record(
                            unit,
                            child,
                            current_path,
                            graph,
                            path_records,
                            path_values,
                            path_meta,
                            unit_paths,
                            depth + 1,
                            "entry" if key == "content" else "container",
                            root_label,
                            fallback_label=key,
                        )
                else:
                    if isinstance(value, dict) and ("name" in value or "type" in value or "value" in value or "items" in value):
                        self._walk_record(
                            unit,
                            value,
                            current_path,
                            graph,
                            path_records,
                            path_values,
                            path_meta,
                            unit_paths,
                            depth + 1,
                            context,
                            root_label,
                            fallback_label=key,
                        )
                    elif isinstance(value, list):
                        for child in value:
                            if isinstance(child, dict):
                                self._walk_record(
                                    unit,
                                    child,
                                    current_path,
                                    graph,
                                    path_records,
                                    path_values,
                                    path_meta,
                                    unit_paths,
                                    depth + 1,
                                    context,
                                    root_label,
                                    fallback_label=key,
                                )

        elif isinstance(obj, list):
            for child in obj:
                self._walk_record(
                    unit,
                    child,
                    parent_path,
                    graph,
                    path_records,
                    path_values,
                    path_meta,
                    unit_paths,
                    depth + 1,
                    context,
                    root_label,
                    fallback_label=fallback_label,
                )

    def _add_containment_edges(self, graph: SchemaGraph):
        by_path = {node.path: nid for nid, node in graph.nodes.items()}
        for path, nid in by_path.items():
            if " / " not in path:
                continue
            parent_path = path.rsplit(" / ", 1)[0]
            parent_id = by_path.get(parent_path)
            if not parent_id:
                continue
            graph.edges.append(SchemaEdge(source=parent_id, target=nid, edge_type="containment", weight=1.0, count=1, containment_connectivity=1.0, structural_connectivity=1.0))

    def _add_cooccurrence_edges(self, graph: SchemaGraph, unit_paths: Dict[str, Set[str]], unit_count: int):
        pair_counts = defaultdict(int)
        for paths in unit_paths.values():
            sorted_paths = sorted(paths)
            for a, b in combinations(sorted_paths, 2):
                pair_counts[(a, b)] += 1
        node_by_path = {n.path: nid for nid, n in graph.nodes.items()}
        for (a, b), count in pair_counts.items():
            na, nb = node_by_path.get(a), node_by_path.get(b)
            if not na or not nb:
                continue
            weight = count / max(unit_count, 1)
            if weight < 0.1:
                continue
            graph.edges.append(SchemaEdge(source=na, target=nb, edge_type="cooccurrence", weight=weight, count=count, cooccurrence_connectivity=weight, structural_connectivity=weight))
            graph.edges.append(SchemaEdge(source=nb, target=na, edge_type="cooccurrence", weight=weight, count=count, cooccurrence_connectivity=weight, structural_connectivity=weight))
