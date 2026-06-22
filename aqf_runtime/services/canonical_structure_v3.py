
class CanonicalStructureV3:
    def build(self, fields):
        groups = {}
        for f in fields:
            root = f['path'].split('.')[0]
            groups.setdefault(root, []).append(f)
        return groups
