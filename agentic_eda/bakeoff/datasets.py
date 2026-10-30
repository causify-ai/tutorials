"""
Dataset registry for the Agentic EDA Bake-off.

Each dataset the agents are scored on is declared once here as a `Dataset`.
`load()` returns a pandas DataFrame. The four datasets are the ones named in
the Agentic Data Science track plan (Project 1).

Skeleton behavior (PR 1.1): `load()` returns a small, synthetic sample that
matches each real dataset's schema and task, so the whole harness runs end to
end with no network access. Wiring the real sources (download + cache into
`data/`) is a follow-up PR — the `source` URL and
`real_loader` hook mark exactly where that goes.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Callable, Optional

import numpy as np
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


@dataclass
class Dataset:
    name: str
    task: str                 # "classification" | "regression" | "text"
    target: Optional[str]     # target column, or None for unsupervised/EDA-only
    source: str               # where the real data comes from (for the real loader)
    description: str
    _sample: Callable[[], pd.DataFrame] = field(repr=False)
    real_loader: Optional[Callable[[], pd.DataFrame]] = field(default=None, repr=False)

    def load(self, real: bool = False) -> pd.DataFrame:
        """Return the dataset as a DataFrame.

        real=False (default): a synthetic sample matching the real schema, so the
        harness runs offline. real=True: the actual dataset, if a cached copy is in
        `data/` or a `real_loader` is wired; otherwise raises NotImplementedError
        naming the source so the gap is explicit, never silently faked.
        """
        if not real:
            return self._sample()
        cached = os.path.join(DATA_DIR, f"{self.name}.csv")
        if os.path.exists(cached):
            return pd.read_csv(cached)
        if self.real_loader is not None:
            return self.real_loader()
        raise NotImplementedError(
            f"Real data for '{self.name}' is not wired yet. "
            f"Add a cached CSV at {cached} or a real_loader. Source: {self.source}"
        )


# --- synthetic samples (schema-faithful, deterministic) --------------------
def _rng(seed: int) -> np.random.Generator:
    return np.random.default_rng(seed)


def _uci_heart_sample(n: int = 300, seed: int = 0) -> pd.DataFrame:
    r = _rng(seed)
    df = pd.DataFrame({
        "age": r.integers(29, 78, n),
        "sex": r.integers(0, 2, n),
        "cp": r.integers(0, 4, n),
        "trestbps": r.integers(94, 201, n),
        "chol": r.integers(126, 565, n),
        "thalach": r.integers(71, 203, n),
        "oldpeak": np.round(r.uniform(0, 6.2, n), 1),
    })
    # target correlated with a few features, so EDA has something real to find
    logit = -4 + 0.03 * df["age"] + 0.6 * df["cp"] - 0.03 * df["thalach"] + 0.5 * df["oldpeak"]
    df["target"] = (r.uniform(0, 1, n) < 1 / (1 + np.exp(-logit))).astype(int)
    return df


def _nyc_taxi_sample(n: int = 2000, seed: int = 1) -> pd.DataFrame:
    r = _rng(seed)
    dist = np.round(r.exponential(2.5, n) + 0.3, 2)
    passengers = r.integers(1, 5, n)
    base = 3.0 + 2.6 * dist + 0.4 * passengers + r.normal(0, 2, n)
    df = pd.DataFrame({
        "trip_distance": dist,
        "passenger_count": passengers,
        "pickup_hour": r.integers(0, 24, n),
        "fare_amount": np.round(np.clip(base, 2.5, None), 2),
    })
    return df


def _openaq_sample(n: int = 1500, seed: int = 2) -> pd.DataFrame:
    r = _rng(seed)
    cities = r.choice(["Delhi", "Beijing", "LA", "London", "Mexico City"], n)
    base = {"Delhi": 140, "Beijing": 95, "LA": 45, "London": 30, "Mexico City": 70}
    pm25 = np.array([base[c] for c in cities]) + r.normal(0, 15, n)
    df = pd.DataFrame({
        "city": cities,
        "pm25": np.round(np.clip(pm25, 1, None), 1),
        "temperature": np.round(r.normal(20, 8, n), 1),
        "humidity": r.integers(10, 100, n),
    })
    return df


def _amazon_reviews_sample(n: int = 1000, seed: int = 3) -> pd.DataFrame:
    r = _rng(seed)
    snippets = [
        "great product love it", "did not work as expected", "okay for the price",
        "absolutely fantastic would buy again", "broke after a week", "works fine",
    ]
    text = r.choice(snippets, n)
    # rating loosely tied to sentiment of the snippet
    pos = np.isin(text, snippets[:1] + snippets[3:4] + snippets[5:6])
    rating = np.where(pos, r.integers(4, 6, n), r.integers(1, 4, n))
    df = pd.DataFrame({
        "review_text": text,
        "rating": rating,
        "verified_purchase": r.integers(0, 2, n).astype(bool),
    })
    return df


# --- registry --------------------------------------------------------------
REGISTRY: dict[str, Dataset] = {
    d.name: d for d in [
        Dataset(
            name="uci_heart",
            task="classification",
            target="target",
            source="https://archive.ics.uci.edu/dataset/45/heart+disease",
            description="UCI Heart Disease; binary classification (~300 rows).",
            _sample=_uci_heart_sample,
        ),
        Dataset(
            name="nyc_taxi",
            task="regression",
            target="fare_amount",
            source="NYC TLC Yellow Taxi trip records (one month, sampled)",
            description="Taxi trips; regression on fare_amount.",
            _sample=_nyc_taxi_sample,
        ),
        Dataset(
            name="openaq",
            task="regression",
            target="pm25",
            source="https://openaq.org (air quality measurements API)",
            description="Air quality; regression on PM2.5.",
            _sample=_openaq_sample,
        ),
        Dataset(
            name="amazon_reviews",
            task="text",
            target="rating",
            source="Amazon Reviews 2023, All_Beauty subset",
            description="Product reviews; sentiment / rating prediction.",
            _sample=_amazon_reviews_sample,
        ),
    ]
}


def get_dataset(name: str) -> Dataset:
    if name not in REGISTRY:
        raise KeyError(f"Unknown dataset '{name}'. Known: {sorted(REGISTRY)}")
    return REGISTRY[name]


def all_datasets() -> list[Dataset]:
    return list(REGISTRY.values())
