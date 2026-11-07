"""
Agent interface for the Agentic EDA Bake-off.

Every contender — the existing `schema_agent`, the time-series agent in
`tutorials/agentic_eda`, AgenTUI, and external baselines like PandasAI — gets
wrapped so it presents the same two-method surface:

    name            : str
    run(dataset)    : -> AgentResult

That is the whole contract later PRs (1.2–1.5) implement. This module ships the
interface plus `DummyAgent`, a trivial-but-real agent that computes genuine
facts (shape, dtypes, strongest correlation) so the harness runs end to end
before any real agent is wired.
"""

from __future__ import annotations

import time
import traceback
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional

import numpy as np

import agentic_eda.bakeoff.datasets as aebdata


@dataclass
class AgentResult:
    """What an agent returns from one run on one dataset.

    insights : human-readable findings, one string each.
    artifacts: paths or in-memory objects the agent produced (plots, reports).
    code     : the analysis code the agent ran, if it emits any (for code-quality scoring in 1.6).
    error    : None on success; the exception text if the run failed.
    runtime_s: wall-clock seconds, filled in by `Agent.timed_run`.
    """
    insights: list[str] = field(default_factory=list)
    artifacts: list[Any] = field(default_factory=list)
    code: Optional[str] = None
    error: Optional[str] = None
    runtime_s: Optional[float] = None

    @property
    def ran_ok(self) -> bool:
        return self.error is None


class Agent(ABC):
    """Base class for every bake-off contender."""

    #: short, unique identifier used in the scorecard
    name: str = "agent"

    @abstractmethod
    def run(self, dataset: aebdata.Dataset) -> AgentResult:
        """Analyze `dataset` and return an AgentResult. Subclasses implement this."""
        raise NotImplementedError

    def timed_run(self, dataset: aebdata.Dataset) -> AgentResult:
        """Run the agent, timing it and catching failures so one bad agent
        never takes down the whole bake-off."""
        start = time.perf_counter()
        try:
            result = self.run(dataset)
        except Exception:
            result = AgentResult(error=traceback.format_exc())
        result.runtime_s = round(time.perf_counter() - start, 3)
        return result


class DummyAgent(Agent):
    """A real but minimal agent: it actually reads the data and reports a few
    true facts. Its only job is to prove the harness end to end; it is the
    floor every real agent should clear."""

    name = "dummy"

    def run(self, dataset: aebdata.Dataset) -> AgentResult:
        df = dataset.load()
        insights: list[str] = [
            f"{dataset.name}: {df.shape[0]} rows x {df.shape[1]} columns.",
            f"Columns: {', '.join(df.columns)}.",
        ]
        n_missing = int(df.isna().sum().sum())
        insights.append(f"Missing cells: {n_missing}.")

        num = df.select_dtypes("number")
        if num.shape[1] >= 2:
            corr = num.corr().abs()
            # Strongest off-diagonal correlation.
            m = corr.to_numpy().copy()
            np.fill_diagonal(m, 0.0)
            i, j = np.unravel_index(m.argmax(), m.shape)
            insights.append(
                f"Strongest numeric correlation: {corr.columns[i]} ~ {corr.columns[j]} "
                f"(|r| = {m[i, j]:.2f})."
            )
        return AgentResult(insights=insights, code="# DummyAgent: describe + top correlation")


def all_agents() -> list[Agent]:
    """The agents entered in the bake-off. PRs 1.2–1.5 append their wrappers here."""
    return [DummyAgent()]
