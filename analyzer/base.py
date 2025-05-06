from __future__ import annotations

import ast
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Optional

from pydiscovery.repository.code_element_repository import CodeElementRepository


class Analyzer(ABC):
    """Common interface for all analyzers."""

    def __init__(self, repository: CodeElementRepository) -> None:
        self.repo = repository

    @abstractmethod
    def analyse(self, file_path: Path, tree: ast.AST) -> None: ...

    def finalize(self, root: Path) -> None:  # optional
        pass

    # helpers ----------------------------------------------------------
    @staticmethod
    def safe_parse(path: Path) -> Optional[ast.AST]:
        try:
            return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (SyntaxError, UnicodeDecodeError):
            return None
