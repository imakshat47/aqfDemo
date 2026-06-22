from __future__ import annotations

from typing import Any, Dict, List
from pydantic import BaseModel, Field

class QueryCondition(BaseModel):
    field: str
    operator: str
    value: Any = None

class QueryRequest(BaseModel):
    conditions: List[QueryCondition] = Field(default_factory=list)
    output_fields: List[str] = Field(default_factory=list)

class QueryRow(BaseModel):
    source_file: str
    fields: Dict[str, Any] = Field(default_factory=dict)

class QueryResponse(BaseModel):
    total_matches: int
    rows: List[QueryRow]
    applied_conditions: List[QueryCondition] = Field(default_factory=list)
    output_fields: List[str] = Field(default_factory=list)

class QueryFieldSuggestion(BaseModel):
    value: str
    count: int = 0

class QueryField(BaseModel):
    field_id: str
    concept_name: str
    path: str
    datatype: str = "unknown"
    recommended_widget: str = "text_input"
    recommended_operators: List[str] = Field(default_factory=list)
    coverage: float = 0.0
    coverage_local: float = 0.0
    distinct_count: int = 0
    examples: List[str] = Field(default_factory=list)

class QuerySection(BaseModel):
    key: str
    label: str
    fields: List[QueryField] = Field(default_factory=list)

class QueryComposition(BaseModel):
    name: str
    field_count: int = 0
    sections: List[QuerySection] = Field(default_factory=list)

class QueryFormsResponse(BaseModel):
    compositions: List[QueryComposition] = Field(default_factory=list)

class QuerySuggestionsResponse(BaseModel):
    field_name: str
    suggestions: List[QueryFieldSuggestion] = Field(default_factory=list)
