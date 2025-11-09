# Attempted InsightPilot Recreation

This folder is an attempted reconstruction of the InsightPilot workflow described across the QuickInsights (SIGMOD'19), MetaInsight (SIGMOD'21), XInsight (SIGMOD'23), and InsightPilot (NeurIPS Datasets & Benchmarks) papers. The goal is to mirror the orchestration patterns while keeping the code inspectable and runnable inside this repository.

## Core Scripts

### 1. `qin.py` — QuickInsights Attempt
- Implements the mining loop from **QuickInsights-camera-ready-final.pdf**: schema guessing, task search, evaluator scoring, and Top‑K buffering.
- Produces `Insight` dataclasses (`InsightSubject`, `highlight`) that downstream engines can reuse without re-mining.
- CLI usage:
  ```bash
  python agentic_eda/advanced_insightpilot_recreation/qin.py \
    --path agentic_eda/T1_slice.csv \
    --max-insights 10 \
    --json-out /tmp/qi.json
  ```

### 2. `metain.py` — MetaInsight Attempt
- Recreates the commonness/exceptions summariser from **MetaInsight.pdf** by grouping QuickInsights output into homogeneous scopes and evaluating Trend/Unimodality/Outlier patterns.
- Depends on `qin.Insight` structures instead of recomputing stats.
- CLI usage:
  ```bash
  python agentic_eda/advanced_insightpilot_recreation/metain.py \
    --path agentic_eda/T1_slice.csv \
    --question "Power vs wind" \
    --max-insights 10
  ```

### 3. `xin.py` — XInsight Attempt
- Follows the predicate-search logic from **XInsight-final.pdf** to explain gaps between two sibling subspaces via causal-style filters.
- Exposes a CLI `explain_difference` replica:
  ```bash
  python agentic_eda/advanced_insightpilot_recreation/xin.py \
    --path agentic_eda/T1_slice.csv \
    --dimension Hour \
    --left q4 \
    --right q1 \
    --measure "LV ActivePower (kW)" \
    --agg avg
  ```

### 4. `insightpilot.py` — LangGraph Orchestrator Attempt
- Inspired by **InsightPilot.pdf**, this script wires QuickInsights/MetaInsight/XInsight into a LangGraph `StateGraph` loop that streams notebook cells and final reports.
- Adds pragmatic guardrails (filter sanitising, temporal feature synthesis, max-step budget) so runs stay reproducible within this repo.
- CLI usage:
  ```bash
  python agentic_eda/advanced_insightpilot_recreation/insightpilot.py \
    --path agentic_eda/T1_slice.csv \
    --question "Analyze wind power patterns" \
    --output /tmp/insightpilot_run.ipynb \
    --trace /tmp/insightpilot_run.jsonl
  ```

## Usage Notes
- Set `OPENAI_API_KEY` for any command that touches `insightpilot.py` (it defaults to `gpt-4o` but you can override with `--model`).
- Each tool script can run independently for debugging, yet `insightpilot.py` expects them to reside in this package so imports stay relative.
- Sample `_slice` datasets (`T1_slice.csv`, `FRED_slice.csv`, `PEMS_slice.csv`) are handy for quick verification runs; the tests in `agentic_eda/test/test_insight_engines.py` exercise the same flows.

## References
1. QuickInsights-camera-ready-final.pdf  
2. MetaInsight.pdf  
3. XInsight-final.pdf  
4. InsightPilot.pdf
