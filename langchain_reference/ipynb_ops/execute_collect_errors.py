from __future__ import annotations

import argparse, json
from pathlib import Path

import nbformat
from nbclient import NotebookClient

def extract_errors(nb) -> list[dict]:
    errs = []
    for i, cell in enumerate(nb.cells):
        if cell.get("cell_type") != "code":
            continue
        for out in cell.get("outputs", []):
            if out.get("output_type") == "error":
                errs.append({
                    "cell_index": i,
                    "ename": out.get("ename"),
                    "evalue": out.get("evalue"),
                    "traceback": out.get("traceback", [])[:20],
                })
    return errs

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in_nb", required=True)
    ap.add_argument("--out_nb", required=True)
    ap.add_argument("--report", required=True)
    ap.add_argument("--workdir", default=".")
    ap.add_argument("--timeout", type=int, default=60)
    args = ap.parse_args()

    nb = nbformat.read(args.in_nb, as_version=4)

    client = NotebookClient(
        nb,
        timeout=args.timeout,
        allow_errors=True,  # keep going even if cells error :contentReference[oaicite:11]{index=11}
        resources={"metadata": {"path": str(Path(args.workdir).resolve())}},
    )
    client.execute()

    Path(args.out_nb).parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(nb, args.out_nb)

    errors = extract_errors(nb)
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(json.dumps(errors, indent=2))
    print(f"Wrote executed notebook: {args.out_nb}")
    print(f"Wrote error report: {args.report} (n={len(errors)})")

if __name__ == "__main__":
    main()
