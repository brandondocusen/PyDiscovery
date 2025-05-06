from __future__ import annotations

import ast
from pathlib import Path

from pydiscovery.analyzer.base import Analyzer
from pydiscovery.model.function_element import FunctionElement


class ContextManagerAnalyzer(Analyzer):
    def analyse(self, file_path: Path, tree: ast.AST) -> None:
        for with_node in (n for n in ast.walk(tree) if isinstance(n, (ast.With, ast.AsyncWith))):
            for item in with_node.items:
                call = item.context_expr
                if isinstance(call, ast.Call) and isinstance(call.func, ast.Name):
                    # attribute 'WITH::<funcname>' for clarity
                    dep = f"WITH::{call.func.id}"
                    # attach to module element
                    top_fn = self.repo.find_by_name(file_path.stem)
                    if top_fn:
                        top_fn.add_dependency(dep)
