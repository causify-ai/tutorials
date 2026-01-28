from __future__ import annotations

import json
from typing_extensions import Annotated
from langchain.tools import tool
from langgraph.prebuilt import InjectedState

@tool
def dataset_brief(
    question: str,
    dataset_meta: Annotated[dict, InjectedState("dataset_meta")], # (not visible to the LLM)
) -> str:
    """
    Answer a question using system-provided dataset metadata 
    """
    # dataset_meta comes from state["dataset_meta"], injected at runtime
    payload = {
        "question": question,
        "n_rows": dataset_meta.get("n_rows"),
        "n_cols": dataset_meta.get("n_cols"),
        "columns": dataset_meta.get("columns"),
        "freq": dataset_meta.get("freq"),
    }
    return json.dumps(payload)
