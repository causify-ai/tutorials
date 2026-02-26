"""
Import as:

import tools.input_tools as tinptool
"""

import json
import pathlib
import re

import langchain.tools as ltools
import pandas as pd

_VALID_HEADER_START_RE = re.compile(r"^[A-Za-z_]")


def load_dataset(path: pathlib.Path) -> pd.DataFrame:
    """
    Load a supported dataset from disk.

    :param path: path to dataset file
    :return: dataset as dataframe
    """
    ext = path.suffix.lower()
    if ext == ".csv":
        dataset = pd.read_csv(path)
    else:
        raise ValueError(f"Unsupported file extension='{ext}'")
    return dataset


def analyze_header(state: dict) -> dict:
    """
    Validate dataset headers.

    :param state: graph state containing dataset path
    :return: updated state fields with header status
    """
    path = pathlib.Path(str(state["path"]))
    dataset = load_dataset(path)
    cols = list(dataset.columns)
    has_header = True
    error = ""
    if (
        all(isinstance(col, int) for col in cols)
        and cols == list(range(len(cols)))
    ):
        has_header = False
        error = "No column names."
    else:
        for col in cols:
            if col is None:
                has_header = False
                error = "One or more column names missing."
                break
            col_name = str(col).strip()
            if col_name == "":
                has_header = False
                error = "One or more column names missing."
                break
            if (
                col_name[0].isdigit()
                or not _VALID_HEADER_START_RE.match(col_name)
            ):
                has_header = False
                error = (
                    "One or more column names start with invalid characters."
                )
                break
    if has_header:
        result = {"has_header": has_header, "dataset": dataset}
    else:
        result = {"has_header": has_header, "error": error}
    return result


@ltools.tool
def extract_metadata(path: str) -> dict:
    """
    Return minimal dataset metadata.

    :param path: dataset path
    :return: metadata with shape and per-column cardinality
    """
    dataset_path = pathlib.Path(path)
    dataset = load_dataset(dataset_path)
    n_rows, n_cols = dataset.shape
    n_unique = dataset.nunique(dropna=True)
    n_unique_map = {str(col): int(n_unique[col]) for col in n_unique.index}
    metadata = {
        "n_rows": int(n_rows),
        "n_cols": int(n_cols),
        "n_unique": n_unique_map,
    }
    return metadata


@ltools.tool
def extract_head(path: str, *, n: int = 5) -> dict:
    """
    Return the first rows from a dataset.

    :param path: dataset path
    :param n: number of rows to return
    :return: head rows serialized as JSON-compatible payload
    """
    dataset_path = pathlib.Path(path)
    dataset = load_dataset(dataset_path)
    n_rows = int(n)
    if n_rows <= 0:
        n_rows = 5
    n_rows = min(n_rows, 50)
    head = dataset.head(n_rows)
    rows = json.loads(head.to_json(orient="records", date_format="iso"))
    payload = {
        "n": n_rows,
        "columns": [str(col) for col in head.columns.tolist()],
        "rows": rows,
    }
    return payload
