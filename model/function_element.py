from __future__ import annotations

from pydiscovery.model.code_element import CodeElement


class FunctionElement(CodeElement):
    def __init__(self, element_id: str, name: str) -> None:
        super().__init__(element_id, "FUNCTION", name)
        self.parameters: list[str] = []

    # -----------------------------------------------------------------
    def add_parameter(self, param_name: str) -> None:
        self.parameters.append(param_name)

    # -----------------------------------------------------------------
    def to_dict(self):
        base = super().to_dict()
        base.update({"parameters": self.parameters})
        return base
