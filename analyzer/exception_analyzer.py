from __future__ import annotations

import ast
from pathlib import Path

from pydiscovery.analyzer.base import Analyzer
from pydiscovery.model.function_element import FunctionElement


class ExceptionAnalyzer(Analyzer):
    def analyse(self, file_path: Path, tree: ast.AST) -> None:
        for node in ast.walk(tree):
            if isinstance(node, ast.Raise) and node.exc and isinstance(node.exc, ast.Call):
                exc_name = getattr(node.exc.func, "id", None)
                if exc_name:
                    fn = self.repo.find_by_name(file_path.stem)
                    if fn:
                        fn.add_dependency(f"RAISES::{exc_name}")
            elif isinstance(node, ast.ExceptHandler) and node.type and isinstance(node.type, ast.Name):
                fn = self.repo.find_by_name(file_path.stem)
                if fn:
                    fn.add_dependency(f"HANDLES::{node.type.id}")
