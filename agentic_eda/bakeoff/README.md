# Agentic EDA Bake-off

This harness runs several EDA agents over the same datasets and records the
results in one scorecard. It is Project 1 of the Agentic Data Science track
(`research/agentic_data_science/track_plan.md` in `gpsaggese.github.io`).

Each existing agent, plus a couple of external baselines, gets wrapped behind
one interface. The harness then runs all of them on a fixed set of datasets and
produces a single table that compares them.

## Usage

From the repo root (inside the dev container):

```bash
python agentic_eda/bakeoff/run_bakeoff.py --list
python agentic_eda/bakeoff/run_bakeoff.py --run
python agentic_eda/bakeoff/run_bakeoff.py --run --agent dummy --dataset uci_heart
pytest agentic_eda/bakeoff/test
```

`--run` writes `results/scorecard.csv`.

## Layout

| File | Contents |
|---|---|
| `datasets.py` | `Dataset` and the registry of the four datasets |
| `agents.py` | `Agent` interface, `AgentResult`, `DummyAgent` |
| `scoring.py` | `Scorecard` / `ScoreRow`, CSV output |
| `run_bakeoff.py` | CLI |
| `data/` | local cache for real datasets (not committed) |
| `results/` | run outputs (not committed) |

## Interfaces

An agent implements `name` and `run(dataset) -> AgentResult`. The harness calls
`agent.timed_run(dataset)`, which times the run and turns an exception into a
recorded failure, so one broken agent does not stop the bake-off.

For each (agent, dataset) pair, the scorecard records `runs_ok`, `runtime_s`,
`n_insights` and the error. The `insight_quality` and `code_quality` columns are
already in the schema but stay blank until the scoring PR fills them.

## Datasets

The four datasets are `uci_heart` (classification), `nyc_taxi` (regression),
`openaq` (regression) and `amazon_reviews` (text). `load()` returns a small
synthetic sample with the real schema, so everything runs offline.
`load(real=True)` reads `data/<name>.csv` or a wired `real_loader`. If neither
exists it raises, naming the source.

## Adding an agent

1. Subclass `Agent` with a wrapper that adapts the existing agent
   (`schema_agent`, `intermediate_v0_timeseries_agent`, AgenTUI, PandasAI) to
   `run(dataset) -> AgentResult`.
2. Add it to `agents.all_agents()`.
3. Run `run_bakeoff.py --run`. The new agent appears in the scorecard.
