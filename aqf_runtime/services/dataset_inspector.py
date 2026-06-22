
import json
from pathlib import Path

class DatasetInspector:
    def inspect(self, dataset_path):
        data = json.loads(Path(dataset_path).read_text(encoding="utf-8"))
        records = data["records"] if isinstance(data, dict) and "records" in data else data
        fields = set()

        def walk(obj, prefix=""):
            if isinstance(obj, dict):
                for k,v in obj.items():
                    p = f"{prefix}.{k}" if prefix else k
                    fields.add(p)
                    walk(v,p)

        for r in records:
            walk(r)

        return {
            "records": len(records),
            "fields": len(fields),
            "paths": sorted(fields)
        }
