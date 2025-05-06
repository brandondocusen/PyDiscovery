from __future__ import annotations

import ast
from pathlib import Path

from pydiscovery.analyzer.base import Analyzer
from pydiscovery.model.function_element import FunctionElement


class DecoratorAnalyzer(Analyzer):
    """Adds decorator→function edges."""

    def analyse(self, file_path: Path, tree: ast.AST) -> None:
        for node in (n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))):
            fn_name = node.name
            fn_elt = self.repo.find_by_name(fn_name)
            if not fn_elt:
                fn_elt = FunctionElement(fn_name, fn_name)
            for deco in node.decorator_list:
                if isinstance(deco, ast.Name):
                    fn_elt.add_dependency(deco.id)
            self.repo.save(fn_elt)
