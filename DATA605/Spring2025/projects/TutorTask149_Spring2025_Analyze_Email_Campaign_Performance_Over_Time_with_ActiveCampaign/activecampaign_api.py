"""
ActiveCampaign.API.py

This script defines the API wrapper to interact with ActiveCampaign. It securely fetches campaign data as a DataFrame.
"""

import os
import requests
import pandas as pd
from dotenv import load_dotenv

# Load .env credentials
load_dotenv()

API_URL = os.getenv("ACTIVE_CAMPAIGN_API_URL")
API_KEY = os.getenv("ACTIVE_CAMPAIGN_API_KEY")

HEADERS = {
    "Api-Token": API_KEY,
    "Content-Type": "application/json"
}

def get_campaigns() -> pd.DataFrame:
    """
    Fetch all email campaign metadata from ActiveCampaign.
    Returns:
        pandas.DataFrame: Campaigns with metadata
    """
    url = f"{API_URL}/api/3/campaigns"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        campaigns = response.json().get("campaigns", [])
        return pd.DataFrame(campaigns)
    else:
        raise Exception(f"API error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    # Quick test when run as a script
    df = get_campaigns()
    print(df.head())
