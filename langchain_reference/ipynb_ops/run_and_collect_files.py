from __future__ import annotations

import argparse, json
from pathlib import Path

import nbformat
from nbclient import NotebookClient

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in_nb", required=True)
    ap.add_argument("--run_dir", required=True)
    ap.add_argument("--out_nb", required=True)
    args = ap.parse_args()

    run_dir = Path(args.run_dir).resolve()
    run_dir.mkdir(parents=True, exist_ok=True)

    nb = nbformat.read(args.in_nb, as_version=4)
    client = NotebookClient(
        nb,
        resources={"metadata": {"path": str(run_dir)}},  # sets cwd for execution :contentReference[oaicite:15]{index=15}
        timeout=120,
    )
    client.execute()
    nbformat.write(nb, args.out_nb)

    files = []
    for p in run_dir.rglob("*"):
        if p.is_file():
            files.append({"path": str(p), "size": p.stat().st_size})

    manifest = run_dir / "files_manifest.json"
    manifest.write_text(json.dumps(files, indent=2))
    print(f"Executed notebook: {args.out_nb}")
    print(f"Found {len(files)} files under {run_dir}")
    print(f"Manifest: {manifest}")

if __name__ == "__main__":
    main()
