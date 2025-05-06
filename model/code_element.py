from __future__ import annotations

from abc import ABC
from typing import Dict, List, Set, Union


class CodeElement(ABC):
    """
    Base domain object for anything we record in the knowledge graph.
    """

    def __init__(self, element_id: str, element_type: str, name: str) -> None:
        self.id: str = element_id
        self.type: str = element_type
        self.name: str = name
        self.dependencies: Set[str] = set()
        self.metadata: Dict[str, Union[str, int, float, bool, Dict, List]] = {}

    # -----------------------------------------------------------------
    def add_dependency(self, dep: str) -> None:
        if dep and dep != self.name:
            self.dependencies.add(dep)

    # -----------------------------------------------------------------
    def to_dict(self) -> Dict[str, object]:
        return {
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "dependencies": sorted(self.dependencies),
            "metadata": self.metadata,
        }
