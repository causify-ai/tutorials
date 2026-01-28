from __future__ import annotations

import argparse
import json
import pathlib

import helpers.hlogging as hlogging

try:
    import agentic_eda.intermediate_v0_timeseries_agent.calculate_mean as calculate_mean_module
except ModuleNotFoundError:  # pragma: no cover - fallback when run inside agentic_eda
    import calculate_mean as calculate_mean_module  # type: ignore

LOGGER = hlogging.getLogger(__name__)


def calculate_median(csv_path: pathlib.Path, column: str) -> float:
    """
    Compute the median value for the selected column.

    :param csv_path: absolute path to the CSV file.
    :param column: column name to analyse.
    :return: median of the numeric series.
    """
    dataframe = calculate_mean_module.read_dataframe(csv_path)
    numeric_series = calculate_mean_module.extract_numeric_series(dataframe, column)
    return float(numeric_series.median())


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.

    :return: parsed CLI arguments.
    """
    parser = argparse.ArgumentParser(description="Calculate the median of a column in a CSV file.")
    parser.add_argument("--path", required=True, help="Absolute path to the CSV file.")
    parser.add_argument("--column", required=True, help="Name of the column to analyse.")
    return parser.parse_args()


def main() -> int:
    """
    Run the CLI entry point.

    :return: zero on success, non-zero otherwise.
    """
    args = parse_args()
    calculate_mean_module.configure_logging()

    try:
        median_value = calculate_median(pathlib.Path(args.path), args.column)
    except (FileNotFoundError, KeyError, TypeError, ValueError) as exc:
        LOGGER.error("%s", exc)
        print(json.dumps({"column": args.column, "error": str(exc)}))
        return 1

    print(json.dumps({"column": args.column, "median": median_value}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
