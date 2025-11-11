# Intermediate v0 Timeseries Agent

This folder contains a compact LangGraph-powered agent (`v0agent.py`) plus the deterministic tools it orchestrates (`calculate_mean.py`, `calculate_median.py`, `detect_seasonality.py`, `detect_trends.py`). The agent loops until it compiles enough insights to emit a final report, writing both a notebook of steps and a JSONL trace so you can audit every decision.

## What `v0agent.py` Does

- Loads the target CSV, infers the datetime column (first column) and numeric measures, and seeds a `StateGraph` state with bookkeeping fields (`insights`, `thought_log`, `trace`, `notebook_cells`).
- Uses a structured-output LLM node to choose the next action:
  - `calculate_mean` / `calculate_median`: compute summary stats on a selected numeric column.
  - `detect_seasonality`: run autocorrelation-based checks for periodic behavior.
  - `detect_trends`: perform linear-regression trend classification across all numeric columns.
- Executes the requested tool via subprocess, ingests the JSON/string result, and appends markdown cells + trace entries for every turn.
- When the LLM decides it has enough context, it emits a markdown final report (and optional visualization requests), which ends the LangGraph loop.

## How to Run

1. Ensure the required dependencies exist (LangChain/OpenAI stack, pandas, scikit-learn, etc.) and that `OPENAI_API_KEY` is set in your environment.
2. Execute the agent with absolute or repo-relative dataset paths:

   ```bash
   python agentic_eda/intermediate_v0_timeseries_agent/v0agent.py \
     --path agentic_eda/T1_slice.csv \
     --question "Summarize key power and wind patterns." \
     --output agentic_eda/intermediate_v0_timeseries_agent/runs/T1_slice_run.ipynb \
     --trace agentic_eda/intermediate_v0_timeseries_agent/runs/T1_slice_run.jsonl
   ```

3. Inspect the generated notebook to review the markdown/tool outputs, and open the `.jsonl` trace for a structured event log (each line is a JSON object capturing the agent’s reasoning, tool payloads, and final report action).

The helper scripts can also run standalone (`python calculate_mean.py --path … --column …`) if you need to test them independently. The agent expects the CSV to have the timestamp as the first column, with numeric metrics following. Adjust the question prompt to steer which columns or analyses the LLM prioritizes.***
