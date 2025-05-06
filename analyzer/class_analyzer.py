# pydiscovery/analyzer/class_analyzer.py
"""
Extracts static information from every `ast.ClassDef` node.

Signature now matches the call‑site:

    analyse(file_path: Path, tree: ast.AST)

so `CodeAnalyzer` can supply the already‑parsed AST and avoid
double‑parsing overhead.
"""
from __future__ import annotations

import ast
from pathlib import Path
from uuid import uuid4

from pydiscovery.analyzer.base import Analyzer
from pydiscovery.model.class_element import ClassElement


class ClassAnalyzer(Analyzer):
    """Collect class name, inheritance, ctor params, attributes, methods."""

    # ------------------------------------------------------------------ #
    def analyse(self, file_path: Path, tree: ast.AST) -> None:  # noqa: D401
        """
        Iterate over `ClassDef` nodes in *tree* and persist a `ClassElement`
        for each.  *file_path* is kept for future use (e.g. diagnostics),
        but parsing is **not** repeated here.
        """
        for node in (n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)):
            element = self._build_class_element(node)
            self.repo.save(element)

    # ------------------------------------------------------------------ #
    # helpers
    def _build_class_element(self, node: ast.ClassDef) -> ClassElement:
        elt = ClassElement(str(uuid4()), node.name)

        # --- inheritance ------------------------------------------------
        for base in node.bases:
            base_name = getattr(base, "id", None) or getattr(base, "attr", None)
            if base_name:
                elt.set_superclass(base_name)

        # --- body inspection -------------------------------------------
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                if item.name == "__init__":
                    self._handle_constructor(item, elt)
                else:
                    elt.add_method_name(item.name)
            elif isinstance(item, ast.Assign):
                self._record_class_attribute(item, elt)

        return elt

    # ------------------------------------------------------------------ #
    def _handle_constructor(self, func: ast.FunctionDef, elt: ClassElement) -> None:
        # parameters (skip `self`)
        for arg in func.args.args[1:]:
            elt.add_dependency(arg.arg)
            elt.metadata.setdefault("ctor_params", []).append(arg.arg)

        # attribute assignments inside __init__
        for assign in (n for n in ast.walk(func) if isinstance(n, ast.Assign)):
            self._record_attribute_assign(assign, elt)

    # ------------------------------------------------------------------ #
    def _record_attribute_assign(self, assign: ast.Assign, elt: ClassElement) -> None:
        for target in assign.targets:
            if (
                isinstance(target, ast.Attribute)
                and isinstance(target.value, ast.Name)
                and target.value.id == "self"
            ):
                attr_name = target.attr
                elt.metadata.setdefault("attributes", []).append(attr_name)

                rhs = assign.value
                if isinstance(rhs, ast.Call) and isinstance(rhs.func, ast.Name):
                    elt.add_dependency(rhs.func.id)
                elif isinstance(rhs, ast.Name):
                    elt.add_dependency(rhs.id)

    # ------------------------------------------------------------------ #
    def _record_class_attribute(self, assign: ast.Assign, elt: ClassElement) -> None:
        for target in assign.targets:
            if isinstance(target, ast.Name):
                elt.metadata.setdefault("class_attributes", []).append(target.id)
