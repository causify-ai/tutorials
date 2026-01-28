from __future__ import annotations

import argparse
import json
import pathlib

import helpers.hdataframe as hdataframe
import helpers.hdatetime as hdatetime
import helpers.hlogging as hlogging
import numpy as np
import pandas as pd
import sklearn.linear_model as sk_linear_model

try:
    import agentic_eda.intermediate_v0_timeseries_agent.calculate_mean as calculate_mean_module
except ModuleNotFoundError:  # pragma: no cover - fallback when run inside agentic_eda
    import calculate_mean as calculate_mean_module  # type: ignore

LOGGER = hlogging.getLogger(__name__)
NORMALISED_SLOPE_TOLERANCE = 1e-3


def prepare_dataframe(csv_path: pathlib.Path, datetime_column: str) -> pd.DataFrame:
    """
    Load the CSV, align on the datetime index, and validate assumptions.

    :param csv_path: absolute path to the CSV file.
    :param datetime_column: column containing datetime values.
    :return: dataframe sorted by datetime and indexed accordingly.
    """
    dataframe = calculate_mean_module.read_dataframe(csv_path)
    if datetime_column not in dataframe.columns:
        raise KeyError(f"Datetime column '{datetime_column}' not found in the CSV file.")

    dataframe[datetime_column] = dataframe[datetime_column].apply(hdatetime.to_timestamp)
    return dataframe.dropna(subset=[datetime_column]).sort_values(datetime_column).set_index(datetime_column)


def classify_trend(series: pd.Series) -> str:
    """
    Classify the trend of a numeric series using a simple linear regression.

    :param series: numeric series indexed by datetime.
    :return: trend label: increasing, decreasing, or uniform.
    """
    clean_series = hdataframe.apply_nan_mode(series, mode="drop")
    if len(clean_series) < 2:
        return "uniform"

    predictors = np.arange(len(clean_series), dtype=float).reshape(-1, 1)
    model = sk_linear_model.LinearRegression()
    model.fit(predictors, clean_series)
    slope = float(model.coef_[0])

    value_range = float(clean_series.max() - clean_series.min())
    normalised_slope = slope / value_range if value_range > 0 else 0.0

    if abs(normalised_slope) < NORMALISED_SLOPE_TOLERANCE:
        return "uniform"
    return "increasing" if slope > 0 else "decreasing"


def detect_trends(csv_path: pathlib.Path, datetime_column: str) -> dict[str, str]:
    """
    Detect monotonic trends across all numeric columns of the dataset.

    :param csv_path: absolute path to the CSV file.
    :param datetime_column: column containing datetime values.
    :return: mapping of column names to their trend classification.
    """
    dataframe = prepare_dataframe(csv_path, datetime_column)
    numeric_columns = list(dataframe.select_dtypes(include=np.number).columns)
    if not numeric_columns:
        raise ValueError("No numeric columns found.")

    return {column: classify_trend(dataframe[column]) for column in numeric_columns}


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.

    :return: parsed CLI arguments.
    """
    parser = argparse.ArgumentParser(description="Detect trends in numeric columns of a CSV file.")
    parser.add_argument("--path", required=True, help="Absolute path to the CSV file.")
    parser.add_argument("--datetime_column", required=True, help="Name of the datetime column.")
    return parser.parse_args()


def main() -> int:
    """
    Run the CLI entry point.

    :return: zero on success, non-zero otherwise.
    """
    args = parse_args()
    calculate_mean_module.configure_logging()

    try:
        result = detect_trends(pathlib.Path(args.path), args.datetime_column)
    except (FileNotFoundError, KeyError, ValueError) as exc:
        LOGGER.error("%s", exc)
        print(json.dumps({"error": str(exc), "datetime_column": args.datetime_column}))
        return 1

    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
