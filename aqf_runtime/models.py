from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class RecordUnit:
    unit_id: str
    repository_type: str
    source_file: str
    json_type: str
    archetype_id: Optional[str]
    composition_name: Optional[str]
    subject_id: Optional[str]
    ehr_id: Optional[str]
    raw_document: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    def to_dict(self): return asdict(self)

@dataclass
class SchemaNode:
    node_id: str
    concept_name: str
    path: str
    datatype: str
    node_type: str
    repository_types: List[str] = field(default_factory=list)
    archetype_ids: List[str] = field(default_factory=list)
    occurrence_count: int = 0
    record_count: int = 0
    coverage_global: float = 0.0
    coverage_local: float = 0.0
    coverage: float = 0.0
    diversity: float = 0.0
    local_utility: float = 0.0
    queriability: float = 0.0
    distinct_count: int = 0
    distinct_values: List[Any] = field(default_factory=list)
    total_records: int = 0
    value_examples: List[Any] = field(default_factory=list)
    recommended_widget: str = "text_input"
    child_count: int = 0
    def to_dict(self): return asdict(self)

@dataclass
class SchemaEdge:
    source: str
    target: str
    edge_type: str
    weight: float = 0.0
    count: int = 0
    containment_connectivity: float = 0.0
    cooccurrence_connectivity: float = 0.0
    structural_connectivity: float = 0.0
    def to_dict(self): return asdict(self)

@dataclass
class SchemaGraph:
    nodes: Dict[str, SchemaNode] = field(default_factory=dict)
    edges: List[SchemaEdge] = field(default_factory=list)
    record_count: int = 0
    repository_types: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    def to_dict(self):
        return {
            "record_count": self.record_count,
            "repository_types": self.repository_types,
            "metadata": self.metadata,
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "edges": [e.to_dict() for e in self.edges],
        }

@dataclass
class CanonicalField:
    field_id: str
    label: str
    path: str
    datatype: str
    queriability: float
    allowed_operators: List[str] = field(default_factory=list)
    distinct_values: List[Any] = field(default_factory=list)
    recommended_widget: str = "text_input"
    metadata: Dict[str, Any] = field(default_factory=dict)
    def to_dict(self): return asdict(self)

@dataclass
class CanonicalGroup:
    group_id: str
    label: str
    fields: List[CanonicalField] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    def to_dict(self):
        return {"group_id": self.group_id, "label": self.label, "fields": [f.to_dict() for f in self.fields], "metadata": self.metadata}

@dataclass
class CanonicalForm:
    form_id: str
    source_tree_id: str
    form_group: str
    root_canonical_id: str
    groups: List[CanonicalGroup] = field(default_factory=list)
    relationship_tree: List[Dict[str, Any]] = field(default_factory=list)
    form_queriability: float = 0.0
    element_count: int = 0
    subgroup_count: int = 0
    max_depth: int = 0
    def to_dict(self):
        return {
            "form_id": self.form_id,
            "source_tree_id": self.source_tree_id,
            "form_group": self.form_group,
            "root_canonical_id": self.root_canonical_id,
            "groups": [g.to_dict() for g in self.groups],
            "relationship_tree": self.relationship_tree,
            "form_queriability": self.form_queriability,
            "element_count": self.element_count,
            "subgroup_count": self.subgroup_count,
            "max_depth": self.max_depth,
        }

@dataclass
class FormElement:
    field_id: str
    label: str
    path: str
    datatype: str
    allowed_operators: List[str]
    queriability: float
    role: str = "filter"
    distinct_values: List[Any] = field(default_factory=list)
    recommended_widget: str = "text_input"
    metadata: Dict[str, Any] = field(default_factory=dict)
    def to_dict(self): return asdict(self)

@dataclass
class AdaptiveForm:
    form_id: str
    title: str
    complexity: float
    elements: List[FormElement] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    def to_dict(self):
        return {"form_id": self.form_id, "title": self.title, "complexity": self.complexity, "elements": [e.to_dict() for e in self.elements], "metadata": self.metadata}
