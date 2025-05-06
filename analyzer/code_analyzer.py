# pydiscovery/analyzer/code_analyzer.py
"""
CodeAnalyzer
============

* Stores the absolute project root **once** (`"root"` is injected by
  `launcher.py`).
* Every file path embedded in the graph (`files`, `data_flows`,
  `external_dependencies[*].used_by`) is now **relative to that root**,
  saving tokens for LLM consumption.
"""
from __future__ import annotations

import ast
import logging
from pathlib import Path
from typing import Dict, List, Set

from pydiscovery.analyzer.class_analyzer import ClassAnalyzer
from pydiscovery.analyzer.function_analyzer import FunctionAnalyzer
from pydiscovery.analyzer.data_flow_analyzer import DataFlowAnalyzer
from pydiscovery.analyzer.import_analyzer import ImportAnalyzer
from pydiscovery.repository.code_element_repository import CodeElementRepository

LOG = logging.getLogger(__name__)


class CodeAnalyzer:
    """Runs analysers and returns a compact, relative‑path knowledge‑graph."""

    # ------------------------------------------------------------------ #
    def __init__(self, repository: CodeElementRepository) -> None:
        self._repo = repository
        # concrete analysers are created later when we know the project root
        self._class_an: ClassAnalyzer | None = None
        self._func_an: FunctionAnalyzer | None = None
        self._import_an: ImportAnalyzer | None = None
        self._df_an = DataFlowAnalyzer()

        self._root: Path | None = None
        self._data_flows: Dict[str, Dict[str, Set[str]]] = {}

    # ------------------------------------------------------------------ #
    def analyse_path(self, root: Path) -> Dict[str, object]:
        self._root = root.resolve()
        self._class_an = ClassAnalyzer(self._repo)
        self._func_an = FunctionAnalyzer(self._repo)
        self._import_an = ImportAnalyzer(self._root)

        files: List[str] = []
        for py in self._root.rglob("*.py"):
            files.append(self._rel(py))
            self._analyse_file(py)

        graph: Dict[str, object] = {
            "files": files,
            "elements": [elt.to_dict() for elt in self._repo.all_elements()],
            "data_flows": self._data_flows,
            "external_dependencies": self._import_an.external_dependencies(),  # type: ignore[union-attr]
        }
        return graph

    # ------------------------------------------------------------------ #
    # helpers
    def _analyse_file(self, path: Path) -> None:
        tree = self._safe_parse(path)
        if tree is None or self._class_an is None or self._func_an is None or self._import_an is None:
            return

        self._class_an.analyse(path, tree)
        self._func_an.analyse(path, tree)
        self._import_an.analyse(path, tree)

        flows = self._df_an.analyse(tree)
        if flows:
            self._data_flows[self._rel_str(path)] = flows

    @staticmethod
    def _safe_parse(path: Path) -> ast.AST | None:
        try:
            return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (SyntaxError, UnicodeDecodeError) as err:
            LOG.debug("Skip %s – %s", path, err)
            return None

    # ------------------------------------------------------------------ #
    def _rel(self, p: Path) -> str:
        return self._rel_str(p)

    def _rel_str(self, p: Path) -> str:
        return p.relative_to(self._root).as_posix()  # type: ignore[arg-type]
