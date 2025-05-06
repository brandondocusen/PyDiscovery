from __future__ import annotations

import ast
import logging
from pathlib import Path
from uuid import uuid4

from pydiscovery.analyzer.base import Analyzer
from pydiscovery.model.function_element import FunctionElement

LOG = logging.getLogger(__name__)


class FunctionAnalyzer(Analyzer):
    """Top‑level function discovery with decorators & typing."""

    def analyse(self, file_path: Path, tree: ast.AST) -> None:
        for node in (n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))):
            # skip methods (have ClassDef parent)
            if any(isinstance(p, ast.ClassDef) for p in ast.walk(node) if p is not node):
                continue
            elt = self._build_function_element(node)
            self.repo.save(elt)

    # ------------------------------------------------------------------
    def _build_function_element(self, node: ast.FunctionDef) -> FunctionElement:
        elt = FunctionElement(str(uuid4()), node.name)
        for arg in node.args.args:
            elt.add_parameter(arg.arg)
            if arg.annotation and isinstance(arg.annotation, ast.Name):
                elt.metadata.setdefault("param_types", {})[arg.arg] = arg.annotation.id
        if node.returns and isinstance(node.returns, ast.Name):
            elt.metadata["return_type"] = node.returns.id
        for call in (n for n in ast.walk(node) if isinstance(n, ast.Call)):
            if isinstance(call.func, ast.Name):
                elt.add_dependency(call.func.id)
        for deco in node.decorator_list:
            if isinstance(deco, ast.Name):
                elt.add_dependency(deco.id)
        if isinstance(node, ast.AsyncFunctionDef):
            elt.metadata["async"] = True
        return elt
