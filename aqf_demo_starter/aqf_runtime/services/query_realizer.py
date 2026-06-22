from __future__ import annotations
from typing import Any, Dict, List

from aqf_runtime.models.forms import AdaptiveForm
from aqf_runtime.models.query import Predicate, QueryExplanation, QueryPlan


class QueryRealizer:
    def build_plan(self, selected: List[Dict[str, Any]]) -> QueryPlan:
        predicates = []
        for item in selected:
            predicates.append(
                Predicate(
                    field_id=item["field_id"],
                    path=item["path"],
                    operator=item.get("operator", "="),
                    value=item.get("value"),
                )
            )
        return QueryPlan(predicates=predicates, select_fields=[i["field_id"] for i in selected])

    def generate_aql(self, plan: QueryPlan) -> str:
        if not plan.predicates:
            return "SELECT * FROM EHR e"
        clauses = []
        for idx, p in enumerate(plan.predicates):
            param = f"$p{idx}"
            if p.operator.lower() == "contains":
                clause = f"e/{p.path} CONTAINS {param}"
            else:
                clause = f"e/{p.path} {p.operator} {param}"
            clauses.append(clause)
        where = " AND ".join(clauses)
        return f"SELECT e FROM EHR e WHERE {where}"

    def explain(self, selected: List[Dict[str, Any]]) -> QueryExplanation:
        plan = self.build_plan(selected)
        return QueryExplanation(
            selected_fields=selected,
            predicates=[p.to_dict() for p in plan.predicates],
            generated_aql=self.generate_aql(plan),
            notes=["Generated from AQF runtime query realizer."],
        )
