from __future__ import annotations

import ast
from pathlib import Path
from uuid import uuid4

from pydiscovery.analyzer.base import Analyzer
from pydiscovery.model.variable_element import VariableElement


class ModuleVariableAnalyzer(Analyzer):
    def analyse(self, file_path: Path, tree: ast.AST) -> None:
        for node in (n for n in tree.body if isinstance(n, ast.Assign)):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    var = VariableElement(str(uuid4()), target.id)
                    self.repo.save(var)
