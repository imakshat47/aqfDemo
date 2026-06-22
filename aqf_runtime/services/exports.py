
import json
from pathlib import Path

class ExportManager:
    def export_json(self, payload, out_file):
        out = Path(out_file)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return str(out)
