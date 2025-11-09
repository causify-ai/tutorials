# Plan for Mini-Timeseries Agent

This document outlines the plan for creating a small-scale agent that analyzes a timeseries CSV file. The agent will use a set of three deterministic tools to perform its analysis, orchestrated by a central agent script.

## 1. Project Structure

The project will consist of four main Python scripts:
- `v0agent.py`: The main agent loop that decides which tool to call.
- `calculate_mean.py`: A tool to calculate the mean of a timeseries column.
- `calculate_median.py`: A tool to calculate the median of a timeseries column.
- `detect_seasonality.py`: A tool to detect a dominant seasonal period in a timeseries column.

## 2. Script Designs

### `v0agent.py` - The Agent
- **Framework:** `langgraph` and `langchain` (similar to `testflow.py`).
- **State (`TimeSeriesState`):**
    - `csv_path`: Path to the input CSV.
    - `column_to_analyze`: The name of the column the agent is currently focused on.
    - `datetime_column`: The name of the timestamp column.
    - `scratchpad`: List of actions taken and results found.
    - `status`: 'ongoing' or 'done'.
    - `summary`: Final textual summary of the analysis.
- **Logic:**
    1.  Initialize with the path to a timeseries CSV.
    2.  The LLM agent node will first identify the numeric columns and the likely datetime column from the CSV. It will select one numeric column to start with.
    3.  In a loop, the agent will decide which tool (`mean`, `median`, `seasonality`) to call on the current column.
    4.  The result from the tool is added to the `scratchpad`.
    5.  The agent can decide to switch to another numeric column to continue its analysis.
    6.  When the agent determines it has enough information, it will set `status` to 'done' and populate the `summary`.
- **Tool Integration:** The agent will use `pydantic` models to structure its tool calls, which will be executed by the `langgraph` framework. The tool functions in `v0agent.py` will call the standalone scripts using `subprocess`.

### `calculate_mean.py` - Mean Tool
- **Interface:** Command-line script.
- **Arguments:**
    - `--path`: Absolute path to the CSV file.
    - `--column`: Name of the column to analyze.
- **Functionality:**
    - Reads the CSV into a pandas DataFrame.
    - Calculates the mean of the specified column.
    - Prints the mean value to standard output.

### `calculate_median.py` - Median Tool
- **Interface:** Command-line script.
- **Arguments:**
    - `--path`: Absolute path to the CSV file.
    - `--column`: Name of the column to analyze.
- **Functionality:**
    - Reads the CSV into a pandas DataFrame.
    - Calculates the median of the specified column.
    - Prints the median value to standard output.

### `detect_seasonality.py` - Seasonality Tool
- **Interface:** Command-line script.
- **Arguments:**
    - `--path`: Absolute path to the CSV file.
    - `--column`: Name of the value column.
    - `--datetime_column`: Name of the datetime column.
- **Functionality:**
    - Reads the CSV, parsing the datetime column and setting it as the index.
    - Calculates the autocorrelation of the value column for a range of lags.
    - Identifies the lag with the highest autocorrelation (ignoring lag 1).
    - If the peak autocorrelation is above a threshold (e.g., 0.5), it reports the lag as a potential seasonal period.
    - Prints a JSON string with the results, e.g., `{"seasonal": true, "period": 7, "confidence": 0.85}` or `{"seasonal": false}`.

## 3. Example Workflow
1.  User runs: `python agentic_eda/intermediate_v0_timeseries_agent/v0agent.py --path /path/to/T1_slice.csv`
2.  Agent starts, inspects `T1_slice.csv` and identifies `'LV ActivePower (kW)'` as the target column and `'Date/Time'` as the datetime column.
3.  **Turn 1:** Agent decides to get a baseline, calls `calculate_mean.py` on the column. Result is added to scratchpad.
4.  **Turn 2:** Agent calls `calculate_median.py`. Result is added to scratchpad.
5.  **Turn 3:** Agent calls `detect_seasonality.py`. Result (e.g., "seasonality detected at period X") is added to scratchpad.
6.  **Turn 4:** Agent decides it has a good overview (mean, median, seasonality) and generates a final summary. It sets `status` to 'done'.
7.  The graph terminates, and the final summary is printed.
