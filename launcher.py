#!/usr/bin/env python3
"""
pydiscovery/launcher.py
-----------------------

Run PyDiscovery from **any working directory**, including when the shell’s cwd
*is* the `pydiscovery` package directory.

* Overwrites `pydiscovery/knowledge_graph.json` on every run.
* Emits only relative file paths inside the graph (the single absolute
  `"root"` key suffices to reconstruct them).
* Pretty‑prints JSON to stdout using the same conversion helper that ensures
  sets / Path objects are serialisable.
"""
from __future__ import annotations

# ------------------------------------------------------------------ #
# 1.  ensure absolute imports work when cwd == pydiscovery directory
import sys
from pathlib import Path

_PKG_DIR = Path(__file__).resolve().parent           # …/pydiscovery
_PROJECT_ROOT = _PKG_DIR.parent                      # one level up

if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# ------------------------------------------------------------------ #
# 2.  standard‑lib + internal imports (after path tweak)
import json
import logging
from uuid import uuid4

from pydiscovery.analyzer.code_analyzer import CodeAnalyzer
from pydiscovery.repository.in_memory_repository import InMemoryCodeElementRepository
from pydiscovery.util.knowledge_graph_file_handler import KnowledgeGraphFileHandler

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
LOG = logging.getLogger("pydiscovery.launcher")


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage:\n"
            "  python launcher.py <path‑to‑project>            # from inside pydiscovery\n"
            "  python -m pydiscovery.launcher <path‑to‑project> # from parent directory"
        )
        sys.exit(1)

    project_root = Path(sys.argv[1]).resolve()
    if not project_root.exists():
        raise SystemExit(f"Path not found: {project_root}")

    LOG.info("Analysing %s …", project_root)

    # 3.  run analysis
    repo = InMemoryCodeElementRepository()
    graph = CodeAnalyzer(repo).analyse_path(project_root)

    # 4.  minimal additional metadata
    graph["analysis_id"] = str(uuid4())
    graph["root"] = str(project_root)

    # 5.  persist & pretty‑print
    KnowledgeGraphFileHandler.save(graph)
    LOG.info("Knowledge graph written to %s", KnowledgeGraphFileHandler.FILE)

    print(json.dumps(KnowledgeGraphFileHandler._to_json_safe(graph), indent=2))


if __name__ == "__main__":
    main()
