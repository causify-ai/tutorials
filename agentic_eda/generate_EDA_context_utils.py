"""
Import as:

import agentic_eda.generate_EDA_context_utils as aegecout
"""

import ast
import logging
import os
from typing import Tuple

import helpers.hio as hio
import pandas as pd

_LOG = logging.getLogger(__name__)


def read_function_table(filepath: str) -> pd.DataFrame:
    """
    Convert a table from a Markdown file into a DataFrame.

    :param filepath: path to the Markdown file
    :return: table with function metadata (e.g., function type, script
        path, and function name)
    """
    df = pd.read_csv(filepath, sep="|", engine="python")
    df = df.dropna(axis=1, how="all")
    # Drop auto-generated 'Unnamed' index column.
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    df.columns = df.columns.str.strip()
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
    # Remove separator line.
    is_separator_row = df["Script Path"].str.fullmatch(r"-+")
    df = df[~is_separator_row]
    return df


def get_function_line_range_and_docstring(
    file_path: str, function_name: str
) -> Tuple[str, str]:
    """
    Get a function's line range and docstring.

    :param file_path: path to the Python script containing the function
    :param function_name: name of the function
    :return: line range of function and docstring text
    """
    source = hio.from_file(file_path, encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            # Extract the function's start and end lines.
            start_line = node.lineno
            end_line = (
                node.end_lineno if hasattr(node, "end_lineno") else start_line
            )
            docstring = ast.get_docstring(node) or ""
            return f"{start_line}-{end_line}", docstring
    raise ValueError(f"Function '{function_name}' not found in {file_path}")


def enrich_function_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add 'Line Range' and 'Docstring' to a table of function metadata.

    :param df: table with function metadata (e.g., function type, script
        path, function name, line range, and docstring)
    :return: table including 'Line Range' and 'Docstring' columns

    Example output:
    ```
    | Function Type | Script Path | Function Name | Line Range | Docstring |
    | ------------- | ----------- | ------------- | ---------- | --------- |
    | data conversion | helpers/hcsv.py | convert_csv_to_pq | 191-216 | Convert CSV file to Parquet file. :param ...|
    | data conversion | helpers/hcsv.py | convert_csv_dir_to_pq_dir | 219-273 | Apply `convert_csv_to_pq()` to all files in `csv_dir`. :param ...|
    ```
    """
    df["Line Range"] = None
    df["Docstring"] = None
    for idx, row in df.iterrows():
        script_path = row["Script Path"]
        function_name = row["Function Name"]
        if not os.path.isfile(script_path):
            # Skip file if it does not exist.
            _LOG.warning("File not found: %s", script_path)
            continue
        # Extract line range and docstring for the function.
        line_range, doc = get_function_line_range_and_docstring(
            script_path, function_name
        )
        df.at[idx, "Line Range"] = line_range
        df.at[idx, "Docstring"] = doc
    return df


def write_markdown_table(df: pd.DataFrame, filepath: str) -> None:
    """
    Write a table of function metadata to a markdown-formatted file.

    :param df: table with function metadata (e.g., function type, script
        path, function name, line range, and docstring)
    :param filepath: path where the output markdown file will be saved
    """
    import tabulate
    df_out = df.copy().fillna("")
    df_out = df_out.map(lambda x: str(x).replace("\n", " ").replace("|", r"\|"))
    table_md = tabulate.tabulate(
        df_out,
        headers="keys",
        tablefmt="github",
        showindex=False,
        disable_numparse=True,
    )
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(table_md + "\n")
    _LOG.debug("Output written to: %s", filepath)
