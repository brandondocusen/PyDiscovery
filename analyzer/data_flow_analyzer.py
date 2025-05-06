from __future__ import annotations

import ast
from typing import Dict, Set


class DataFlowAnalyzer:
    """
    Builds a very lightweight variable assignment dependency graph
    for a single AST (file).
    """

    # -----------------------------------------------------------------
    def analyse(self, node: ast.AST) -> Dict[str, Set[str]]:
        assigns: Dict[str, Set[str]] = {}
        for n in ast.walk(node):
            if isinstance(n, ast.Assign):
                # left‑hand targets
                targets = [t.id for t in n.targets if isinstance(t, ast.Name)]
                # RHS dependencies (all Name nodes inside the value)
                deps = {d.id for d in ast.walk(n.value) if isinstance(d, ast.Name)}
                for t in targets:
                    assigns.setdefault(t, set()).update(deps)
        return assigns
