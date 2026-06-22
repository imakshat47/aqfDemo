from __future__ import annotations
import json
from pathlib import Path
from typing import List
from aqf_runtime.adapters.openehr_adapter import OpenEHRAdapter
from aqf_runtime.models import RecordUnit

class RepositoryNormalizer:
    def __init__(self):
        self.adapters = [OpenEHRAdapter()]
    def load_folder(self, folder: str | Path) -> List[RecordUnit]:
        folder = Path(folder)
        if not folder.exists():
            raise FileNotFoundError(f"Input folder not found: {folder}")
        units: List[RecordUnit] = []
        for path in sorted(folder.rglob("*.json")):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                continue
            docs = payload if isinstance(payload, list) else [payload] if isinstance(payload, dict) else []
            for doc in docs:
                adapter = self._find_adapter(doc)
                if adapter is None:
                    continue
                try:
                    units.extend(adapter.normalize(doc, path))
                except Exception:
                    continue
        return units
    def _find_adapter(self, document):
        for adapter in self.adapters:
            try:
                if adapter.can_handle(document):
                    return adapter
            except Exception:
                continue
        return None
