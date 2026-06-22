from __future__ import annotations
from typing import List

from aqf_runtime.models.canonical import CanonicalForm


class OperatorAwareness:
    def operators_for_datatype(self, datatype: str) -> List[str]:
        mapping = {
            "numeric": ["=", "!=", ">", ">=", "<", "<="],
            "boolean": ["="],
            "text": ["=", "!=", "contains", "starts_with"],
            "unknown": ["="],
        }
        return mapping.get(datatype, ["="])

    def annotate(self, canonical_form: CanonicalForm) -> CanonicalForm:
        for tree in [canonical_form.input_tree, canonical_form.output_tree]:
            for group in tree.groups:
                for field in group.fields:
                    field.allowed_operators = self.operators_for_datatype(field.datatype)
                    field.metadata["operator_awareness"] = True
        return canonical_form
