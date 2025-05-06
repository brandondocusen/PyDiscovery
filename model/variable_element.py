from __future__ import annotations

from pydiscovery.model.code_element import CodeElement


class VariableElement(CodeElement):
    """Represents a module‑level variable or constant."""

    def __init__(self, element_id: str, name: str) -> None:
        super().__init__(element_id, "VARIABLE", name)
