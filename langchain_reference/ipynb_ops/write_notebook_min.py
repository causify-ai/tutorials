from __future__ import annotations

import argparse
from pathlib import Path

import nbformat
from nbformat import validate  # schema validation

def build_nb():
    nb = nbformat.v4.new_notebook()
    nb.cells = [
        nbformat.v4.new_markdown_cell("# Hello"),
        nbformat.v4.new_code_cell("print('hello from a generated notebook')"),
    ]
    return nb

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    nb = build_nb()
    validate(nb)  # raises ValidationError if invalid :contentReference[oaicite:1]{index=1}

    nbformat.write(nb, str(out_path))
    print(f"Wrote: {out_path}")

if __name__ == "__main__":
    main()
