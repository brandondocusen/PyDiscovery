from __future__ import annotations

from pydiscovery.model.code_element import CodeElement


class DecoratorElement(CodeElement):
    def __init__(self, element_id: str, name: str) -> None:
        super().__init__(element_id, "DECORATOR", name)
