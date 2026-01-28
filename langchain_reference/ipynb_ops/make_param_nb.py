from __future__ import annotations
from pathlib import Path
import nbformat

def main():
    Path("notebooks").mkdir(exist_ok=True)
    nb = nbformat.v4.new_notebook()

    # parameters cell (tagged)
    params = nbformat.v4.new_code_cell("x = 2\ny = 5")
    params.metadata["tags"] = ["parameters"]

    body = nbformat.v4.new_code_cell(
        "print('x+y =', x + y)\n"
        "print('x*y =', x * y)\n"
    )

    nb.cells = [nbformat.v4.new_markdown_cell("# Papermill params demo"), params, body]
    nbformat.write(nb, "notebooks/params_demo.ipynb")
    print("Wrote notebooks/params_demo.ipynb")

if __name__ == "__main__":
    main()
