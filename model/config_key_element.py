from __future__ import annotations

from pydiscovery.model.code_element import CodeElement


class ConfigKeyElement(CodeElement):
    def __init__(self, element_id: str, name: str) -> None:
        super().__init__(element_id, "CONFIG_KEY", name)
