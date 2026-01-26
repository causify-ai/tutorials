from __future__ import annotations

import argparse
from pathlib import Path

import nbformat
from nbclient import NotebookClient

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in_nb", required=True)
    ap.add_argument("--out_nb", required=True)
    ap.add_argument("--workdir", default=".")
    ap.add_argument("--timeout", type=int, default=60)
    ap.add_argument("--kernel", default=None)  # e.g. "python3"
    args = ap.parse_args()

    in_path = Path(args.in_nb)
    out_path = Path(args.out_nb)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    nb = nbformat.read(str(in_path), as_version=4)  # as_version recommended 

    client = NotebookClient(
        nb,
        timeout=args.timeout,
        kernel_name=args.kernel,
        resources={"metadata": {"path": str(Path(args.workdir).resolve())}},
    )
    client.execute()  # fills outputs

    nbformat.write(nb, str(out_path))
    print(f"Executed notebook saved to: {out_path}")

if __name__ == "__main__":
    main()
