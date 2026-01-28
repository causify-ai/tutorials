# ipynb_ops/run_papermill.py
from __future__ import annotations

import argparse
from pathlib import Path
import papermill as pm

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in_nb", required=True)
    ap.add_argument("--out_nb", required=True)
    ap.add_argument("--x", type=float, required=True)
    ap.add_argument("--y", type=float, required=True)
    ap.add_argument("--kernel", default="python3")
    ap.add_argument("--language", default="python")
    ap.add_argument("--cwd", default=None)
    args = ap.parse_args()

    Path(args.out_nb).parent.mkdir(parents=True, exist_ok=True)

    pm.execute_notebook(
        args.in_nb,
        args.out_nb,
        parameters={"x": args.x, "y": args.y},
        kernel_name=args.kernel,
        language=args.language,  
        cwd=args.cwd,
    )
    print(f"Ran papermill -> {args.out_nb}")

if __name__ == "__main__":
    main()
