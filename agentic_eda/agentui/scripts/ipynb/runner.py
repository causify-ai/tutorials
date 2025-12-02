#!/usr/bin/env python3
import argparse
import base64
import json
import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

try:
    import matplotlib
except ImportError:  # pragma: no cover
    matplotlib = None  # type: ignore

PATH_LITERAL_PATTERN = re.compile(r'(["\'])/(?!/)([^"\']+?)(\1)')
RUN_ID_SANITIZE = re.compile(r'[^A-Za-z0-9._-]+')


def _rewrite_literal(workspace_root: str | None, literal: str) -> str:
    if not workspace_root:
        return literal
    normalized = literal.lstrip('/')
    if not normalized:
        return literal
    trailing = normalized.endswith('/')
    stripped = normalized.rstrip('/')
    if not stripped:
        return literal
    first_segment = stripped.split('/', 1)[0]
    candidate_root = os.path.join(workspace_root, first_segment)
    if not os.path.exists(candidate_root):
        return literal
    rebuilt = os.path.join(workspace_root, stripped)
    if trailing and not rebuilt.endswith(os.sep):
        rebuilt = rebuilt + os.sep
    return rebuilt


def _rewrite_source(source: str, workspace_root: str | None) -> str:
    if not workspace_root:
        return source

    def _replace(match: re.Match[str]) -> str:
        start_quote, body, _ = match.groups()
        rewritten = _rewrite_literal(workspace_root, f'/{body}')
        return f'{start_quote}{rewritten}{start_quote}'

    return PATH_LITERAL_PATTERN.sub(_replace, source)


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _prepare_notebook(path: str, workspace_root: str | None):
    nb = nbformat.read(path, as_version=4)
    if workspace_root:
        for cell in nb.cells:
            if cell.get('cell_type') == 'code':
                cell['source'] = _rewrite_source(cell.get('source', ''), workspace_root)
    return nb


def _artifact_directory(output_path: str, run_id: str) -> Path:
    base = Path(output_path).with_suffix('')
    artifacts_root = base / 'artifacts'
    safe_run = RUN_ID_SANITIZE.sub('-', run_id)
    artifacts_dir = artifacts_root / f'run-{safe_run}'
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    return artifacts_dir


def _collect_outputs(nb, artifact_dir: Path, attempt_index: int):
    artifacts = []
    errors = []
    for cell_index, cell in enumerate(nb.cells):
        if cell.get('cell_type') != 'code':
            continue
        for output in cell.get('outputs', []):
            if output.get('output_type') == 'error':
                errors.append({
                    "cell": cell_index,
                    "ename": output.get('ename'),
                    "evalue": output.get('evalue'),
                    "traceback": output.get('traceback', [])
                })
            data = output.get('data', {})
            if 'image/png' in data:
                suffix = f"cell-{cell_index}"
                if attempt_index > 1:
                    suffix = f"{suffix}-attempt-{attempt_index}"
                artifact_path = artifact_dir / f"{suffix}.png"
                with open(artifact_path, 'wb') as img:
                    img.write(base64.b64decode(data['image/png']))
                artifacts.append({
                    "cell": cell_index,
                    "path": str(artifact_path),
                    "mimetype": "image/png"
                })
    return artifacts, errors


def _detect_matplotlib_backend():
    if matplotlib is None:
        return None
    try:
        return matplotlib.get_backend()
    except Exception:  # pragma: no cover
        return None


def create_notebook(plan_path: str, output_path: str):
    with open(plan_path, 'r') as f:
        sections = json.load(f)
    nb = new_notebook(cells=[])
    for section in sections:
        nb.cells.append(new_markdown_cell(f"## {section['title']}"))
        if section.get('code'):
            nb.cells.append(new_code_cell(section['code']))
    nbformat.write(nb, output_path)
    return {"status": "ok", "action": "create", "path": output_path}


def run_notebook(
    path: str,
    output_path: str,
    workspace_root: str | None = None,
    allow_errors: bool = False,
    max_retries: int = 1,
    run_id: str | None = None
):
    run_identifier = run_id or uuid4().hex[:12]
    artifact_dir = _artifact_directory(output_path, run_identifier)
    started_at = _timestamp()
    backend = _detect_matplotlib_backend()
    max_retries = max(1, int(max_retries))
    attempt_index = 0
    artifacts = []
    errors = []
    last_exception = None
    while attempt_index < max_retries:
        attempt_index += 1
        nb = _prepare_notebook(path, workspace_root)
        client = NotebookClient(nb, timeout=120, kernel_name='python3', allow_errors=allow_errors)
        try:
            client.execute()
        except CellExecutionError as exc:
            last_exception = str(exc)
        nbformat.write(nb, output_path)
        artifacts, errors = _collect_outputs(nb, artifact_dir, attempt_index)
        if allow_errors or not errors:
            break

    finished_at = _timestamp()
    metadata = {
        "run_id": run_identifier,
        "attempts": attempt_index,
        "max_retries": max_retries,
        "allow_errors": allow_errors,
        "started_at": started_at,
        "finished_at": finished_at,
        "python_version": sys.version,
        "matplotlib_backend": backend,
        "artifact_dir": str(artifact_dir),
        "last_exception": last_exception
    }
    return {
        "status": "ok",
        "action": "run",
        "output": output_path,
        "artifacts": artifacts,
        "errors": errors,
        "metadata": metadata
    }


def summarize_notebook(path: str):
    nb = nbformat.read(path, as_version=4)
    summary = []
    for i, cell in enumerate(nb.cells):
        cell_type = cell['cell_type']
        content = '\n'.join(cell['source'].splitlines()[:5])
        summary.append({"cell": i, "type": cell_type, "preview": content})
    return {"status": "ok", "action": "summarize", "summary": summary}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['create', 'run', 'summarize'])
    parser.add_argument('--plan')
    parser.add_argument('--input')
    parser.add_argument('--output')
    parser.add_argument('--workspace-root')
    parser.add_argument('--allow-errors', action='store_true')
    parser.add_argument('--max-retries', type=int, default=1)
    parser.add_argument('--run-id')
    args = parser.parse_args()

    try:
        if args.action == 'create':
            result = create_notebook(args.plan, args.output)
        elif args.action == 'run':
            result = run_notebook(
                args.input,
                args.output,
                args.workspace_root,
                args.allow_errors,
                args.max_retries,
                args.run_id
            )
        elif args.action == 'summarize':
            result = summarize_notebook(args.input)
        else:
            raise ValueError('Unknown action')
    except Exception as exc:  # pylint: disable=broad-except
        result = {"status": "error", "message": str(exc)}

    print(json.dumps(result))
    sys.exit(0)


if __name__ == '__main__':
    main()
