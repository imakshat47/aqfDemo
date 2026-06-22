from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from aqf_backend.models import QueryFormsResponse
from aqf_backend.services.metadata_service import MetadataService

router = APIRouter(tags=["forms"])

@router.get("/forms", response_model=QueryFormsResponse)
def list_forms():
    svc = MetadataService()
    svc.load()
    return svc.forms

@router.get("/forms/adaptive")
def get_adaptive_form():
    svc = MetadataService()
    svc.load()
    return svc.adaptive_form

@router.get("/forms/{composition_name}")
def get_form_by_composition(composition_name: str):
    svc = MetadataService()
    svc.load()
    for comp in svc.forms.compositions:
        if comp.name.lower() == composition_name.lower():
            return comp
    raise HTTPException(status_code=404, detail=f"Composition not found: {composition_name}")

@router.get("/query/suggestions/{field_name}")
def get_suggestions(field_name: str):
    svc = MetadataService()
    svc.load()
    return {"field_name": field_name, "suggestions": svc.suggestions_for_field(field_name)}
