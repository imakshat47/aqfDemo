
class QueriabilityEngineV3:
    def local_utility(self, coverage, diversity):
        return coverage * diversity

    def structural_connectivity(self, containment, cooccurrence, lam=0.25):
        return lam * containment + (1-lam) * cooccurrence

    def score(self, coverage, diversity, neighborhood=0.0, mu=0.25):
        return self.local_utility(coverage, diversity) + mu * neighborhood
