from __future__ import annotations

import ast
from pathlib import Path

from pydiscovery.analyzer.base import Analyzer
from pydiscovery.model.function_element import FunctionElement


class TypingAnalyzer(Analyzer):
    """Stores PEP‑484 annotations into metadata."""

    def analyse(self, file_path: Path, tree: ast.AST) -> None:
        for node in (n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))):
            fn_name = node.name
            elt = self.repo.find_by_name(fn_name)
            if isinstance(elt, FunctionElement):
                # parameters
                for arg in node.args.args:
                    if arg.annotation and isinstance(arg.annotation, ast.Name):
                        elt.metadata.setdefault("param_types", {})[arg.arg] = arg.annotation.id
                if node.returns and isinstance(node.returns, ast.Name):
                    elt.metadata["return_type"] = node.returns.id
