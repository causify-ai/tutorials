# main.py

import os
import platform
from rasa_utils import BitcoinAPI
import matplotlib.pyplot as plt

def clear_terminal():
    # Clears the macOS/Linux terminal (or Windows cmd)
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def main():
    clear_terminal()

    # 1. Instantiate the API client
    api = BitcoinAPI(vs_currency="usd")

    # 2. Fetch current price
    current_price = api.get_current_price()
    print(f"Current Bitcoin price (USD): ${current_price:,.2f}\n")

    # 3. Fetch 30 days of history
    df = api.get_historical_data(days=30, interval="daily")

    # 4. Summary statistics
    stats = api.summarize_trends(df)
    print("30-day summary statistics:")
    for name, val in stats.items():
        print(f"  {name.title():>5}: ${val:,.2f}")
    print()

    # 5. Plotting
    ax = df.set_index("timestamp")["price"].plot(
        title="Bitcoin Price (Last 30 Days)"
    )
    ax.set_xlabel("Date")
    ax.set_ylabel("Price (USD)")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()