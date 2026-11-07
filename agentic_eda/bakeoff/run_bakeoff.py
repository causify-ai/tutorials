#!/usr/bin/env python3
"""
Run the Agentic EDA Bake-off: every registered agent on every registered dataset.

Usage:
> run_bakeoff.py --list
> run_bakeoff.py --run
> run_bakeoff.py --run --agent dummy --dataset uci_heart

`--run` times each (agent, dataset) pair, records failures instead of aborting,
prints the scorecard, and writes it to `results/scorecard.csv`.
"""

import argparse
import logging
import sys
from typing import List, Optional

import helpers.hdbg as hdbg
import helpers.hparser as hparser

import agentic_eda.bakeoff.agents as aebagent
import agentic_eda.bakeoff.datasets as aebdata
import agentic_eda.bakeoff.scoring as aebscor

_LOG = logging.getLogger(__name__)


def _list() -> None:
    """
    Print the registered datasets and agents.
    """
    datasets = aebdata.all_datasets()
    agents = aebagent.all_agents()
    print(f"Datasets ({len(datasets)}):")
    for d in datasets:
        tgt = f", target={d.target}" if d.target else ""
        print(f"  - {d.name:16s} [{d.task}{tgt}]  {d.description}")
    print(f"\nAgents ({len(agents)}):")
    for a in agents:
        print(f"  - {a.name}")


def _run(
    agent_name: Optional[str], dataset_name: Optional[str]
) -> aebscor.Scorecard:
    """
    Run the selected agents on the selected datasets and save the scorecard.

    :param agent_name: run only this agent; None runs all
    :param dataset_name: run only on this dataset; None runs on all
    :return: the scorecard
    """
    agents = [a for a in aebagent.all_agents() if agent_name in (None, a.name)]
    if not agents:
        sys.exit(f"No agent matched '{agent_name}'.")
    if dataset_name:
        datasets = [aebdata.get_dataset(dataset_name)]
    else:
        datasets = aebdata.all_datasets()
    card = aebscor.Scorecard()
    for agent in agents:
        for ds in datasets:
            _LOG.info("Running %s on %s", agent.name, ds.name)
            res = agent.timed_run(ds)
            card.add(
                aebscor.ScoreRow(
                    agent=agent.name,
                    dataset=ds.name,
                    task=ds.task,
                    runs_ok=res.ran_ok,
                    runtime_s=res.runtime_s,
                    n_insights=len(res.insights),
                    error=(res.error.splitlines()[-1] if res.error else None),
                )
            )
    print("SCORECARD")
    print(card)
    path = card.save()
    print(f"\nSaved to {path}")
    return card


def _parse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--list", action="store_true", help="List datasets and agents"
    )
    parser.add_argument("--run", action="store_true", help="Run the bake-off")
    parser.add_argument("--agent", help="Restrict to one agent by name")
    parser.add_argument("--dataset", help="Restrict to one dataset by name")
    hparser.add_verbosity_arg(parser)
    return parser


def _main(parser: argparse.ArgumentParser, argv: Optional[List[str]] = None) -> None:
    args = parser.parse_args(argv)
    hdbg.init_logger(verbosity=args.log_level, use_exec_path=True)
    if args.list:
        _list()
    elif args.run:
        _run(args.agent, args.dataset)
    else:
        parser.print_help()


if __name__ == "__main__":
    _main(_parse())
