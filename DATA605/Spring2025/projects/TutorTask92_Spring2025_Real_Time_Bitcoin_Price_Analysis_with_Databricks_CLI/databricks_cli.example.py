"""
End-to-end pipeline: fetch Bitcoin data, forecast, and plot results.

Usage:
    python databricks_cli.example.py

Functions:
    fetch_data(): pull and append latest price
    parse_data(path): load JSON lines into a DataFrame
    train_model(series): fit ARIMA and return (model, order)
    make_forecast(model, steps): produce future-point forecast
    save_plots(history, forecast): write PNGs to output_plots/

See also: databricks_cli.example.md
"""

from databricks_cli_utils import (
    fetch_bitcoin_data,
    parse_local_json_data,
    train_arima_model,
    get_forecast,
    plot_historical_data,
    plot_forecast_data,
)

def fetch_data() -> str:
    """Fetch and append Bitcoin price; return the JSON file path."""
    return fetch_bitcoin_data(output_dir="data")

def parse_data(path: str):
    """Parse JSON lines into a pandas DataFrame."""
    return parse_local_json_data(path)

def train_model(df):
    """Fit ARIMA and pick best order; return (fitted_model, order)."""
    return train_arima_model(df["price"])

def make_forecast(model_fit, steps: int = 10):
    """Generate a forecast DataFrame for the given fitted model."""
    return get_forecast(model_fit, steps=steps)

def save_plots(history, forecast):
    """Save historical and forecast plots to disk."""
    plot_historical_data(history, filename="output_plots/historical.png")
    plot_forecast_data(history, forecast, filename="output_plots/forecast.png")

def main():
    data_path = fetch_data()
    print("Data at:", data_path)

    df = parse_data(data_path)
    print("DataFrame shape:", df.shape)

    model_fit, order = train_model(df)
    print("ARIMA order:", order)

    forecast_df = make_forecast(model_fit)
    print("Forecast tail:\n", forecast_df.tail())

    save_plots(df, forecast_df)
    print("Plots saved in output_plots/")

if __name__ == "__main__":
    main()
