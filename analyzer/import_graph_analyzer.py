from __future__ import annotations

import ast
import sys
from pathlib import Path

from pydiscovery.analyzer.base import Analyzer
from pydiscovery.model.module_element import ModuleElement


class ImportGraphAnalyzer(Analyzer):
    """Captures module‑level import dependencies."""

    def __init__(self, repository):
        super().__init__(repository)
        self._root: Path | None = None

    # ------------------------------------------------------------------
    def analyse(self, file_path: Path, tree: ast.AST) -> None:
        mod_name = self._module_name(file_path)
        if mod_name is None:
            return
        module_elt = self.repo.find_by_name(mod_name) or ModuleElement(
            element_id=mod_name, name=mod_name, file=str(file_path)
        )
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_elt.add_dependency(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module_elt.add_dependency(node.module)
        self.repo.save(module_elt)

    # helpers -----------------------------------------------------------
    def _module_name(self, path: Path) -> str | None:
        if self._root is None:
            return path.stem
        try:
            return str(path.relative_to(self._root)).replace(".py", "").replace("/", ".")
        except ValueError:
            return None

    def finalize(self, root: Path) -> None:
        self._root = root
