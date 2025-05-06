from __future__ import annotations

import ast
from pathlib import Path
from uuid import uuid4

from pydiscovery.analyzer.base import Analyzer
from pydiscovery.model.config_key_element import ConfigKeyElement


class ConfigAnalyzer(Analyzer):
    CONFIG_FUNCS = {"getenv", "ConfigParser", "load"}

    def analyse(self, file_path: Path, tree: ast.AST) -> None:
        for call in (c for c in ast.walk(tree) if isinstance(c, ast.Call)):
            func_name = None
            if isinstance(call.func, ast.Attribute):
                func_name = call.func.attr
            elif isinstance(call.func, ast.Name):
                func_name = call.func.id
            if func_name in self.CONFIG_FUNCS and call.args:
                key_node = call.args[0]
                if isinstance(key_node, ast.Constant) and isinstance(key_node.value, str):
                    key = key_node.value
                    elt = ConfigKeyElement(str(uuid4()), key)
                    self.repo.save(elt)
