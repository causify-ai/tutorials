### Data Fetching
# from template_utils import fetch_price

# # Fetch and display the current Bitcoin price
# price = fetch_price()
# if price:
#     print(f"Current Bitcoin Price (USD): ${price}")
# else:
#     print("Failed to fetch Bitcoin price.")

### Data Fetching and Saving
from gensim_utils import data_ingest

# Ingest price data for 3 minutes
data_ingest(minutes=3)

# Run indefinitely
# data_ingest()