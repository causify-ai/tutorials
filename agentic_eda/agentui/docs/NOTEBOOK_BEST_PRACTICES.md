# Notebook Guardrails for AgenTUI

Derived from Context7 documentation for Jupyter Notebook, Matplotlib, and nbclient, remind notebook operations of the following:

1. Plot, save, and close in the same cell. Capture the figure handle (e.g., `fig, ax = plt.subplots()`, then `fig.savefig('path.png', dpi=200)` and `plt.close(fig)`) so saved plots match what was drawn.
2. Show inline plots unless the user explicitly wants a headless run. The binder example notebook demonstrates pairing plotting code with `plt.show()` for immediate visibility.
3. Summaries and edits must use `nbformat` to inspect cells (`for cell in nb.cells`) instead of fragile string parsing. The `show_notebook` helper in the official docs is the reference.
4. Execute notebooks with nbclient’s pattern: wrap `client.execute()` in `try/except CellExecutionError`, write the executed notebook in a `finally` block, and surface the traceback pointing to the executed copy.
5. Only enable `allow_errors`/`--allow-errors` when a prompt explicitly asks to collect failures; otherwise stop on the first error so we can fix the notebook before re-running.
