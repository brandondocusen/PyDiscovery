# pydiscovery/analyzer/import_analyzer.py
"""
ImportAnalyzer
==============

Discovers third‑party (PyPI) package usage.

* Stores every `used_by` entry as a **relative path** to the analysed project
  root, saving tokens.
* No external dependencies; uses `importlib.metadata` from the standard
  library to resolve versions.
"""
from __future__ import annotations

import ast
import sys
from importlib import metadata
from pathlib import Path
from typing import Dict, Set

from pydiscovery.analyzer.base import Analyzer

_STD_LIB: Set[str] = set(sys.stdlib_module_names)  # Python ≥ 3.10


class ImportAnalyzer(Analyzer):
    # ------------------------------------------------------------------ #
    def __init__(self, project_root: Path) -> None:
        # This analyser does not create CodeElement objects
        super().__init__(None)  # type: ignore[arg-type]
        self._root = project_root.resolve()
        self._internal: Set[str] = self._discover_internal_packages()
        self._pkg_to_files: Dict[str, Set[str]] = {}

    # ------------------------------------------------------------------ #
    # API consumed by CodeAnalyzer
    def analyse(self, file_path: Path, tree: ast.AST) -> None:
        """Record top‑level import names for a single file."""
        rel = file_path.relative_to(self._root).as_posix()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self._record(alias.name.split(".")[0], rel)
            elif isinstance(node, ast.ImportFrom):
                if node.level == 0 and node.module:
                    self._record(node.module.split(".")[0], rel)

    def external_dependencies(self) -> list[dict]:
        """Return list sorted by package name."""
        out: list[dict] = []
        for pkg, files in sorted(self._pkg_to_files.items()):
            out.append(
                {
                    "package": pkg,
                    "version": self._resolve_version(pkg),
                    "used_by": sorted(files),
                }
            )
        return out

    # ------------------------------------------------------------------ #
    # helpers
    def _record(self, name: str, rel_file: str) -> None:
        if name in _STD_LIB or name in self._internal or name == "":
            return
        self._pkg_to_files.setdefault(name, set()).add(rel_file)

    def _discover_internal_packages(self) -> Set[str]:
        """Top‑level dirs with `__init__.py` + project folder name itself."""
        pkgs: Set[str] = {self._root.name}
        for child in self._root.iterdir():
            if child.is_dir() and (child / "__init__.py").exists():
                pkgs.add(child.name)
        return pkgs

    @staticmethod
    def _resolve_version(pkg: str) -> str | None:
        try:
            return metadata.version(pkg)
        except metadata.PackageNotFoundError:
            return None
