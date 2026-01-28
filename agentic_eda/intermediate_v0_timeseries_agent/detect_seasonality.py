from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any

import helpers.hdatetime as hdatetime
import helpers.hlogging as hlogging
import helpers.hpandas as hpandas
import pandas as pd

try:
    import agentic_eda.intermediate_v0_timeseries_agent.calculate_mean as calculate_mean_module
except ModuleNotFoundError:  # pragma: no cover - fallback when run inside agentic_eda
    import calculate_mean as calculate_mean_module  # type: ignore

LOGGER = hlogging.getLogger(__name__)
AUTOCORR_THRESHOLD = 0.5
MIN_OBSERVATIONS = 8
MIN_LAG = 2
MAX_LAG_CAP = 365


def prepare_dataframe(csv_path: pathlib.Path, datetime_column: str) -> pd.DataFrame:
    """
    Load the CSV, align on the datetime index, and validate assumptions.

    :param csv_path: absolute path to the CSV file.
    :param datetime_column: column containing datetime values.
    :return: dataframe indexed by datetime.
    """
    dataframe = calculate_mean_module.read_dataframe(csv_path)
    if datetime_column not in dataframe.columns:
        raise KeyError(f"Datetime column '{datetime_column}' not found in the CSV file.")

    dataframe[datetime_column] = dataframe[datetime_column].apply(hdatetime.to_timestamp)
    dataframe = dataframe.dropna(subset=[datetime_column]).sort_values(datetime_column).set_index(datetime_column)
    hpandas.dassert_index_is_datetime(dataframe)
    return dataframe


def analyse_seasonality(series: pd.Series) -> dict[str, Any]:
    """
    Inspect autocorrelation scores to determine whether the signal is seasonal.

    :param series: numeric series indexed by datetime.
    :return: seasonality assessment including confidence and period where applicable.
    """
    if len(series) < MIN_OBSERVATIONS:
        return {"seasonal": False, "reason": "Insufficient observations to detect seasonality."}

    max_lag = min(len(series) // 4, MAX_LAG_CAP)
    if max_lag < MIN_LAG + 1:
        return {"seasonal": False, "reason": "Timeseries is too short to detect seasonality."}

    autocorrs = [(lag, series.autocorr(lag=lag)) for lag in range(MIN_LAG, max_lag)]
    valid_scores = [(lag, score) for lag, score in autocorrs if pd.notna(score)]
    if not valid_scores:
        return {"seasonal": False, "reason": "Could not calculate autocorrelation with the provided data."}

    peak_lag, peak_confidence = max(valid_scores, key=lambda item: item[1])
    response: dict[str, Any] = {"confidence": float(peak_confidence)}
    if peak_confidence > AUTOCORR_THRESHOLD:
        response.update({"seasonal": True, "period": int(peak_lag)})
        return response

    response.update({"seasonal": False})
    return response


def detect_seasonality(csv_path: pathlib.Path, column: str, datetime_column: str) -> dict[str, Any]:
    """
    Detect seasonality in a timeseries column of a CSV file.

    :param csv_path: absolute path to the CSV file.
    :param column: column to inspect for seasonal behaviour.
    :param datetime_column: column containing datetime values.
    :return: seasonality assessment payload.
    """
    dataframe = prepare_dataframe(csv_path, datetime_column)
    numeric_series = calculate_mean_module.extract_numeric_series(dataframe, column)
    return analyse_seasonality(numeric_series)


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.

    :return: parsed CLI arguments.
    """
    parser = argparse.ArgumentParser(description="Detect seasonality in a column of a CSV file.")
    parser.add_argument("--path", required=True, help="Absolute path to the CSV file.")
    parser.add_argument("--column", required=True, help="Name of the column to analyse.")
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
        result = detect_seasonality(pathlib.Path(args.path), args.column, args.datetime_column)
    except (FileNotFoundError, KeyError, TypeError, ValueError) as exc:
        LOGGER.error("%s", exc)
        print(json.dumps({"error": str(exc), "column": args.column, "datetime_column": args.datetime_column}))
        return 1

    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
