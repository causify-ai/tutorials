#!/usr/bin/env python3
"""
Extract function context and enrich a Markdown table.

This script reads a Markdown table containing function metadata and appends
the source line range and docstring of each function by parsing the original script files.

Usage:
> generate_EDA_context.py --i ABC.md --o XYZ.md

Example input (Markdown table):

| Function Type   | Script Path     | Function Name             |
|-----------------|-----------------|---------------------------|
| data conversion | helpers/hcsv.py | convert_csv_to_pq         |
| data conversion | helpers/hcsv.py | convert_csv_dir_to_pq_dir |

Example output (Markdown table):

| Function Type | Script Path | Function Name | Line Range | Docstring |
| ------------- | ----------- | ------------- | ---------- | --------- |
| data conversion | helpers/hcsv.py | convert_csv_to_pq | 191-216 | Convert CSV file to Parquet file. :param ...|
| data conversion | helpers/hcsv.py | convert_csv_dir_to_pq_dir | 219-273 | Apply `convert_csv_to_pq()` to all files in `csv_dir`. :param ...|
"""

import argparse
import logging

import helpers.hdbg as hdbg
import helpers.hparser as hparser

import agentic_eda.generate_EDA_context_utils as aegecout

_LOG = logging.getLogger(__name__)


# #############################################################################
# CLI entry point
# #############################################################################


def _enrich_markdown_file(in_file: str, out_file: str) -> None:
    """
    Enrich a Markdown function table with each function's line range and
    docstring.

    This function:
    - Reads a given Markdown table `in_file`
    - Scans the referenced Python files to find each function and extract its line range and docstring
    - Adds 'Line Range' and 'Docstring' columns to the table
    - Writes the output Markdown table to `out_file`

    :param in_file: path to the given Markdown file
    :param out_file: path where the output markdown file will be saved
    """
    df = aegecout.read_function_table(in_file)
    required_col = {"Function Type", "Script Path", "Function Name"}
    hdbg.dassert_is_subset(required_col, df.columns)
    df = aegecout.enrich_function_table(df)
    aegecout.write_markdown_table(df, out_file)


def _parse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "-i",
        "--in_file",
        required=True,
        help="Path to input markdown table",
    )
    parser.add_argument(
        "-o",
        "--out_file",
        required=True,
        help="Path to output enriched markdown table",
    )
    hparser.add_verbosity_arg(parser)
    return parser


def _main(parser: argparse.ArgumentParser) -> None:
    args = parser.parse_args()
    hdbg.init_logger(verbosity=args.log_level, use_exec_path=True)
    _enrich_markdown_file(args.in_file, args.out_file)


if __name__ == "__main__":
    _main(_parse())
