#!/usr/bin/env python
"""
Import as:

import src.main as smain
"""

import argparse
import json
import logging

import src.format_datetime as sfordat
import src.handle_inputs as shainp
import src.integrity as sinteg

_LOG = logging.getLogger(__name__)


def _parse_args() -> argparse.Namespace:
    """
    Parse CLI arguments.

    :return: parsed arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        required=True,
        choices=["input", "format", "integrity"],
        help="Pipeline stage to execute.",
    )
    parser.add_argument(
        "--path",
        required=True,
        help="Path to dataset file.",
    )
    parser.add_argument(
        "--time_col",
        default=None,
        help="Optional time column override for integrity mode.",
    )
    parser.add_argument(
        "--entity_col",
        default=None,
        help="Optional entity column for integrity mode.",
    )
    args = parser.parse_args()
    return args


def _run_cli(args: argparse.Namespace) -> dict:
    """
    Execute selected backend stage.

    :param args: parsed CLI args
    :return: stage output payload
    """
    mode = args.mode
    if mode == "input":
        payload = shainp.run_input_handler(args.path)
    elif mode == "format":
        payload = sfordat.run_date_formatter(args.path)
    elif mode == "integrity":
        payload = sinteg.run_integrity(
            args.path,
            time_col=args.time_col,
            entity_col=args.entity_col,
        )
    else:
        raise ValueError(f"Unsupported mode='{mode}'")
    return payload


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    cli_args = _parse_args()
    output = _run_cli(cli_args)
    _LOG.info("Pipeline output: %s", json.dumps(output, default=str, indent=2))
