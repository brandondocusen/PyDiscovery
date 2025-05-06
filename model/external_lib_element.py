from __future__ import annotations

from pydiscovery.model.code_element import CodeElement


class ExternalLibElement(CodeElement):
    def __init__(self, element_id: str, name: str) -> None:
        super().__init__(element_id, "EXTERNAL_LIB", name)
