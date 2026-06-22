from __future__ import annotations
from collections import defaultdict
from typing import Dict, List

from aqf_runtime.models.schema import SchemaGraph
from aqf_runtime.models.canonical import CanonicalTree, CanonicalForm, CanonicalGroup, CanonicalField


class CanonicalStructureBuilder:
    def build(self, reduced_graph: SchemaGraph) -> CanonicalForm:
        groups: Dict[str, List[CanonicalField]] = defaultdict(list)

        for node in reduced_graph.nodes.values():
            top_group = node.path.split(".")[0]
            groups[top_group].append(
                CanonicalField(
                    field_id=node.node_id,
                    label=node.label,
                    path=node.path,
                    datatype=node.datatype,
                    queriability=node.queriability,
                    metadata={"node_type": node.node_type},
                )
            )

        input_groups = []
        output_groups = []
        relationship = []

        for group_name, fields in sorted(groups.items()):
            sorted_fields = sorted(fields, key=lambda f: f.queriability, reverse=True)
            input_fields = [f for f in sorted_fields if f.datatype in {"text", "numeric", "boolean", "unknown"}][:8]
            output_fields = [f for f in sorted_fields if f.datatype in {"numeric", "text"}][:8]

            input_groups.append(CanonicalGroup(group_id=f"in_{group_name}", label=group_name, fields=input_fields))
            output_groups.append(CanonicalGroup(group_id=f"out_{group_name}", label=group_name, fields=output_fields))
            relationship.append({"group": group_name, "field_count": len(fields)})

        return CanonicalForm(
            input_tree=CanonicalTree(groups=input_groups),
            output_tree=CanonicalTree(groups=output_groups),
            relationship_tree=CanonicalTree(groups=[], relationship_map=relationship),
        )
