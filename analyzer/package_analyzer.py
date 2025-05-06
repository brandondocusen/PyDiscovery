from __future__ import annotations

from pathlib import Path

from pydiscovery.analyzer.base import Analyzer
from pydiscovery.model.package_element import PackageElement


class PackageAnalyzer(Analyzer):
    """Filesystem walk to produce PackageElement hierarchy."""

    def analyse(self, file_path, tree):
        pass  # not per‑file

    def finalize(self, root: Path) -> None:
        for pkg_dir in root.rglob("__init__.py"):
            pkg_path = pkg_dir.parent
            rel = pkg_path.relative_to(root)
            pkg_name = ".".join(rel.parts)
            parent = ".".join(rel.parts[:-1]) if len(rel.parts) > 1 else None
            elt = PackageElement(pkg_name, pkg_name)
            if parent:
                elt.add_dependency(parent)
            self.repo.save(elt)
