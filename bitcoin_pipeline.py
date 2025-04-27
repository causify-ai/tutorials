import time
import logging
import requests
import csv

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

# Function to save data to CSV
def save_to_csv(data):
    with open("bitcoin_data.csv", "a", newline='') as file:
        fieldnames = ["timestamp", "bitcoin_usd"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        if file.tell() == 0:  # Check if file is empty to write headers
            writer.writeheader()
        
        # Ensure the data is in the expected format
        row = {
            "timestamp": time.time(),
            "bitcoin_usd": data["bitcoin"]["usd"] if "bitcoin" in data else None  # Extract USD price
        }
        
        writer.writerow(row)

# Main function to fetch and save data
def main():
    for i in range(50):
        logging.info(f"Iteration {i+1}/50")
        
        # Fetch Bitcoin data
        data = fetch_bitcoin_data()
        
        if data:
            # Save data to CSV
            save_to_csv(data)
            logging.info(f"Fetched and saved one record. Iteration {i+1}/50.")
        else:
            logging.warning("No data fetched.")
        
        # Sleep for 1 second to avoid rate limiting
        time.sleep(1)

if __name__ == "__main__":
    main()
