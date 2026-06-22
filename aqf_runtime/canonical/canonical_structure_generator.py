from __future__ import annotations
from collections import defaultdict
from uuid import uuid4
from aqf_runtime.models import CanonicalField, CanonicalForm, CanonicalGroup, SchemaGraph

class CanonicalStructureGenerator:
    def build(self, graph: SchemaGraph) -> CanonicalForm:
        groups_by_root = defaultdict(list)
        for node in graph.nodes.values():
            if node.node_type == "root":
                continue
            root = node.path.split(" / ", 1)[0] if " / " in node.path else "root"
            groups_by_root[root].append(CanonicalField(
                field_id=node.node_id,
                label=node.concept_name,
                path=node.path,
                datatype=node.datatype,
                queriability=node.queriability,
                allowed_operators=self._operators_for_datatype(node.datatype),
                distinct_values=node.distinct_values[:20],
                recommended_widget=node.recommended_widget,
                metadata={"node_type": node.node_type, "repository_types": node.repository_types, "archetype_ids": node.archetype_ids},
            ))
        groups = []
        relationship_tree = []
        for root, fields in sorted(groups_by_root.items()):
            fields = sorted(fields, key=lambda x: x.queriability, reverse=True)
            groups.append(CanonicalGroup(group_id=f"group_{root.replace(' ', '_')}", label=root.replace("_", " ").title(), fields=fields))
            relationship_tree.append({"source": f"group_{root.replace(' ', '_')}", "target_count": len(fields), "edge_type": "group_contains_fields"})
        return CanonicalForm(
            form_id=str(uuid4()),
            source_tree_id="schema_graph",
            form_group="AQF Canonical Form",
            root_canonical_id="aqf_root",
            groups=groups,
            relationship_tree=relationship_tree,
            form_queriability=sum(f.queriability for g in groups for f in g.fields),
            element_count=sum(len(g.fields) for g in groups),
            subgroup_count=len(groups),
            max_depth=1 if groups else 0,
        )

    def _operators_for_datatype(self, datatype: str):
        dt = (datatype or "").upper()
        if "DATE" in dt:
            return ["=", "!=", "before", "after", "between"]
        if "BOOLEAN" in dt:
            return ["="]
        if dt in {"DV_COUNT", "DV_QUANTITY", "DV_DURATION", "DV_PROPORTION"}:
            return ["=", "!=", ">", ">=", "<", "<=", "between"]
        return ["=", "!=", "contains", "starts_with"]
