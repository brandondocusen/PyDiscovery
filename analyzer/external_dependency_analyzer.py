"""ExternalDependencyAnalyzer

Detects third‑party packages imported in the project and reports their
installed version (if available) without introducing extra dependencies.
It deliberately filters out:
  * Python standard‑library modules
  * Packages that belong to the project itself (top‑level dirs containing
    `__init__.py` inside the analysed root)

After scanning all files, `external_dependencies()` returns a list of dicts:
    {
        "package": "requests",
        "version": "2.32.0",  # None if not installed / vendored
        "used_by": ["src/net/client.py", "tests/test_api.py"]
    }
This analyser does **not** create CodeElement nodes; the coordinator simply
inserts the resulting list into the knowledge‑graph JSON.
"""
from __future__ import annotations

import ast
import sys
from importlib import metadata
from pathlib import Path
from typing import Dict, List, Set

from pydiscovery.analyzer.base import Analyzer

STD_LIB: Set[str] = set(getattr(sys, "stdlib_module_names", ()))


class ExternalDependencyAnalyzer(Analyzer):
    """Analyse import statements and resolve external package info."""

    def __init__(self, repo):  # repo kept for Analyzer compatibility
        super().__init__(repo)
        self._root: Path | None = None
        self._internal_pkgs: Set[str] = set()
        self._usage: Dict[str, Set[Path]] = {}

    # -----------------------------------------------------------------
    def analyse(self, file_path: Path, tree: ast.AST) -> None:  # noqa: D401
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self._record(alias.name.split(".")[0], file_path)
            elif isinstance(node, ast.ImportFrom):
                if node.level == 0 and node.module:
                    self._record(node.module.split(".")[0], file_path)

    def finalize(self, project_root: Path) -> None:  # noqa: D401
        self._root = project_root.resolve()
        self._internal_pkgs = self._discover_internal_packages()
        # prune stdlib / internal
        for pkg in list(self._usage.keys()):
            if not self._is_external(pkg):
                self._usage.pop(pkg, None)

    # -----------------------------------------------------------------
    def external_dependencies(self) -> List[Dict[str, object]]:  # noqa: D401
        root = self._root or Path.cwd()
        deps: List[Dict[str, object]] = []
        for pkg, files in sorted(self._usage.items()):
            deps.append(
                {
                    "package": pkg,
                    "version": self._pkg_version(pkg),
                    "used_by": sorted(str(p.relative_to(root)) for p in files),
                }
            )
        return deps

    # helpers ----------------------------------------------------------
    def _record(self, top_pkg: str, path: Path) -> None:
        self._usage.setdefault(top_pkg, set()).add(path)

    def _discover_internal_packages(self) -> Set[str]:
        pkgs: Set[str] = set()
        if not self._root:
            return pkgs
        for init in self._root.rglob("__init__.py"):
            parts = init.relative_to(self._root).parts
            if parts:
                pkgs.add(parts[0])
        return pkgs

    def _is_external(self, pkg: str) -> bool:
        return pkg not in STD_LIB and pkg not in self._internal_pkgs

    @staticmethod
    def _pkg_version(pkg: str) -> str | None:
        try:
            return metadata.version(pkg)
        except metadata.PackageNotFoundError:
            return None