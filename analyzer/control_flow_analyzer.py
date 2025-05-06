from __future__ import annotations

import ast
from pathlib import Path
from typing import Dict, List

from pydiscovery.analyzer.base import Analyzer


class ControlFlowAnalyzer(Analyzer):
    """
    Simple stub that records presence of control‑flow constructs
    (If / For / While / Try) in each module.
    """

    def analyse(self, file_path: Path, tree: ast.AST) -> None:
        structures: List[str] = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.Try)):
                structures.append(type(node).__name__)
        if structures:
            mod = self.repo.find_by_name(file_path.stem)
            if mod:
                mod.metadata["control_structures"] = structures
