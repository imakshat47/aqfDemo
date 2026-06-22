
from collections import defaultdict

class SchemaGraphBuilderV3:
    def extract_paths(self, record, prefix="", paths=None):
        if paths is None:
            paths = []
        if isinstance(record, dict):
            for k,v in record.items():
                p = f"{prefix}.{k}" if prefix else k
                paths.append(p)
                self.extract_paths(v, p, paths)
        return paths

    def build_cooccurrence(self, records):
        co = defaultdict(int)
        for r in records:
            paths = set(self.extract_paths(r))
            for a in paths:
                for b in paths:
                    if a < b:
                        co[(a,b)] += 1
        return dict(co)
