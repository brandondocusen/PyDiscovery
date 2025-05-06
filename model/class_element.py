from __future__ import annotations

from pydiscovery.model.code_element import CodeElement


class ClassElement(CodeElement):
    def __init__(self, element_id: str, name: str) -> None:
        super().__init__(element_id, "CLASS", name)
        self.methods: list[str] = []
        self.superclass: str | None = None

    # -----------------------------------------------------------------
    def set_superclass(self, superclass: str) -> None:
        self.superclass = superclass
        self.add_dependency(superclass)

    def add_method_name(self, method: str) -> None:
        self.methods.append(method)

    # -----------------------------------------------------------------
    def to_dict(self):
        base = super().to_dict()
        base.update(
            {
                "methods": self.methods,
                "superclass": self.superclass,
            }
        )
        return base
