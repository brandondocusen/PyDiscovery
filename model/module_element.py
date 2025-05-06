from __future__ import annotations

from pydiscovery.model.code_element import CodeElement


class ModuleElement(CodeElement):
    def __init__(self, element_id: str, name: str, file: str) -> None:
        super().__init__(element_id, "MODULE", name)
        self.metadata["file"] = file
