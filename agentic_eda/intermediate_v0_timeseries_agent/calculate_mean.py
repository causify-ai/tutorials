
from __future__ import annotations

import argparse
import json
import logging
import pathlib

import helpers.hlogging as hlogging
import pandas as pd

LOGGER = hlogging.getLogger(__name__)
CSV_SKIPROWS = [1]


def configure_logging() -> None:
    """
    Initialise a basic logging configuration if none exists.
    """
    if logging.getLogger().handlers:
        return
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")


def read_dataframe(csv_path: pathlib.Path) -> pd.DataFrame:
    """
    Read the CSV file while applying repo-specific parsing defaults.

    :param csv_path: absolute path to the CSV file.
    :return: dataframe parsed from the CSV content.
    """
    try:
        return pd.read_csv(csv_path, skiprows=CSV_SKIPROWS)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"CSV file not found: {csv_path}") from exc
    except pd.errors.EmptyDataError as exc:
        raise ValueError(f"CSV file is empty: {csv_path}") from exc
    except pd.errors.ParserError as exc:
        raise ValueError(f"Failed to parse CSV file: {csv_path}") from exc


def extract_numeric_series(dataframe: pd.DataFrame, column: str) -> pd.Series:
    """
    Return the numeric series for the requested column.

    :param dataframe: dataframe loaded from the CSV file.
    :param column: column name whose numeric values need to be analysed.
    :return: numeric series with NaNs removed.
    """
    if column not in dataframe.columns:
        raise KeyError(f"Column '{column}' not found in the CSV file.")

    series = dataframe[column]
    if not pd.api.types.is_numeric_dtype(series):
        raise TypeError(f"Column '{column}' is not numeric.")

    numeric_series = pd.to_numeric(series, errors="coerce").dropna()
    if numeric_series.empty:
        raise ValueError(f"Column '{column}' has no valid numeric values.")
    return numeric_series


def calculate_mean(csv_path: pathlib.Path, column: str) -> float:
    """
    Compute the mean value for the selected column.

    :param csv_path: absolute path to the CSV file.
    :param column: column name to analyse.
    :return: mean of the numeric series.
    """
    dataframe = read_dataframe(csv_path)
    numeric_series = extract_numeric_series(dataframe, column)
    return float(numeric_series.mean())


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.

    :return: parsed CLI arguments.
    """
    parser = argparse.ArgumentParser(description="Calculate the mean of a column in a CSV file.")
    parser.add_argument("--path", required=True, help="Absolute path to the CSV file.")
    parser.add_argument("--column", required=True, help="Name of the column to analyse.")
    return parser.parse_args()


def main() -> int:
    """
    Run the CLI entry point.

    :return: zero on success, non-zero otherwise.
    """
    args = parse_args()
    configure_logging()

    try:
        mean_value = calculate_mean(pathlib.Path(args.path), args.column)
    except (FileNotFoundError, KeyError, TypeError, ValueError) as exc:
        LOGGER.error("%s", exc)
        print(json.dumps({"column": args.column, "error": str(exc)}))
        return 1

    print(json.dumps({"column": args.column, "mean": mean_value}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
