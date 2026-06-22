from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List
from aqf_runtime.models import RecordUnit

class BaseRepositoryAdapter(ABC):
    name: str = "base"
    @abstractmethod
    def can_handle(self, document: Dict[str, Any]) -> bool: ...
    @abstractmethod
    def normalize(self, document: Dict[str, Any], source_file: Path) -> List[RecordUnit]: ...
