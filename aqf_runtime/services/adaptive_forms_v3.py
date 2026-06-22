
class AdaptiveFormGeneratorV3:
    def generate(self, fields, budget=53):
        fields = sorted(fields, key=lambda x: x.get('score',0), reverse=True)
        return {
            'complexity': min(len(fields), budget),
            'elements': fields[:budget]
        }
