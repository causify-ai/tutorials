# databricks_cli_utils.py

"""
Utilities for real-time Bitcoin price analysis using the Databricks CLI.

This module provides:
- subprocess-based wrappers around the Databricks CLI
- functions to fetch and parse Bitcoin price data
- ARIMA modeling and forecast generation
- plotting helpers for historical and forecast data
"""

__all__ = [
    "_run_databricks_cli",
    "create_cluster_cli",
    "get_cluster_status_cli",
    "upload_to_dbfs_cli",
    "download_from_dbfs_cli",
    "submit_notebook_job_cli",
    "get_job_run_status_cli",
    "delete_cluster_cli",
    "fetch_bitcoin_data",
    "parse_local_json_data",
    "train_arima_model",
    "get_forecast",
    "plot_historical_data",
    "plot_forecast_data",
    "submit_notebook_run_cli",
]


import subprocess
import json
import os
import time
import logging
import shlex
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple

import requests
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import matplotlib.pyplot as plt
from config.settings import COINGECKO_PRICE_URL

_LOG = logging.getLogger(__name__)
if not logging.getLogger().hasHandlers():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# === Databricks CLI Interaction ===

def _run_databricks_cli(command_list: List[str]) -> Dict[str, Any]:
    """Execute a Databricks CLI command and return a result dict."""
    _LOG.debug("Running Databricks CLI command: %s", shlex.join(command_list))
    result = {"success": False, "output": None, "raw_stdout": "", "stderr": "", "error": None}
    try:
        process = subprocess.run(
            command_list,
            capture_output=True,
            text=True,
            check=False,
            encoding='utf-8'
        )
        result["raw_stdout"] = process.stdout.strip()
        result["stderr"] = process.stderr.strip()

        if process.returncode == 0:
            _LOG.debug("CLI command successful.")
            try:
                result["output"] = json.loads(result["raw_stdout"])
                result["success"] = True
                _LOG.debug("Parsed JSON output.")
            except json.JSONDecodeError:
                result["success"] = True
                _LOG.debug("Command successful, output is not JSON.")
        else:
            result["error"] = f"CLI command failed with exit code {process.returncode}. Stderr: {result['stderr']}"
            _LOG.error(result["error"])

    except FileNotFoundError:
        result["error"] = "'databricks' command not found."
        _LOG.exception(result["error"])
    except Exception as e:
        result["error"] = f"An unexpected error occurred: {e}"
        _LOG.exception(result["error"])

    return result

def create_cluster_cli(config_file: str = "config/cluster_config.json", cluster_id_file: str = "config/cluster_id.txt") -> Optional[str]:
    """Create a Databricks cluster via CLI, save its ID, and return it."""
    if not os.path.exists(config_file):
        _LOG.error("Cluster config file not found: %s", config_file)
        return None

    command = ['databricks', 'clusters', 'create', '--json-file', config_file]
    result = _run_databricks_cli(command)

    if result["success"] and isinstance(result["output"], dict) and "cluster_id" in result["output"]:
        cluster_id = result["output"]["cluster_id"]
        _LOG.info("Submitted cluster creation. ID: %s", cluster_id)
        try:
            os.makedirs(os.path.dirname(cluster_id_file), exist_ok=True)
            with open(cluster_id_file, 'w') as f:
                f.write(cluster_id)
            _LOG.info("Saved cluster ID to %s", cluster_id_file)
            return cluster_id
        except IOError as e:
            _LOG.error("Failed to save cluster ID to %s: %s", cluster_id_file, e)
            return None
    else:
        _LOG.error("Failed to create cluster. Error: %s", result.get("error", "Unknown"))
        return None

def get_cluster_status_cli(cluster_id: str) -> Optional[str]:
    """Gets the status of a Databricks cluster via CLI."""
    if not cluster_id:
        _LOG.error("Invalid cluster_id.")
        return None
    command = ['databricks', 'clusters', 'get', '--cluster-id', cluster_id]
    result = _run_databricks_cli(command)

    if result["success"] and isinstance(result["output"], dict) and "state" in result["output"]:
        status = result["output"]["state"]
        _LOG.info("Cluster '%s' status: %s", cluster_id, status)
        return status
    else:
        _LOG.error("Failed to get status for cluster '%s'. Error: %s", cluster_id, result.get("error", "Unknown"))
        return None

def upload_to_dbfs_cli(local_path: str, dbfs_path: str, overwrite: bool = True) -> bool:
    """Uploads a local file to DBFS via CLI."""
    if not os.path.exists(local_path):
        _LOG.error("Local file not found for upload: %s", local_path)
        return False

    command = ['databricks', 'fs', 'cp', local_path, dbfs_path]
    if overwrite:
        command.append('--overwrite')

    result = _run_databricks_cli(command)
    if result["success"]:
        _LOG.info("Uploaded '%s' to '%s'", local_path, dbfs_path)
        return True
    else:
        _LOG.error("Failed upload '%s' to '%s'. Error: %s", local_path, dbfs_path, result.get("error", "Unknown"))
        return False

def download_from_dbfs_cli(dbfs_path: str, local_path: str, overwrite: bool = True) -> bool:
    """Downloads a file from DBFS via CLI."""
    local_dir = os.path.dirname(local_path)
    if local_dir:
        os.makedirs(local_dir, exist_ok=True)

    command = ['databricks', 'fs', 'cp', dbfs_path, local_path]
    if overwrite:
        command.append('--overwrite')

    result = _run_databricks_cli(command)
    if result["success"]:
        _LOG.info("Downloaded '%s' to '%s'", dbfs_path, local_path)
        return True
    else:
        _LOG.error("Failed download '%s' to '%s'. Error: %s", dbfs_path, local_path, result.get("error", "Unknown"))
        if os.path.exists(local_path) and os.path.getsize(local_path) == 0:
             try:
                 os.remove(local_path)
             except OSError:
                 pass
        return False

def submit_notebook_job_cli(job_id: str) -> Optional[str]:
    """Submits a pre-defined Databricks Job via CLI."""
    if not job_id:
        _LOG.error("Invalid job_id.")
        return None
    command = ['databricks', 'jobs', 'run-now', '--job-id', job_id]
    result = _run_databricks_cli(command)

    if result["success"] and isinstance(result["output"], dict) and "run_id" in result["output"]:
        run_id = str(result["output"]["run_id"])
        _LOG.info("Submitted job '%s'. Run ID: %s", job_id, run_id)
        return run_id
    else:
        _LOG.error("Failed to submit job '%s'. Error: %s", job_id, result.get("error", "Unknown"))
        return None

def get_job_run_status_cli(run_id: str) -> Optional[Dict[str, str]]:
    """Gets the status of a Databricks job run via CLI."""
    if not run_id:
        _LOG.error("Invalid run_id.")
        return None
    command = ['databricks', 'runs', 'get', '--run-id', run_id]
    result = _run_databricks_cli(command)

    if result["success"] and isinstance(result["output"], dict) and "state" in result["output"]:
        state = result["output"]["state"]
        _LOG.info("Job run '%s' status: %s", run_id, state.get("life_cycle_state", "N/A"))
        return state
    else:
        _LOG.error("Failed get status for job run '%s'. Error: %s", run_id, result.get("error", "Unknown"))
        return None

def delete_cluster_cli(cluster_id: str) -> bool:
    """Deletes a Databricks cluster via CLI."""
    if not cluster_id:
        _LOG.error("Invalid cluster_id for deletion.")
        return False
    command = ['databricks', 'clusters', 'delete', '--cluster-id', cluster_id]
    result = _run_databricks_cli(command)

    if result["success"]:
        _LOG.info("Submitted deletion request for cluster '%s'", cluster_id)
        return True
    else:
        stderr = result.get("stderr", "").lower()
        if "cluster does not exist" in stderr or "unexpected state terminated" in stderr:
             _LOG.warning("Cluster '%s' might already be gone.", cluster_id)
             return True
        _LOG.error("Failed delete cluster '%s'. Error: %s", cluster_id, result.get("error", "Unknown"))
        return False

# === Data Fetching ===

def fetch_bitcoin_data(api_url: str = COINGECKO_PRICE_URL,
                       output_dir: str = "data",
                       output_filename: str = "bitcoin_price.json") -> Optional[str]:
    """Fetches Bitcoin price and appends to a local JSON file."""
    output_path = os.path.join(output_dir, output_filename)
    try:
        res = requests.get(api_url, timeout=10)
        res.raise_for_status()
        data = res.json()

        if 'bitcoin' in data and 'usd' in data['bitcoin']:
            price = data['bitcoin']['usd']
            time_now = datetime.utcnow().isoformat()
            record = {"timestamp": time_now, "price": price}

            os.makedirs(output_dir, exist_ok=True)
            with open(output_path, "a") as f:
                f.write(json.dumps(record) + "\n")

            _LOG.info(f"Fetched/saved Bitcoin price: ${price} to {output_path}")
            return output_path
        else:
            _LOG.warning("Unexpected API response format: %s", data)
            return None

    except requests.exceptions.RequestException as e:
        _LOG.error("HTTP request failed fetching data: %s", e)
        return None
    except Exception as e:
        _LOG.error("Error fetching/saving data: %s", e)
        return None

# === Data Processing and Analysis ===

def parse_local_json_data(local_json_path: str) -> Optional[pd.DataFrame]:
    """Parses line-delimited JSON into a cleaned pandas DataFrame."""
    if not os.path.exists(local_json_path):
        _LOG.error("Local JSON file not found: %s", local_json_path)
        return None
    try:
        records = []
        with open(local_json_path, 'r') as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))

        if not records:
             _LOG.warning("No records found in %s", local_json_path)
             return None

        pdf = pd.DataFrame(records)
        pdf['timestamp'] = pd.to_datetime(pdf['timestamp'], errors='coerce')
        pdf['price'] = pd.to_numeric(pdf['price'], errors='coerce')
        pdf.dropna(subset=['timestamp', 'price'], inplace=True)
        pdf = pdf.sort_values('timestamp')
        pdf = pdf.drop_duplicates(subset=['timestamp'], keep='last')
        pdf.set_index('timestamp', inplace=True)

        pdf['price_change_pct'] = pdf['price'].pct_change()
        pdf['price_ma_5'] = pdf['price'].rolling(window=5).mean()
        pdf.dropna(inplace=True)

        if pdf.empty:
             _LOG.warning("DataFrame empty after cleaning: %s", local_json_path)
             return None

        _LOG.info("Parsed/cleaned data from %s. Shape: %s", local_json_path, pdf.shape)
        return pdf

    except Exception as e:
        _LOG.error("Failed parsing local JSON data from %s: %s", local_json_path, e)
        return None

def train_arima_model(price_series: pd.Series,
                      order_candidates: List[Tuple[int, int, int]] = [(1, 1, 1), (2, 1, 2), (0, 1, 1)],
                      default_order: Tuple[int, int, int] = (1, 1, 1)
                      ) -> Optional[Tuple[Any, Tuple[int, int, int]]]:
    """Trains an ARIMA model, selecting the best order via AIC."""
    if price_series.empty:
        _LOG.error("Cannot train ARIMA on empty series.")
        return None
    if not isinstance(price_series.index, pd.DatetimeIndex):
         _LOG.warning("Price series index is not DatetimeIndex.")

    best_model_fit = None
    best_order = None
    best_aic = float('inf')

    _LOG.info("Fitting ARIMA models with orders: %s", order_candidates)
    for order in order_candidates:
        try:
            model = ARIMA(price_series, order=order)
            model_fit = model.fit()
            aic = model_fit.aic
            _LOG.info("Fitted ARIMA%s, AIC: %.2f", order, aic)
            if aic < best_aic:
                best_aic = aic
                best_model_fit = model_fit
                best_order = order
        except Exception as e:
            _LOG.warning("Failed fit ARIMA%s: %s", order, e)

    if best_model_fit:
        _LOG.info("Selected ARIMA order %s with AIC %.2f", best_order, best_aic)
        return best_model_fit, best_order
    else:
        _LOG.error("Failed fit any candidate ARIMA model.")
        try:
             _LOG.warning("Falling back to order: %s", default_order)
             model = ARIMA(price_series, order=default_order)
             model_fit = model.fit()
             _LOG.info("Fitted fallback ARIMA%s, AIC: %.2f", default_order, model_fit.aic)
             return model_fit, default_order
        except Exception as e:
            _LOG.error("Fallback ARIMA%s failed: %s", default_order, e)
            return None

def get_forecast(model_fit, steps: int = 10) -> Optional[pd.DataFrame]:
    """Generates forecasts from a fitted ARIMA model."""
    try:
        forecast_result = model_fit.get_forecast(steps=steps)
        forecast_mean = forecast_result.predicted_mean
        conf_int = forecast_result.conf_int(alpha=0.05)

        last_timestamp = model_fit.data.endog.index[-1]
        freq = pd.infer_freq(model_fit.data.endog.index)
        if freq:
             future_index = pd.date_range(start=last_timestamp + pd.Timedelta(freq), periods=steps, freq=freq)
        else:
             time_diff = model_fit.data.endog.index[-1] - model_fit.data.endog.index[-2]
             future_index = pd.date_range(start=last_timestamp + time_diff, periods=steps, freq=time_diff)

        forecast_df = pd.DataFrame({
            'timestamp': future_index,
            'forecast': forecast_mean.values,
            'lower_ci': conf_int.iloc[:, 0].values,
            'upper_ci': conf_int.iloc[:, 1].values
        })
        forecast_df.set_index('timestamp', inplace=True)
        _LOG.info("Generated forecast for %d steps.", steps)
        return forecast_df

    except Exception as e:
        _LOG.error("Failed forecast generation: %s", e)
        return None

# === Plotting ===

def plot_historical_data(data: pd.DataFrame, price_col: str = 'price', ma_col: str = 'price_ma_5', filename: Optional[str] = None) -> None:
    """Plots historical price data and moving average."""
    if data.empty:
        _LOG.warning("Cannot plot empty historical data.")
        return
    try:
        plt.figure(figsize=(14, 6))
        plt.plot(data.index, data[price_col], label="Price (USD)", color="#F7931A")
        if ma_col in data.columns:
             plt.plot(data.index, data[ma_col], label="5-Point MA", linestyle="--", color="#0D2D6C")

        plt.title("Bitcoin Price Analysis", pad=20)
        plt.xlabel("Timestamp", labelpad=10)
        plt.ylabel("USD", labelpad=10)
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()

        if filename:
            plt.savefig(filename, bbox_inches='tight')
            _LOG.info("Saved historical plot to %s", filename)
        else:
            plt.show()
        plt.clf()
        plt.close()

    except Exception as e:
        _LOG.error("Failed plotting historical data: %s", e)
        plt.clf()
        plt.close()

def plot_forecast_data(history: pd.DataFrame,
                       forecast_df: pd.DataFrame,
                       price_col: str = 'price',
                       forecast_col: str = 'forecast_price', 
                       lower_ci_col: str = 'lower_ci',     
                       upper_ci_col: str = 'upper_ci',     
                       filename: Optional[str] = None) -> None:
    """Plots historical data with forecast and optional confidence intervals."""
    if history.empty or forecast_df.empty:
        _LOG.warning("Cannot plot forecast with empty data.")
        return
    try:
        plt.figure(figsize=(12, 5))

        # Plot historical price
        if price_col in history.columns:
             plt.plot(history.index, history[price_col], label='Historical', color="#0D2D6C")
        else:
             _LOG.error(f"Historical price column '{price_col}' not found.")
             print(f"ERROR: Historical price column '{price_col}' not found.")
             return

        # Plot forecast price
        if forecast_col in forecast_df.columns:
            plt.plot(forecast_df.index, forecast_df[forecast_col], label='Forecast', linestyle="--", color="#F7931A")
        else:
             _LOG.error(f"Forecast column '{forecast_col}' not found in forecast_df.")
             print(f"ERROR: Forecast column '{forecast_col}' not found.")



        if lower_ci_col in forecast_df.columns and upper_ci_col in forecast_df.columns:
            plt.fill_between(
                forecast_df.index,
                forecast_df[lower_ci_col],
                forecast_df[upper_ci_col],
                color='orange', alpha=0.1, label='95% CI'
            )
            _LOG.info("Plotting with confidence intervals.")
        else:
             _LOG.warning(f"Confidence interval columns ('{lower_ci_col}', '{upper_ci_col}') not found, plotting forecast only.")
        # --- End CI Check ---

        plt.title('Bitcoin Price Forecast', pad=15)
        plt.xlabel('Time')
        plt.ylabel('USD')
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()

        if filename:
            
            output_dir = os.path.dirname(filename)
            if output_dir:
                 os.makedirs(output_dir, exist_ok=True)
            plt.savefig(filename, bbox_inches='tight')
            _LOG.info("Saved forecast plot to %s", filename)
        else:
            plt.show()
        plt.clf()
        plt.close()

    except KeyError as e:
         _LOG.error(f"Failed plotting forecast data due to missing column: {e}")
         print(f"ERROR: Plotting failed - missing column: {e}")
         plt.clf()
         plt.close()
    except Exception as e:
        _LOG.error(f"Failed plotting forecast data: {e}")
        print(f"ERROR: An unexpected error occurred during plotting: {e}")
        plt.clf()
        plt.close()
def submit_notebook_run_cli(notebook_path: str, cluster_id: str, run_name_prefix: str = "NotebookRun") -> Optional[str]:
    """
    Submits a notebook as a one-time run on an existing cluster using 'databricks runs submit'.


    Returns:
        The run ID if submission was successful, otherwise None.
    """
    if not notebook_path or not cluster_id:
        _LOG.error("Invalid notebook_path or cluster_id provided for run submission.")
        return None

    run_payload = {
        "existing_cluster_id": cluster_id,
        "notebook_task": {
            "notebook_path": notebook_path,
   
        },
        "run_name": f"{run_name_prefix}_{os.path.basename(notebook_path)}_{int(time.time())}"
    }

    # Convert payload to JSON string for the command
    try:
        json_payload = json.dumps(run_payload)
    except TypeError as e:
         _LOG.error(f"Failed to serialize run payload to JSON: {e}")
         return None

    command = ['databricks', 'runs', 'submit', '--json', json_payload]
    result = _run_databricks_cli(command)

    if result["success"] and isinstance(result.get("output"), dict) and "run_id" in result["output"]:
        run_id = str(result["output"]["run_id"]) 
        _LOG.info("Successfully submitted run for notebook '%s' on cluster '%s'. Run ID: %s", notebook_path, cluster_id, run_id)
        return run_id
    else:
        _LOG.error("Failed to submit run for notebook '%s'. Error: %s", notebook_path, result.get("error", "Unknown error"))
        return None
    

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _LOG.info("Running utils module directly for testing.")

    data_file = fetch_bitcoin_data()
    if data_file:
        df = parse_local_json_data(data_file)
        if df is not None:
            os.makedirs("output_plots", exist_ok=True) 
            plot_historical_data(df, filename="output_plots/historical_test.png")
            model_info = train_arima_model(df['price'])
            if model_info:
                fitted_model, _ = model_info
                forecast = get_forecast(fitted_model, steps=20)
                if forecast is not None:
                     plot_forecast_data(df, forecast, filename="output_plots/forecast_test.png")