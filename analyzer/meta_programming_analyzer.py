from __future__ import annotations

import ast
from pathlib import Path

from pydiscovery.analyzer.base import Analyzer
from pydiscovery.model.module_element import ModuleElement


class MetaProgrammingAnalyzer(Analyzer):
    META_FUNCS = {"exec", "eval", "type", "compile", "import_module"}

    def analyse(self, file_path: Path, tree: ast.AST) -> None:
        mod_elt = self.repo.find_by_name(file_path.stem)
        if not isinstance(mod_elt, ModuleElement):
            mod_elt = ModuleElement(file_path.stem, file_path.stem, str(file_path))
        for call in (c for c in ast.walk(tree) if isinstance(c, ast.Call) and isinstance(c.func, ast.Name)):
            if call.func.id in self.META_FUNCS:
                mod_elt.metadata["dynamic_code"] = True
        self.repo.save(mod_elt)
