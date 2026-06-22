from __future__ import annotations
from typing import Iterable, Set

CLINICAL_LABEL_BLACKLIST = {
    "components", "structure", "tree", "items", "context", "protocol", "description",
    "data", "content", "unknown"
}

class ClinicalFilter:
    def __init__(self, blacklist: Set[str] | None = None):
        self.blacklist = {x.lower() for x in (blacklist or CLINICAL_LABEL_BLACKLIST)}

    # def keep(self, node) -> bool:
    #     label = (node.concept_name or "").strip().lower()
    #     node_type = (node.node_type or "").strip().lower()
    #     if label in self.blacklist:
    #         return False
    #     if node_type in {"root"}:
    #         return True
    #     if node.datatype == "unknown" and label in self.blacklist:
    #         return False
    #     return True
    
    def keep(self, node) -> bool:

        node_type = (node.node_type or "").lower()

        return node_type == "field"
