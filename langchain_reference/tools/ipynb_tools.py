from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import nbformat
from nbformat import validate
from langchain_core.tools import tool

WORKSPACE = Path("notebooks").resolve()

def _safe_path(rel_path: str) -> Path:
    p = (WORKSPACE / rel_path).resolve()
    if not str(p).startswith(str(WORKSPACE)):
        raise ValueError("Path escapes workspace")
    return p

@tool
def write_notebook(spec: dict[str, Any], out_rel: str) -> str:
    """
    Write a notebook from a simple spec into the notebooks workspace.
    spec = {"cells": [{"type":"markdown","source":"# Title"}, {"type":"code","source":"print(1)"}]}
    out_rel is a relative path inside WORKSPACE, e.g. "toy.ipynb"
    """
    out_path = _safe_path(out_rel)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    nb = nbformat.v4.new_notebook()
    cells = []
    for c in spec.get("cells", []):
        t: Literal["markdown", "code"] = c["type"]
        src = c.get("source", "")
        if t == "markdown":
            cells.append(nbformat.v4.new_markdown_cell(src))
        elif t == "code":
            cells.append(nbformat.v4.new_code_cell(src))
        else:
            raise ValueError(f"Unknown cell type: {t}")
    nb.cells = cells

    validate(nb)  # nbformat schema validation 
    nbformat.write(nb, str(out_path))
    return str(out_path)
