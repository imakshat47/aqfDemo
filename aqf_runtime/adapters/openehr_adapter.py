from __future__ import annotations
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional
from aqf_runtime.adapters.base_adapter import BaseRepositoryAdapter
from aqf_runtime.models import RecordUnit

def _get_path(obj: Any, path: List[str], default=None):
    cur = obj
    for part in path:
        if isinstance(cur, dict):
            cur = cur.get(part)
        else:
            return default
        if cur is None:
            return default
    return cur

def _looks_like_composition(doc: Dict[str, Any]) -> bool:
    arch = doc.get("archetype_node_id")
    typ = doc.get("type") or doc.get("_type")
    if isinstance(arch, str) and "COMPOSITION" in arch: return True
    if isinstance(typ, str) and typ.upper() == "COMPOSITION": return True
    if "content" in doc and isinstance(doc.get("name"), (dict, str)): return True
    if "versions" in doc and isinstance(doc.get("versions"), dict):
        data = _get_path(doc, ["versions", "data"], {})
        return isinstance(data, dict) and "content" in data
    return False

def _looks_like_ehr_index(doc: Dict[str, Any]) -> bool:
    return "ehr_id" in doc and isinstance(doc.get("compositions"), list)

def _extract_archetype_id(doc: Dict[str, Any]) -> Optional[str]:
    if isinstance(doc.get("archetype_node_id"), str): return doc["archetype_node_id"]
    aid = _get_path(doc, ["archetype_details", "archetype_id", "value"])
    return aid if isinstance(aid, str) else None

def _extract_name(doc: Dict[str, Any]) -> Optional[str]:
    name = doc.get("name")
    if isinstance(name, dict): return name.get("value")
    if isinstance(name, str): return name
    return None

def _extract_ehr_id(doc: Dict[str, Any]) -> Optional[str]:
    for key in ("ehr_id", "ehrId"):
        val = doc.get(key)
        if isinstance(val, str): return val
        if isinstance(val, dict):
            v = val.get("value") or val.get("id")
            if v: return str(v)
    ehr = doc.get("ehr")
    if isinstance(ehr, dict): return _extract_ehr_id(ehr)
    return None

def _extract_subject_id(doc: Dict[str, Any]) -> Optional[str]:
    for key in ("subject_id", "subjectId", "patient_id", "patientId"):
        val = doc.get(key)
        if isinstance(val, str): return val
    subject = doc.get("subject")
    if isinstance(subject, dict):
        ext = subject.get("external_ref")
        if isinstance(ext, dict):
            ref_id = ext.get("id")
            if isinstance(ref_id, dict): return ref_id.get("value")
            if isinstance(ref_id, str): return ref_id
    return None

def _make_unit_id(source_file: Path, index: int, archetype_id: Optional[str]) -> str:
    raw = f"{source_file}|{index}|{archetype_id or ''}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()

class OpenEHRAdapter(BaseRepositoryAdapter):
    name = "openehr"
    def can_handle(self, document: Dict[str, Any]) -> bool:
        return _looks_like_composition(document) or _looks_like_ehr_index(document)
    def normalize(self, document: Dict[str, Any], source_file: Path) -> List[RecordUnit]:
        if _looks_like_ehr_index(document):
            return [self._normalize_ehr_index(document, source_file)]
        if isinstance(document.get("versions"), dict):
            comp = _get_path(document, ["versions", "data"], None)
            if isinstance(comp, dict) and "content" in comp:
                return [self._normalize_composition(comp, source_file, "versioned_composition")]
        if _looks_like_composition(document):
            return [self._normalize_composition(document, source_file, "composition")]
        return []
    def _normalize_composition(self, doc: Dict[str, Any], source_file: Path, json_type: str) -> RecordUnit:
        archetype_id = _extract_archetype_id(doc)
        return RecordUnit(
            unit_id=_make_unit_id(source_file, 0, archetype_id),
            repository_type="openehr",
            source_file=str(source_file),
            json_type=json_type,
            archetype_id=archetype_id,
            composition_name=_extract_name(doc),
            subject_id=_extract_subject_id(doc),
            ehr_id=_extract_ehr_id(doc),
            raw_document=doc,
            metadata={"root_keys": sorted(list(doc.keys()))[:50]},
        )
    def _normalize_ehr_index(self, doc: Dict[str, Any], source_file: Path) -> RecordUnit:
        ehr_id = _extract_ehr_id(doc)
        return RecordUnit(
            unit_id=_make_unit_id(source_file, 0, "EHR_INDEX"),
            repository_type="openehr",
            source_file=str(source_file),
            json_type="ehr_index_reference",
            archetype_id="EHR_INDEX_REFERENCE",
            composition_name="EHR Index Reference",
            subject_id=_extract_subject_id(doc),
            ehr_id=ehr_id,
            raw_document=doc,
            metadata={"composition_count": len(doc.get("compositions", [])) if isinstance(doc.get("compositions"), list) else 0},
        )
