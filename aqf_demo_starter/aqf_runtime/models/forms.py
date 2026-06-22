from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any


@dataclass
class FormElement:
    field_id: str
    label: str
    path: str
    datatype: str
    allowed_operators: List[str]
    queriability: float
    role: str = "filter"  # filter | projection | ordering | aggregation
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AdaptiveForm:
    form_id: str
    title: str
    complexity: float
    elements: List[FormElement] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "form_id": self.form_id,
            "title": self.title,
            "complexity": self.complexity,
            "elements": [e.to_dict() for e in self.elements],
            "metadata": self.metadata,
        }
