import time
import logging
import requests
import csv
import bonobo
import pandas as pd
import matplotlib.pyplot as plt

# Set up a simple logging configuration
logging.basicConfig(level=logging.INFO)

# Function to fetch Bitcoin data
def fetch_bitcoin_data():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data: {e}")
        return None


# Function to transform data (parse and clean)
def transform_bitcoin_data(data):
    if data and "bitcoin" in data:
        return {
            "timestamp": time.time(),
            "bitcoin_usd": data["bitcoin"]["usd"]  # Extract USD price
        }
    return None

# Function to save data to CSV
def save_to_csv(data):
    with open("bitcoin_data.csv", "a", newline='') as file:
        fieldnames = ["timestamp", "bitcoin_usd"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if file.tell() == 0:  # Check if file is empty to write headers
            writer.writeheader()

        writer.writerow(data)

# Function for basic time series analysis (moving average)
def time_series_analysis():
    try:
        df = pd.read_csv("bitcoin_data.csv")
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        df.set_index('timestamp', inplace=True)

        # Moving average of Bitcoin price
        df['moving_average'] = df['bitcoin_usd'].rolling(window=10).mean()
        price_series = df['bitcoin_usd'].to_numpy()[:, None]

        # Plot the data
        plt.figure(figsize=(10, 6))
        plt.plot(df.index, df['bitcoin_usd'], label='Bitcoin Price (USD)', color='blue')
        plt.plot(df.index, df['moving_average'], label='10-period Moving Average', color='red', linestyle='--')
        plt.xlabel('Time')
        plt.ylabel('Price (USD)')
        plt.title('Bitcoin Price and Moving Average')
        plt.legend()
        plt.tight_layout()
        plt.savefig("btc_plot.png")
        plt.close()
        logging.info("Time series analysis complete. Plot saved as btc_plot.png.")

    except Exception as e:
        logging.error(f"Error during time series analysis: {e}")

# Bonobo pipeline to fetch, transform, and save data
def create_pipeline():
    # Define the pipeline steps
    graph = bonobo.Graph(
        fetch_bitcoin_data,
        transform_bitcoin_data,
        save_to_csv
    )

    return graph

# Main function to run the pipeline and perform analysis
def main():
    max_iterations = 5000  # Maximum iterations

    for i in range(max_iterations):
        logging.info(f"Iteration {i+1}/{max_iterations}")

        # Create and run the Bonobo pipeline
        graph = create_pipeline()
        bonobo.run(graph)

        logging.info(f"Fetched and saved one record. Iteration {i+1}/{max_iterations}.")

        # Sleep for 1 second to avoid rate limiting
        time.sleep(5)

    logging.info("Completed all iterations.")
    
    # Perform time series analysis after collecting data
    logging.info("Performing time series analysis...")
    time_series_analysis()

if __name__ == "__main__":
    main()
