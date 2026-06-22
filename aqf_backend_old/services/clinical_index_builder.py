from __future__ import annotations
import json, re
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

from aqf_backend.services.record_loader import SemanticRecord, _is_noise_value

def normalize_name(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()

def infer_widget(datatype: str, distinct_count: int) -> str:
    dt = (datatype or "").upper()
    if "DATE" in dt:
        return "date_picker"
    if "BOOLEAN" in dt:
        return "checkbox"
    if dt in {"DV_COUNT", "DV_QUANTITY", "DV_DURATION", "DV_PROPORTION"}:
        return "number_input"
    if distinct_count == 0:
        return "text_input"
    if distinct_count <= 20:
        return "dropdown"
    if distinct_count <= 100:
        return "autocomplete"
    return "text_input"

def human_ops(datatype: str) -> List[str]:
    dt = (datatype or "").upper()
    if "DATE" in dt:
        return ["is", "is not", "greater than", "less than", "between"]
    if "BOOLEAN" in dt:
        return ["is", "is not"]
    if dt in {"DV_COUNT", "DV_QUANTITY", "DV_DURATION", "DV_PROPORTION"}:
        return ["is", "is not", "greater than", "less than", "between"]
    return ["is", "is not", "contains", "starts with"]

class ClinicalIndexBuilder:
    def __init__(self, max_examples: int = 12):
        self.max_examples = max_examples

    def build(self, field_statistics_file: str | Path, output_file: str | Path, semantic_records: List[SemanticRecord] | None = None, queryable_fields_output: str | Path | None = None) -> Dict[str, Any]:
        stats = json.loads(Path(field_statistics_file).read_text(encoding="utf-8"))
        semantic_records = semantic_records or []
        index: Dict[str, Dict[str, Any]] = {}
        catalog: Dict[str, Dict[str, Any]] = defaultdict(lambda: {"field_count": 0, "sections": defaultdict(list)})

        for row in stats:
            concept = row.get("concept_name")
            if not concept or not self._is_queryable(row):
                continue
            path = str(row.get("path") or "")
            parts = [p.strip() for p in path.split(" / ") if p.strip()]
            composition = parts[0] if parts else str(row.get("composition") or "Unknown")
            section = parts[1] if len(parts) > 1 else composition
            aliases = self._aliases(concept, path, composition, section)
            examples = self._gather_examples(aliases, semantic_records, row.get("distinct_values") or [])
            distinct_count = len(examples)
            widget = row.get("recommended_widget") or infer_widget(str(row.get("datatype") or ""), distinct_count)
            entry = {
                "concept_name": concept,
                "node_id": row.get("node_id"),
                "composition": composition,
                "section": section,
                "path": path,
                "datatype": row.get("datatype", "unknown"),
                "widget": widget,
                "recommended_widget": widget,
                "recommended_operators": row.get("recommended_operators") or human_ops(str(row.get("datatype") or "")),
                "coverage": row.get("coverage"),
                "coverage_global": row.get("coverage_global"),
                "coverage_local": row.get("coverage_local"),
                "distinct_count": distinct_count,
                "examples": examples[: self.max_examples],
                "aliases": aliases,
                "node_type": row.get("node_type", ""),
            }
            index[concept] = entry
            catalog[composition]["field_count"] += 1
            catalog[composition]["sections"][section].append({
                "field_id": row.get("node_id"),
                "concept_name": concept,
                "path": path,
                "datatype": row.get("datatype", "unknown"),
                "recommended_widget": widget,
                "recommended_operators": entry["recommended_operators"],
                "coverage": row.get("coverage"),
                "coverage_local": row.get("coverage_local"),
                "distinct_count": distinct_count,
                "examples": examples[: self.max_examples],
            })

        compositions = []
        for comp_name, comp_data in sorted(catalog.items(), key=lambda kv: kv[0].lower()):
            sections = []
            for sec_name, fields in sorted(comp_data["sections"].items(), key=lambda kv: kv[0].lower()):
                fields = sorted(fields, key=lambda f: (f.get("distinct_count", 0) > 0, f.get("coverage_local") or f.get("coverage") or 0), reverse=True)
                sections.append({"key": f"{comp_name}||{sec_name}", "label": sec_name, "fields": fields})
            compositions.append({"name": comp_name, "field_count": comp_data["field_count"], "sections": sections})

        payload = {"total_fields": len(index), "fields": index}
        out = Path(output_file)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        if queryable_fields_output is not None:
            q = Path(queryable_fields_output)
            q.parent.mkdir(parents=True, exist_ok=True)
            q.write_text(json.dumps({"compositions": compositions}, indent=2, ensure_ascii=False), encoding="utf-8")
        return payload

    def _is_queryable(self, row: Dict[str, Any]) -> bool:
        node_type = str(row.get("node_type") or "")
        concept = str(row.get("concept_name") or "").lower()
        if node_type == "root" or concept in {"components", "tree", "structure", "data"}:
            return False
        return node_type in {"leaf", "substructure", "section"} or int(row.get("distinct_count") or 0) > 0

    def _aliases(self, concept: str, path: str, composition: str, section: str) -> List[str]:
        raw = {concept, composition, section, path}
        for text in list(raw):
            for part in re.split(r"[/|>:]+", text or ""):
                part = part.strip()
                if part:
                    raw.add(part)
        cleaned = []
        for a in raw:
            n = normalize_name(a)
            if not n or n in {"admin entry", "evaluation", "action", "observation", "instruction", "components", "tree", "structure", "data"}:
                continue
            if n not in cleaned:
                cleaned.append(n)
        return cleaned

    def _gather_examples(self, aliases: List[str], semantic_records: List[SemanticRecord], fallback_examples: List[Any]) -> List[str]:
        examples: List[str] = []
        for v in fallback_examples:
            t = str(v).strip()
            if t and not _is_noise_value(t) and t not in examples:
                examples.append(t)
        alias_set = set(aliases)
        for rec in semantic_records:
            for label, values in rec.semantic_map.items():
                if normalize_name(label) in alias_set:
                    for v in values:
                        t = str(v).strip()
                        if t and not _is_noise_value(t) and t not in examples:
                            examples.append(t)
                        if len(examples) >= self.max_examples:
                            return examples
        return examples
