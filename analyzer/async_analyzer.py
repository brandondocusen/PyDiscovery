from __future__ import annotations

import ast
from pathlib import Path

from pydiscovery.analyzer.base import Analyzer
from pydiscovery.model.function_element import FunctionElement


class AsyncAnalyzer(Analyzer):
    """Marks async functions and await dependencies."""

    def analyse(self, file_path: Path, tree: ast.AST) -> None:
        for node in (n for n in ast.walk(tree) if isinstance(n, ast.AsyncFunctionDef)):
            fn_name = node.name
            elt = self.repo.find_by_name(fn_name)
            if not isinstance(elt, FunctionElement):
                continue
            elt.metadata["async"] = True
            for aw in (n for n in ast.walk(node) if isinstance(n, ast.Await)):
                if isinstance(aw.value, ast.Call) and isinstance(aw.value.func, ast.Name):
                    elt.add_dependency(aw.value.func.id)
