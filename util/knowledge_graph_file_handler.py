"""
Persist the knowledge‑graph JSON.

Changes
-------
* Always **overwrite** (no deep‑merge).
* `FILE` is anchored in the pydiscovery package root folder, so the graph
  lands at   pydiscovery/knowledge_graph.json   every run.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


# pydiscovery package root … /pydiscovery
ROOT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_FILE = ROOT_DIR / "knowledge_graph.json"


class KnowledgeGraphFileHandler:
    FILE: Path = OUTPUT_FILE  # public constant

    # ----------------------------------------------------------------- #
    @classmethod
    def save(cls, data: Dict[str, Any]) -> None:
        """Serialise *data* (after sanitising sets / Path) to FILE."""
        serialisable = cls._to_json_safe(data)
        cls.FILE.write_text(json.dumps(serialisable, indent=2), encoding="utf-8")

    @staticmethod
    def _to_json_safe(obj: Any) -> Any:
        """Convert sets ➜ lists, Path ➜ str, recurse into containers."""
        from pathlib import Path  # local import to avoid circulars

        if isinstance(obj, dict):
            return {k: KnowledgeGraphFileHandler._to_json_safe(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [KnowledgeGraphFileHandler._to_json_safe(v) for v in obj]
        if isinstance(obj, set):
            return [KnowledgeGraphFileHandler._to_json_safe(v) for v in sorted(obj)]
        if isinstance(obj, Path):
            return str(obj)
        return obj
