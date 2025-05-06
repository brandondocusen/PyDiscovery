from __future__ import annotations

import ast
from pathlib import Path

from pydiscovery.analyzer.base import Analyzer
from pydiscovery.model.module_element import ModuleElement


class EntryPointAnalyzer(Analyzer):
    def analyse(self, file_path: Path, tree: ast.AST) -> None:
        for node in ast.walk(tree):
            if isinstance(node, ast.If) and isinstance(node.test, ast.Compare):
                # crude check for if __name__ == "__main__"
                names = {getattr(node.test.left, "id", "")}
                names.update(getattr(c, "s", "") for c in node.test.comparators if isinstance(c, ast.Constant))
                if "__name__" in names and "__main__" in names:
                    elt = self.repo.find_by_name(file_path.stem)
                    if isinstance(elt, ModuleElement):
                        elt.metadata["entry_point"] = True
