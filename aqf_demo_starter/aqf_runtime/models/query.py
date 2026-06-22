from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any


@dataclass
class Predicate:
    field_id: str
    path: str
    operator: str
    value: Any

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class QueryPlan:
    predicates: List[Predicate] = field(default_factory=list)
    select_fields: List[str] = field(default_factory=list)
    sort_fields: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "predicates": [p.to_dict() for p in self.predicates],
            "select_fields": self.select_fields,
            "sort_fields": self.sort_fields,
        }


@dataclass
class QueryExplanation:
    selected_fields: List[Dict[str, Any]] = field(default_factory=list)
    predicates: List[Dict[str, Any]] = field(default_factory=list)
    generated_aql: str = ""
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
