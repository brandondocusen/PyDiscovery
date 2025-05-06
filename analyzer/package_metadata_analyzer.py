from __future__ import annotations

import tomllib
from pathlib import Path

from pydiscovery.analyzer.base import Analyzer
from pydiscovery.util.knowledge_graph_file_handler import KnowledgeGraphFileHandler


class PackageMetadataAnalyzer(Analyzer):
    def analyse(self, file_path, tree):
        pass  # handled globally

    def finalize(self, root: Path) -> None:
        pyproject = root / "pyproject.toml"
        if pyproject.exists():
            data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
            graph = KnowledgeGraphFileHandler.load()
            graph["package_metadata"] = data
            KnowledgeGraphFileHandler.save(graph, merge=False)
