"""
pydiscovery/repository/in_memory_repository.py
Simple in‑memory implementation of CodeElementRepository.
"""
from __future__ import annotations

from typing import Dict, Iterable, Optional

from pydiscovery.model.code_element import CodeElement
from pydiscovery.repository.code_element_repository import CodeElementRepository


class InMemoryCodeElementRepository(CodeElementRepository):
    def __init__(self) -> None:
        self._store: Dict[str, CodeElement] = {}

    # ------------------------------------------------------------------
    def save(self, element: CodeElement) -> None:
        self._store[element.name] = element

    def find_by_name(self, name: str) -> Optional[CodeElement]:
        return self._store.get(name)

    def all_elements(self) -> Iterable[CodeElement]:
        return self._store.values()
