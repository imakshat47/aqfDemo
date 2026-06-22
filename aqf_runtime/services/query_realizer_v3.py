
class QueryRealizerV3:
    def explain(self, predicates):
        clauses = []
        for i,p in enumerate(predicates):
            clauses.append(f"e/{p['path']} {p['operator']} $p{i}")
        aql = "SELECT e FROM EHR e"
        if clauses:
            aql += " WHERE " + " AND ".join(clauses)
        return {
            'predicates': predicates,
            'aql': aql
        }
