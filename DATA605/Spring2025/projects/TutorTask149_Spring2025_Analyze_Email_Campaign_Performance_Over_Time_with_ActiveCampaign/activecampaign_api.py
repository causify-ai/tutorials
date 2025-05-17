import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("ACTIVE_CAMPAIGN_API_URL")
API_KEY = os.getenv("ACTIVE_CAMPAIGN_API_KEY")

HEADERS = {
    "Api-Token": API_KEY,
    "Content-Type": "application/json"
}

def get_campaigns() -> pd.DataFrame:
    url = f"{API_URL}/api/3/campaigns"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return pd.DataFrame(response.json().get("campaigns", []))
    else:
        raise Exception(f"API error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    df = get_campaigns()
    print(df.head())

