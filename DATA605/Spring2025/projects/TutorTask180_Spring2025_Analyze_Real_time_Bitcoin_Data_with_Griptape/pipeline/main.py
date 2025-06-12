# main.py
import yaml
from utils import BitcoinTool
from analysis import BitcoinAnalysisTool  # <- contains reporting functions

def main():
    # Load config
    with open("pipeline/config.yaml", "r") as f:
        config = yaml.safe_load(f)

    # Update data pipeline
    tool = BitcoinTool(config=config)
    print(tool.run({}))  # This performs data update

    # Load the updated data
    analysis = BitcoinAnalysisTool()
    df = analysis.load_and_clean_data("warehouse/bitcoin_prices.csv")  # replace with actual path key

    # Run forecast
    df_prophet, forecast = analysis.run_prophet_forecast(df)

    # Generate reports
    data_report = analysis.generate_data_summary_report(df)
    forecast_report = analysis.generate_forecast_report(forecast)

    # Output reports
    print(data_report)
    print(forecast_report)

if __name__ == "__main__":
    main()
