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
1. Ding, R., Han, S., Xu, Y., Zhang, H., & Zhang, D. (2019). QuickInsights: Quick and automatic discovery of insights from multi-dimensional data. *Proceedings of the 2019 International Conference on Management of Data (SIGMOD ’19)*. ACM. https://doi.org/10.1145/3299869.3314037  
2. Ma, P., Ding, R., Han, S., & Zhang, D. (2021). MetaInsight: Automatic discovery of structured knowledge for exploratory data analysis. *Proceedings of the 2021 International Conference on Management of Data (SIGMOD ’21)*. ACM. https://doi.org/10.1145/3448016.3457267  
3. Ma, P., Ding, R., Wang, S., Han, S., & Zhang, D. (2023). XInsight: eXplainable data analysis through the lens of causality. *Proceedings of the ACM on Management of Data, 1*(2), Article 156. https://doi.org/10.1145/3589301  
4. Ma, P., Ding, R., Wang, S., Han, S., & Zhang, D. (2023). InsightPilot: An LLM-empowered automated data exploration system. *arXiv preprint arXiv:2304.00477*.
