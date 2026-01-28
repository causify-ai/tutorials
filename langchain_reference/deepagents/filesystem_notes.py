from __future__ import annotations

from deepagents import create_deep_agent
from src.config import get_chat_model
from pathlib import Path

def main():
    model = get_chat_model()

    # Default backend is StateBackend (ephemeral in state). :contentReference[oaicite:16]{index=16}
    agent = create_deep_agent(model=model)

    prompt = (
        "Do the following using filesystem tools:\n"
        "1) write_file to /workspace/notes.md with 6 bullet points of EDA checks for multivariate time series.\n"
        "2) read_file /workspace/notes.md\n"
        "3) In your final answer, quote exactly 2 bullets from the file and say why they matter.\n"
    )

    out_state = agent.invoke({"messages": [{"role": "user", "content": prompt}]})

    print("\n=== FINAL ANSWER ===\n")
    print(out_state["messages"][-1].content)

    print("\n=== STATE KEYS ===")
    print(list(out_state.keys()))

    # Some versions expose a "files" channel in state. :contentReference[oaicite:17]{index=17}
    if "files" in out_state:
        print("\n=== FILES (state backend) ===")
        # Might be large; print just the keys
        Path("workspace").mkdir(parents=True, exist_ok=True)
        # dump file from state.
        Path("workspace/notes.md").write_text("\n".join(out_state["files"]["/workspace/notes.md"]["content"]), encoding="utf-8")
        files = out_state["files"]
        if isinstance(files, dict):
            print("paths:", list(files.keys())[:20])
        else:
            print(type(files), files)


if __name__ == "__main__":
    main()
