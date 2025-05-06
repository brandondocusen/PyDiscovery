"""
pydiscovery/repository/code_element_repository.py
Abstract interface for element storage back‑ends.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Optional

from pydiscovery.model.code_element import CodeElement


class CodeElementRepository(ABC):
    """Storage abstraction so we can replace in‑memory storage later."""

    @abstractmethod
    def save(self, element: CodeElement) -> None: ...

    @abstractmethod
    def find_by_name(self, name: str) -> Optional[CodeElement]: ...

    @abstractmethod
    def all_elements(self) -> Iterable[CodeElement]: ...
