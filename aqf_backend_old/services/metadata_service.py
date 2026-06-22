from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional

from aqf_backend.config import (
    ADAPTIVE_FORM_FILE,
    CLINICAL_INDEX_FILE,
    DATASET_DIR,
    FIELD_STATISTICS_FILE,
    QUERYABLE_FIELDS_FILE,
)
from aqf_backend.models import QueryComposition, QueryField, QueryFormsResponse, QuerySection
from aqf_backend.services.clinical_index_builder import ClinicalIndexBuilder, infer_widget, normalize_name
from aqf_backend.services.record_loader import RecordLoader, SemanticRecord

class MetadataService:
    def __init__(self, output_dir: str | Path | None = None, dataset_dir: str | Path | None = None):
        self.output_dir = Path(output_dir or CLINICAL_INDEX_FILE.parent)
        self.dataset_dir = Path(dataset_dir or DATASET_DIR)
        self.field_statistics_file = Path(FIELD_STATISTICS_FILE)
        self.clinical_index_file = Path(CLINICAL_INDEX_FILE)
        self.queryable_fields_file = Path(QUERYABLE_FIELDS_FILE)
        self.adaptive_form_file = Path(ADAPTIVE_FORM_FILE)
        self._field_stats: List[Dict[str, Any]] | None = None
        self._semantic_records: List[SemanticRecord] | None = None
        self._clinical_index: Dict[str, Any] | None = None
        self._forms: QueryFormsResponse | None = None
        self._lookup: Dict[str, Dict[str, Any]] | None = None
        self._adaptive_form: Dict[str, Any] | None = None

    def load(self) -> None:
        self.ensure_artifacts()

    def ensure_artifacts(self) -> None:
        if not self.field_statistics_file.exists():
            raise FileNotFoundError(f"Missing runtime artifact: {self.field_statistics_file}")
        loader = RecordLoader()
        self._semantic_records = loader.load_semantic_records(self.dataset_dir)
        builder = ClinicalIndexBuilder()
        payload = builder.build(
            self.field_statistics_file,
            self.clinical_index_file,
            semantic_records=self._semantic_records,
            queryable_fields_output=self.queryable_fields_file,
        )
        self._clinical_index = payload["fields"]
        self._lookup = self._build_lookup()
        self._forms = self._build_forms()
        self._adaptive_form = self._load_json_if_exists(self.adaptive_form_file)

    @property
    def field_stats(self) -> List[Dict[str, Any]]:
        if self._field_stats is None:
            self._field_stats = json.loads(self.field_statistics_file.read_text(encoding="utf-8"))
        return self._field_stats

    @property
    def semantic_records(self) -> List[SemanticRecord]:
        if self._semantic_records is None:
            loader = RecordLoader()
            self._semantic_records = loader.load_semantic_records(self.dataset_dir)
        return self._semantic_records

    @property
    def clinical_index(self) -> Dict[str, Any]:
        if self._clinical_index is None:
            if self.clinical_index_file.exists():
                payload = json.loads(self.clinical_index_file.read_text(encoding="utf-8"))
                self._clinical_index = payload.get("fields", payload)
            else:
                self.ensure_artifacts()
        return self._clinical_index or {}

    @property
    def forms(self) -> QueryFormsResponse:
        if self._forms is None:
            self._forms = self._build_forms()
        return self._forms

    @property
    def adaptive_form(self) -> Dict[str, Any]:
        if self._adaptive_form is None:
            self._adaptive_form = self._load_json_if_exists(self.adaptive_form_file) or {}
        return self._adaptive_form or {}

    def _load_json_if_exists(self, file_path: Path) -> Dict[str, Any] | None:
        if not file_path.exists():
            return None
        return json.loads(file_path.read_text(encoding="utf-8"))

    def _build_lookup(self) -> Dict[str, Dict[str, Any]]:
        lookup: Dict[str, Dict[str, Any]] = {}
        for name, entry in self.clinical_index.items():
            lookup[normalize_name(name)] = entry
            for alias in entry.get("aliases", []):
                lookup[normalize_name(alias)] = entry
        return lookup

    def resolve_field_entry(self, field_name: str) -> Optional[Dict[str, Any]]:
        if self._lookup is None:
            self._lookup = self._build_lookup()
        norm = normalize_name(field_name)
        entry = self._lookup.get(norm)
        if entry:
            return entry
        for key, value in self._lookup.items():
            if norm and (norm in key or key in norm):
                return value
        return None

    def suggestions_for_field(self, field_name: str) -> List[Dict[str, Any]]:
        entry = self.resolve_field_entry(field_name)
        if not entry:
            return []
        examples = [str(v).strip() for v in entry.get("examples", []) if str(v).strip()]
        counts = Counter(examples)
        return [{"value": value, "count": count} for value, count in counts.most_common()]

    def _build_forms(self) -> QueryFormsResponse:
        if self.queryable_fields_file.exists():
            try:
                payload = json.loads(self.queryable_fields_file.read_text(encoding="utf-8"))
                if isinstance(payload, dict) and "compositions" in payload:
                    return self._forms_from_queryable_artifact(payload)
            except Exception:
                pass

        comp_map: Dict[str, Dict[str, Any]] = {}
        for row in self.field_stats:
            if not self._is_queryable_field(row):
                continue
            path = str(row.get("path") or "")
            parts = [p.strip() for p in path.split(" / ") if p.strip()]
            composition = parts[0] if parts else str(row.get("composition") or "Unknown")
            section = parts[1] if len(parts) > 1 else composition
            comp_bucket = comp_map.setdefault(composition, {"field_count": 0, "sections": {}})
            comp_bucket["field_count"] += 1
            sec_bucket = comp_bucket["sections"].setdefault(section, [])
            widget = row.get("recommended_widget") or infer_widget(str(row.get("datatype") or ""), int(row.get("distinct_count") or 0))
            field = QueryField(
                field_id=str(row.get("node_id") or row.get("field_id") or row.get("concept_name")),
                concept_name=str(row.get("concept_name") or ""),
                path=path,
                datatype=str(row.get("datatype") or "unknown"),
                recommended_widget=str(widget),
                recommended_operators=list(row.get("recommended_operators") or self._ops_for_datatype(str(row.get("datatype") or ""))),
                coverage=float(row.get("coverage") or 0.0),
                coverage_local=float(row.get("coverage_local") or row.get("coverage") or 0.0),
                distinct_count=int(row.get("distinct_count") or 0),
                examples=[str(v) for v in (row.get("distinct_values") or []) if str(v).strip()],
            )
            sec_bucket.append(field)
        compositions = []
        for comp_name, comp_data in sorted(comp_map.items(), key=lambda kv: kv[0].lower()):
            sections = []
            for sec_name, fields in sorted(comp_data["sections"].items(), key=lambda kv: kv[0].lower()):
                fields = sorted(fields, key=lambda f: (f.distinct_count > 0, f.coverage_local, f.coverage), reverse=True)
                sections.append(QuerySection(key=f"{comp_name}||{sec_name}", label=sec_name, fields=fields))
            compositions.append(QueryComposition(name=comp_name, field_count=comp_data["field_count"], sections=sections))
        return QueryFormsResponse(compositions=compositions)

    def _forms_from_queryable_artifact(self, payload: Dict[str, Any]) -> QueryFormsResponse:
        compositions: List[QueryComposition] = []
        for comp in payload.get("compositions", []):
            sections: List[QuerySection] = []
            for sec in comp.get("sections", []):
                fields: List[QueryField] = []
                for field in sec.get("fields", []):
                    fields.append(QueryField(
                        field_id=str(field.get("field_id") or field.get("node_id") or field.get("concept_name")),
                        concept_name=str(field.get("concept_name") or ""),
                        path=str(field.get("path") or ""),
                        datatype=str(field.get("datatype") or "unknown"),
                        recommended_widget=str(field.get("recommended_widget") or field.get("widget") or "text_input"),
                        recommended_operators=list(field.get("recommended_operators") or self._ops_for_datatype(str(field.get("datatype") or ""))),
                        coverage=float(field.get("coverage") or field.get("coverage_local") or 0.0),
                        coverage_local=float(field.get("coverage_local") or field.get("coverage") or 0.0),
                        distinct_count=int(field.get("distinct_count") or 0),
                        examples=[str(v) for v in (field.get("examples") or field.get("distinct_values") or []) if str(v).strip()],
                    ))
                sections.append(QuerySection(key=str(sec.get("key") or sec.get("label") or ""), label=str(sec.get("label") or ""), fields=fields))
            compositions.append(QueryComposition(name=str(comp.get("name") or ""), field_count=int(comp.get("field_count") or 0), sections=sections))
        return QueryFormsResponse(compositions=compositions)

    def _is_queryable_field(self, row: Dict[str, Any]) -> bool:
        node_type = str(row.get("node_type") or "")
        concept = str(row.get("concept_name") or "").lower()
        if node_type == "root" or concept in {"components", "tree", "structure", "data"}:
            return False
        return node_type in {"leaf", "substructure", "section"} or int(row.get("distinct_count") or 0) > 0

    def _ops_for_datatype(self, datatype: str) -> List[str]:
        dt = (datatype or "").upper()
        if "DATE" in dt:
            return ["is", "is not", "greater than", "less than", "between"]
        if "BOOLEAN" in dt:
            return ["is", "is not"]
        if dt in {"DV_COUNT", "DV_QUANTITY", "DV_DURATION", "DV_PROPORTION"}:
            return ["is", "is not", "greater than", "less than", "between"]
        return ["is", "is not", "contains", "starts with"]
