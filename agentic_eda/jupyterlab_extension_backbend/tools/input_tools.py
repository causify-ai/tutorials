from __future__ import annotations

import json
from typing_extensions import Annotated
from langchain.tools import tool
from langgraph.prebuilt import InjectedState
import pandas as pd
from pathlib import Path
import re
# from src.handle_inputs import InputState

# @tool
# def dataset_brief(
#     question: str,
#     dataset_meta: Annotated[dict, InjectedState("dataset_meta")], # (not visible to the LLM)
# ) -> str:
#     """
#     Answer a question using system-provided dataset metadata 
#     """
#     # dataset_meta comes from state["dataset_meta"], injected at runtime
#     payload = {
#         "question": question,
#         "n_rows": dataset_meta.get("n_rows"),
#         "n_cols": dataset_meta.get("n_cols"),
#         "columns": dataset_meta.get("columns"),
#         "freq": dataset_meta.get("freq"),
#     }
#     return json.dumps(payload)


def load_dataset(path: Path) -> pd.DataFrame:
    # Load dataset.
    
    ext = path.suffix.lower()

    if ext in {'.csv'}:
        data = pd.read_csv(path)
    # TODO: Extend to other types of data.

    return data

def headerAnalysis(
    state
) -> dict:
    path = Path(state['path'])
    data = load_dataset(path)
    cols = list(data.columns)
    has_header: bool = True
    error: str = ""
    _valid_start = re.compile(r"^[A-Za-z_]")
    if all(isinstance(c, int) for c in cols) and cols == list(range(len(cols))):
        has_header = False
        error += "No column names;"

        return {'has_header': has_header, 'error': error}
    
    for i, c in enumerate(cols):
        if c is None:
            has_header = False
            error += "One or more column names missing"
            return {'has_header': has_header, 'error': error}
        name = str(c).strip()
        if name[0].isdigit() or not _valid_start.match(name):
            has_header = False
            error += "One or more column names missing (headers are numbers)"
            return {'has_header': has_header, 'error': error}
    


    return {'has_header': has_header, 'dataset': data}


@tool
def extract_metadata(
        path: str
) -> dict:
    """
    Return minimal dataset metadata.

    Only includes:
    - number of rows
    - number of columns
    - number of unique values per column
    
    :param dataset: dataset to process
    :return: metadata
    """
    d_path = Path(path)
    dataset = load_dataset(d_path)
    n_rows, n_cols = dataset.shape
    nunique = dataset.nunique(dropna=True)
    nunique_map = {str(col): int(nunique[col]) for col in nunique.index}

    return {
        "n_rows": int(n_rows),
        "n_cols": int(n_cols),
        "n_unique": nunique_map,
    }

@tool
def extract_head(
    path: str,
    n: int = 5
) -> dict:
    """
    Return dataset head
    
    :param dataset: dataset to process
    :param n: number of head rows
    :return: the first n rows
    """
    d_path = Path(path)
    dataset = load_dataset(d_path)
    n_int = int(n)
    if n_int <= 0:
        n_int = 5
    n_int = min(n_int, 50)

    head = dataset.head(n_int)
    # Use to_json so datetimes become ISO strings and NaNs become null-ish.
    rows = json.loads(head.to_json(orient="records", date_format="iso"))
    return {
        "n": n_int,
        "columns": [str(c) for c in head.columns.tolist()],
        "rows": rows,
    }
