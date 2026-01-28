# Notebook Tooling Pipeline

This document summarizes how AgenTUI handles notebook-oriented requests end-to-end.

## Core Flow

1. **Creation** – `ipynb_create` writes a notebook from a plan (markdown + optional code snippets).  
2. **Patching** – `ipynb_patch` can replace/insert/remove cells while preserving execution outputs (new cells start with empty outputs/execution counts).  
3. **Execution** – `ipynb_run` executes notebooks with `nbclient`, captures errors, and stores artifacts under `<executed>.ipynb/artifacts/run-<id>/`.  
4. **Analysis** – `ipynb_analyze` filters notebook summaries (optional `includeMarkdown`, `includeCode`, `maxCells`).  
5. **Artifact lookup** – `ipynb_artifacts` lists the saved images for any executed notebook so the agent can answer “where is the plot?” style questions without rerunning.

## Image Handling

- Notebook runs save images to both the `artifacts/run-*` directory and any explicit output path the notebook code uses.  
- The new `ipynb_artifacts` tool allows the agent to answer “where is the sine plot saved?” by listing filenames and run IDs.  
- Automatic image analysis is **disabled** by default; set `AGEN_TUI_AUTO_ANALYZE_IMAGES=1` before calling `ipynb_run` to enable captions inline, or ask the agent to run `analyze_image` manually for specific files.

## CLI Smoke Coverage

`npm run agent:smoke` now tests:

- Filesystem listing commands.  
- Notebook creation.  
- Notebook summarization (`ipynb_analyze`).  
- A patch + run workflow that inserts a new code cell, executes the notebook, and lists generated artifacts.

## Troubleshooting

- If artifacts are missing, rerun the notebook (`ipynb_run`) and then call `ipynb_artifacts`.  
- When patching cells, specify either `cellIndex` (exact position) or a `match` string so the helper can find the right cell.  
- Use the new `includeMarkdown` / `includeCode` flags when summarizing heavy notebooks to keep responses concise.
