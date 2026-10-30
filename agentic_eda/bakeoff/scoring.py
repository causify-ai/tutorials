"""
Scorecard for the Agentic EDA Bake-off.

One `ScoreRow` per (agent, dataset) run. PR 1.1 records only the objective,
automatically-measurable fields — did it run, how long it took, how many
insights it produced. The judgment columns (`insight_quality`, `code_quality`)
are declared here but left as None; PR 1.6 fills them with a rubric/LLM judge.
Keeping the columns present now means the CSV schema does not change when
scoring lands.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field, asdict
from typing import Optional

import pandas as pd

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")

COLUMNS = [
    "agent", "dataset", "task",
    "runs_ok", "runtime_s", "n_insights",
    "insight_quality", "code_quality",  # filled in PR 1.6
    "error",
]


@dataclass
class ScoreRow:
    agent: str
    dataset: str
    task: str
    runs_ok: bool
    runtime_s: Optional[float]
    n_insights: int
    insight_quality: Optional[float] = None   # PR 1.6
    code_quality: Optional[float] = None       # PR 1.6
    error: Optional[str] = None


@dataclass
class Scorecard:
    rows: list[ScoreRow] = field(default_factory=list)

    def add(self, row: ScoreRow) -> None:
        self.rows.append(row)

    def to_frame(self) -> pd.DataFrame:
        if not self.rows:
            return pd.DataFrame(columns=COLUMNS)
        df = pd.DataFrame([asdict(r) for r in self.rows])
        return df[COLUMNS]

    def save(self, path: Optional[str] = None) -> str:
        os.makedirs(RESULTS_DIR, exist_ok=True)
        path = path or os.path.join(RESULTS_DIR, "scorecard.csv")
        self.to_frame().to_csv(path, index=False)
        return path

    def __str__(self) -> str:
        df = self.to_frame()
        if df.empty:
            return "(empty scorecard — no runs recorded)"
        # error text is noisy in a table; show a boolean and keep full text in the CSV
        show = df.drop(columns=["error"]).copy()
        return show.to_string(index=False)
