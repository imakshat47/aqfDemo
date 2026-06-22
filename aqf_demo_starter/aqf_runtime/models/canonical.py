from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any


@dataclass
class CanonicalField:
    field_id: str
    label: str
    path: str
    datatype: str
    queriability: float
    allowed_operators: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CanonicalGroup:
    group_id: str
    label: str
    fields: List[CanonicalField] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "group_id": self.group_id,
            "label": self.label,
            "fields": [f.to_dict() for f in self.fields],
            "metadata": self.metadata,
        }


@dataclass
class CanonicalTree:
    groups: List[CanonicalGroup] = field(default_factory=list)
    relationship_map: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "groups": [g.to_dict() for g in self.groups],
            "relationship_map": self.relationship_map,
        }


@dataclass
class CanonicalForm:
    input_tree: CanonicalTree
    output_tree: CanonicalTree
    relationship_tree: CanonicalTree

    def to_dict(self) -> Dict[str, Any]:
        return {
            "input_tree": self.input_tree.to_dict(),
            "output_tree": self.output_tree.to_dict(),
            "relationship_tree": self.relationship_tree.to_dict(),
        }
