#!/usr/bin/env python
"""
Import as:

import src.main as smain
"""

import argparse
import json
import logging

import src.ingest.compute_temporal_stats as sctstats
import src.ingest.format_datetime as sfordat
import src.ingest.handle_inputs as shainp
import src.ingest.infer_structure as sinferstruct
import src.ingest.infer_type as sinfert
import src.ingest.integrity as sinteg
import src.quality_handling.audit_missingness as sauditmiss
import src.quality_handling.handle_missingness as shandlemiss
import src.quality_handling.standardize as sstandard
import src.univariate_analysis.test_transforms as stransforms
import src.univariate_analysis.univariate_metrics_plotting as sunivar

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
        choices=[
            "input",
            "format",
            "infer_type",
            "infer_structure",
            "compute_temporal_stats",
            "integrity",
            "audit_missingness",
            "handle_missingness",
            "standardize",
            "univariate_metrics_plotting",
            "test_transforms",
        ],
        help="Pipeline stage to execute.",
    )
    parser.add_argument(
        "--path",
        required=True,
        help="Path to dataset file.",
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
        payload = sinteg.run_integrity(args.path)
    elif mode == "infer_type":
        payload = sinfert.run_infer_type(args.path)
    elif mode == "infer_structure":
        payload = sinferstruct.run_infer_structure(args.path)
    elif mode == "compute_temporal_stats":
        payload = sctstats.run_compute_temporal_stats(args.path)
    elif mode == "audit_missingness":
        payload = sauditmiss.run_audit_missingness(args.path)
    elif mode == "handle_missingness":
        payload = shandlemiss.run_handle_missingness(args.path)
    elif mode == "standardize":
        payload = sstandard.run_standardize(args.path)
    elif mode == "univariate_metrics_plotting":
        payload = sunivar.run_univariate_metrics_plotting(args.path)
    elif mode == "test_transforms":
        payload = stransforms.run_test_transforms(args.path)
    else:
        raise ValueError(f"Unsupported mode='{mode}'")
    return payload


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    cli_args = _parse_args()
    output = _run_cli(cli_args)
    _LOG.info("Pipeline output: %s", json.dumps(output, default=str, indent=2))
