
class AQFMetrics:
    def complexity(self, adaptive_form):
        return adaptive_form.get("complexity", 0)

    def field_count(self, adaptive_form):
        return len(adaptive_form.get("elements", []))

    def operator_burden(self, adaptive_form):
        total = 0
        for e in adaptive_form.get("elements", []):
            total += len(e.get("allowed_operators", []))
        return total
