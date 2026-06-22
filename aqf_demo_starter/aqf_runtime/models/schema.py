from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any


@dataclass
class SchemaNode:
    node_id: str
    label: str
    path: str
    node_type: str  # section | substructure | leaf
    datatype: str = "unknown"
    coverage: float = 0.0
    diversity: float = 0.0
    queriability: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SchemaEdge:
    source: str
    target: str
    edge_type: str  # containment | cooccurrence
    weight: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SchemaGraph:
    nodes: Dict[str, SchemaNode] = field(default_factory=dict)
    edges: List[SchemaEdge] = field(default_factory=list)
    record_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "record_count": self.record_count,
            "nodes": {k: v.to_dict() for k, v in self.nodes.items()},
            "edges": [e.to_dict() for e in self.edges],
        }
