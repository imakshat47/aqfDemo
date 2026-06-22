from __future__ import annotations
from typing import List
from uuid import uuid4

from aqf_runtime.models.canonical import CanonicalForm
from aqf_runtime.models.forms import AdaptiveForm, FormElement


class AdaptiveFormGenerator:
    def generate(self, canonical_form: CanonicalForm, complexity_budget: float = 53.0) -> AdaptiveForm:
        elements: List[FormElement] = []
        complexity = 0.0

        for group in canonical_form.input_tree.groups:
            for field in sorted(group.fields, key=lambda f: f.queriability, reverse=True):
                if complexity + 1 > complexity_budget:
                    break
                elements.append(
                    FormElement(
                        field_id=field.field_id,
                        label=field.label,
                        path=field.path,
                        datatype=field.datatype,
                        allowed_operators=field.allowed_operators or ["="],
                        queriability=field.queriability,
                        role="filter",
                        metadata=field.metadata,
                    )
                )
                complexity += 1

        return AdaptiveForm(
            form_id=str(uuid4()),
            title="AQF Adaptive Query Form",
            complexity=complexity,
            elements=elements,
            metadata={"complexity_budget": complexity_budget},
        )
