from __future__ import annotations

import argparse, base64, json
from pathlib import Path

import nbformat

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--executed_nb", required=True)
    ap.add_argument("--out_dir", required=True)
    args = ap.parse_args()

    nb = nbformat.read(args.executed_nb, as_version=4)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = []

    for i, cell in enumerate(nb.cells):
        if cell.get("cell_type") != "code":
            continue

        # 1) stdout/stderr streams
        for j, out in enumerate(cell.get("outputs", [])):
            if out.get("output_type") == "stream":
                text = out.get("text", "")
                p = out_dir / f"cell_{i}_stream_{j}.txt"
                p.write_text(text if isinstance(text, str) else "".join(text))
                manifest.append({"cell": i, "kind": "stream", "path": str(p)})

            # 2) mimebundle images/text
            if out.get("output_type") in ("display_data", "execute_result"):
                data = out.get("data", {})
                if "text/plain" in data:
                    t = data["text/plain"]
                    p = out_dir / f"cell_{i}_text_{j}.txt"
                    p.write_text(t if isinstance(t, str) else "".join(t))
                    manifest.append({"cell": i, "kind": "text/plain", "path": str(p)})

                if "image/png" in data:
                    b64 = data["image/png"]
                    b = base64.b64decode(b64 if isinstance(b64, str) else "".join(b64))
                    p = out_dir / f"cell_{i}_img_{j}.png"
                    p.write_bytes(b)
                    manifest.append({"cell": i, "kind": "image/png", "path": str(p)})

    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"Wrote {len(manifest)} artifacts + manifest.json to {out_dir}")

if __name__ == "__main__":
    main()
