from __future__ import annotations

import argparse
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in_nb", required=True)
    ap.add_argument("--out_nb", required=True)
    ap.add_argument("--workdir", default=".")
    ap.add_argument("--timeout", type=int, default=60)
    args = ap.parse_args()

    in_path = Path(args.in_nb)
    out_path = Path(args.out_nb)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    nb = nbformat.read(str(in_path), as_version=4)
    client = NotebookClient(
        nb,
        timeout=args.timeout,
        resources={"metadata": {"path": str(Path(args.workdir).resolve())}},
    )

    try:
        client.execute()
    except CellExecutionError:
        print(f'Error executing "{in_path}". See "{out_path}" for traceback.')
        raise
    finally:
        nbformat.write(nb, str(out_path))  # always save 

if __name__ == "__main__":
    main()
