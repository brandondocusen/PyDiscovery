from __future__ import annotations

import ast
from pathlib import Path

from pydiscovery.analyzer.base import Analyzer
from pydiscovery.model.module_element import ModuleElement


class TestCoverageAnalyzer(Analyzer):
    """Map tests to imported modules."""

    def analyse(self, file_path: Path, tree: ast.AST) -> None:
        if "tests" not in file_path.parts and not file_path.name.startswith("test_"):
            return
        test_mod = self.repo.find_by_name(file_path.stem) or ModuleElement(
            file_path.stem, file_path.stem, str(file_path)
        )
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    test_mod.add_dependency(f"COVERS::{alias.name}")
            elif isinstance(node, ast.ImportFrom) and node.module:
                test_mod.add_dependency(f"COVERS::{node.module}")
        self.repo.save(test_mod)
