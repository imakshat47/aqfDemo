from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

IGNORE_KEYS = {
    "uid", "external_ref", "defining_code", "terminology_id", "code_string",
    "archetype_details", "language", "territory", "category", "composer",
    "lifecycle_state", "owner_id", "versions", "commit_audit", "time_created",
    "encoding", "subject", "time", "context", "protocol", "instruction_details",
    "workflow_id", "feeder_audit", "other_context",
}

NOISE_VALUES = {
    "", "unknown", "none", "null", "n/a", "na", "not applicable",
}

def _to_text(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        t = value.strip()
        return t or None
    if isinstance(value, dict):
        if "value" in value:
            return _to_text(value["value"])
        if "id" in value:
            return _to_text(value["id"])
    return None

def _is_noise_value(value: Any) -> bool:
    text = _to_text(value)
    if text is None:
        return True
    norm = re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()
    if not norm or norm in NOISE_VALUES:
        return True
    if text.endswith(".json") or re.match(r"^[a-zA-Z]:[\\/]", text):
        return True
    return False

def _extract_label(obj: Dict[str, Any], fallback: Optional[str] = None) -> Optional[str]:
    name = obj.get("name")
    if isinstance(name, dict):
        t = _to_text(name.get("value")) or _to_text(name.get("name"))
        if t:
            return t
    elif isinstance(name, str):
        t = name.strip()
        if t:
            return t
    arch = obj.get("archetype_node_id")
    if isinstance(arch, str) and arch and not arch.startswith("at"):
        return fallback or arch
    return fallback

def _extract_scalar_value(obj: Dict[str, Any]) -> Optional[str]:
    value = obj.get("value")
    if isinstance(value, dict):
        return _to_text(value.get("value")) or _to_text(value)
    return _to_text(value)

@dataclass
class SemanticRecord:
    source_file: str
    raw: Dict[str, Any]
    semantic_map: Dict[str, List[str]] = field(default_factory=dict)
    semantic_text: str = ""

class RecordLoader:
    def __init__(self):
        self._raw_cache: List[Dict[str, Any]] | None = None
        self._semantic_cache: List[SemanticRecord] | None = None

    def load_dataset(self, dataset_dir: str | Path) -> List[Dict[str, Any]]:
        if self._raw_cache is not None:
            return self._raw_cache
        dataset_dir = Path(dataset_dir)
        records: List[Dict[str, Any]] = []
        for file_path in sorted(dataset_dir.rglob("*.json")):
            try:
                payload = json.loads(file_path.read_text(encoding="utf-8"))
            except Exception as exc:
                print(f"[AQF] Failed loading {file_path}: {exc}")
                continue
            docs = payload if isinstance(payload, list) else [payload] if isinstance(payload, dict) else []
            for doc in docs:
                if isinstance(doc, dict):
                    doc["_source_file"] = str(file_path)
                    records.append(doc)
        self._raw_cache = records
        return records

    def load_semantic_records(self, dataset_dir: str | Path) -> List[SemanticRecord]:
        if self._semantic_cache is not None:
            return self._semantic_cache
        semantic_records: List[SemanticRecord] = []
        for raw in self.load_dataset(dataset_dir):
            semantic_map = self.extract_semantic_map(raw)
            semantic_text = self.build_semantic_text(raw, semantic_map)
            semantic_records.append(SemanticRecord(str(raw.get("_source_file", "")), raw, semantic_map, semantic_text))
        self._semantic_cache = semantic_records
        return semantic_records

    def extract_semantic_map(self, obj: Any) -> Dict[str, List[str]]:
        semantic: Dict[str, List[str]] = {}

        def add(label: Optional[str], value: Any):
            if not label:
                return
            text = _to_text(value)
            if text is None or _is_noise_value(text):
                return
            if _is_noise_value(label):
                return
            norm_label = re.sub(r"[^a-z0-9]+", " ", label.lower()).strip()
            norm_text = re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()
            if not norm_text or norm_text == norm_label:
                return
            semantic.setdefault(label, [])
            if text not in semantic[label]:
                semantic[label].append(text)

        def walk(node: Any, fallback_label: Optional[str] = None):
            if isinstance(node, dict):
                label = _extract_label(node, fallback_label)
                scalar = _extract_scalar_value(node)
                if label and scalar is not None:
                    add(label, scalar)
                for key, value in node.items():
                    if key.startswith("_"):
                        continue
                    if key in IGNORE_KEYS:
                        continue
                    if isinstance(value, (dict, list)):
                        walk(value, label)
                    else:
                        if label and key not in {"type", "archetype_node_id", "null_flavour"}:
                            add(label, value)
            elif isinstance(node, list):
                for item in node:
                    walk(item, fallback_label)

        walk(obj)
        return semantic

    def build_semantic_text(self, raw: Dict[str, Any], semantic_map: Dict[str, List[str]]) -> str:
        chunks: List[str] = []
        for label, values in semantic_map.items():
            if _is_noise_value(label):
                continue
            chunks.append(label)
            chunks.extend([v for v in values if not _is_noise_value(v)])
        return " ".join(chunks).lower()

    @staticmethod
    def normalize_name(text: str) -> str:
        return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()
