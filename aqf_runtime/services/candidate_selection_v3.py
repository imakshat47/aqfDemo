
class CandidateSelectionV3:
    def select(self, nodes, theta=0.10):
        if not nodes:
            return []
        maxscore = max(x['score'] for x in nodes)
        return [x for x in nodes if x['score'] >= theta * maxscore]
