from __future__ import annotations
import json
from pathlib import Path
from collections import defaultdict
from typing import Any, Dict, List, Tuple

from aqf_runtime.models.schema import SchemaNode, SchemaEdge, SchemaGraph


def _is_primitive(value: Any) -> bool:
    return value is None or isinstance(value, (str, int, float, bool))


class SchemaGraphBuilder:
    """Builds a lightweight schema graph from a JSON dataset.

    Expected dataset format:
    - A list of records, or
    - A dict with a top-level 'records' key.
    """

    def load_records(self, dataset_path: str | Path) -> List[Dict[str, Any]]:
        p = Path(dataset_path)
        if p.is_dir():
            candidates = list(p.glob("*.json"))
            if not candidates:
                raise FileNotFoundError(f"No JSON file found in {p}")
            p = candidates[0]
        data = json.loads(p.read_text(encoding="utf-8"))
        if isinstance(data, dict) and "records" in data:
            records = data["records"]
        elif isinstance(data, list):
            records = data
        else:
            raise ValueError("Dataset must be a list of records or a dict with a 'records' key.")
        if not isinstance(records, list):
            raise ValueError("'records' must be a list.")
        return [r for r in records if isinstance(r, dict)]

    def build(self, dataset_path: str | Path) -> SchemaGraph:
        records = self.load_records(dataset_path)
        graph = SchemaGraph(record_count=len(records))

        path_values: Dict[str, List[Any]] = defaultdict(list)
        path_presence: Dict[str, int] = defaultdict(int)
        containment_edges: Dict[Tuple[str, str], float] = defaultdict(float)

        def walk(obj: Any, prefix: str = "", parent_path: str | None = None):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    path = f"{prefix}.{key}" if prefix else key
                    if parent_path:
                        containment_edges[(parent_path, path)] += 1.0
                    walk(value, path, path)
            elif isinstance(obj, list):
                for idx, item in enumerate(obj):
                    walk(item, prefix, parent_path)
            else:
                path_values[prefix].append(obj)
                path_presence[prefix] += 1

        for rec in records:
            walk(rec)

        # Collect all paths with simple heuristics for node types and datatypes
        all_paths = sorted(set(path_values.keys()) | set(path_presence.keys()))
        for path in all_paths:
            values = path_values.get(path, [])
            coverage = (path_presence[path] / max(len(records), 1)) if path in path_presence else 0.0
            distinct = len(set(v for v in values if v is not None))
            diversity = distinct / max(len(values), 1) if values else 0.0
            sample = next((v for v in values if v is not None), None)
            if path.count(".") == 0:
                node_type = "section"
            elif path.count(".") == 1:
                node_type = "substructure"
            else:
                node_type = "leaf"
            datatype = (
                "numeric" if isinstance(sample, (int, float)) and not isinstance(sample, bool)
                else "boolean" if isinstance(sample, bool)
                else "text" if isinstance(sample, str)
                else "unknown"
            )
            node = SchemaNode(
                node_id=path.replace(".", "__"),
                label=path.split(".")[-1],
                path=path,
                node_type=node_type,
                datatype=datatype,
                coverage=coverage,
                diversity=diversity,
                metadata={"sample_value": sample},
            )
            graph.nodes[node.node_id] = node

        # containment edges from observed parent-child relations
        for (src, tgt), weight in containment_edges.items():
            if src.replace(".", "__") in graph.nodes and tgt.replace(".", "__") in graph.nodes:
                graph.edges.append(
                    SchemaEdge(source=src.replace(".", "__"), target=tgt.replace(".", "__"), edge_type="containment", weight=float(weight))
                )

        return graph
