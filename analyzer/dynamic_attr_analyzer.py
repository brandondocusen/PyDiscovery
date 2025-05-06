from __future__ import annotations

import ast
from pathlib import Path

from pydiscovery.analyzer.base import Analyzer
from pydiscovery.model.class_element import ClassElement


class DynamicAttrAnalyzer(Analyzer):
    def analyse(self, file_path: Path, tree: ast.AST) -> None:
        for call in (c for c in ast.walk(tree) if isinstance(c, ast.Call)):
            if isinstance(call.func, ast.Name) and call.func.id in {"setattr", "getattr"}:
                cls = self.repo.find_by_name(file_path.stem)
                if isinstance(cls, ClassElement):
                    cls.metadata["dynamic_attrs"] = True
