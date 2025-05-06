# pydiscovery/analyzer/runtime_monitor.py
"""
Minimal runtime monitor that records caller→callee edges and call counts
using `sys.setprofile`.  Usage:

>>> from pydiscovery.analyzer.runtime_monitor import RuntimeMonitor
>>> with RuntimeMonitor() as mon:
...     your_function()
>>> print(mon.edges)
"""
from __future__ import annotations

import sys
import threading
from types import FrameType
from typing import Dict, Tuple

CallEdge = Tuple[str, str]  # (caller, callee)


class RuntimeMonitor:
    def __init__(self) -> None:
        self.edges: Dict[CallEdge, int] = {}
        self._lock = threading.Lock()

    # context‑manager ---------------------------------------------------
    def __enter__(self):
        sys.setprofile(self._profile)
        return self

    def __exit__(self, exc_type, exc, tb):
        sys.setprofile(None)

    # profiler callback -------------------------------------------------
    def _profile(self, frame: FrameType, event: str, arg):  # noqa: ANN001
        if event != "call":
            return
        caller = frame.f_back
        callee_name = self._qualname(frame)
        caller_name = self._qualname(caller) if caller else "<root>"
        edge = (caller_name, callee_name)
        with self._lock:
            self.edges[edge] = self.edges.get(edge, 0) + 1

    # helpers -----------------------------------------------------------
    @staticmethod
    def _qualname(frame: FrameType | None) -> str:
        if frame is None:
            return "<root>"
        code = frame.f_code
        return f"{code.co_filename}:{code.co_name}"