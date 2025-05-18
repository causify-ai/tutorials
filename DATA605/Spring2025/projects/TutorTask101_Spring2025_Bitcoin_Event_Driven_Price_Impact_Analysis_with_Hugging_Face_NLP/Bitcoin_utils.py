
import pandas as pd
import numpy as np
from datetime import datetime
from transformers import pipeline

# Set seed for reproducibility
np.random.seed(42)

# Load models
ner_pipeline = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")
classifier_pipeline = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Candidate labels for classification
CANDIDATE_LABELS = [
    "Regulatory", "Technological", "Market Manipulation", "Adoption News",
    "ETF News", "Security Breach", "Legal Action", "Macro News"
]

def extract_entities(text):
    try:
        ner_results = ner_pipeline(text[:512])
        return [(ent['entity_group'], ent['word']) for ent in ner_results]
    except Exception:
        return []

def classify_event(text, labels=CANDIDATE_LABELS):
    try:
        result = classifier_pipeline(text[:512], labels)
        return result['labels'][0]  # Top label
    except Exception:
        return "Uncategorized"

def generate_fallback_articles(num_articles=50, date_range=None):
    """
    Generates fallback Bitcoin news articles with timestamps aligned to OHLC data.
    """
    if date_range is None:
        date_range = pd.date_range("2024-01-01", pd.to_datetime("today"), periods=num_articles)

    titles = [
        "SEC Charges Exchange with Unregistered Securities Offerings",
        "Bitcoin Network Undergoes Major Upgrade",
        "Anonymous Whale Moves 10,000 BTC",
        "Visa Enables Bitcoin Payments at 70M Merchants",
        "Blackrock ETF Filing Delayed by SEC",
        "Crypto Exchange Hacked, Millions Lost",
        "Lawsuit Filed Against Major Exchange",
        "Fed Hints at New Crypto Regulation"
    ]
    contents = [
        "The Securities and Exchange Commission filed charges against...",
        "Today, the Bitcoin Core developers released a major upgrade...",
        "An anonymous wallet transferred 10,000 BTC to an unknown address...",
        "Visa announced support for BTC payments at retail merchants...",
        "Blackrock's proposed ETF was delayed again, citing SEC concerns...",
        "Millions in BTC and ETH were stolen after a major hack...",
        "A class-action lawsuit was initiated against one of the top exchanges...",
        "Federal Reserve Chairman hinted at upcoming stablecoin regulation..."
    ]

    df = pd.DataFrame({
        "title": np.random.choice(titles, num_articles),
        "content": np.random.choice(contents, num_articles),
        "published": date_range
    })

    return df


import requests

def fetch_ohlc_data(days=365, vs_currency="usd"):
    """
    Fetches historical daily OHLC data for Bitcoin from CoinGecko.
    """
    url = f"https://api.coingecko.com/api/v3/coins/bitcoin/ohlc"
    params = {
        "vs_currency": vs_currency,
        "days": days  # Options: 1, 7, 30, 90, 180, 365, max
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Error fetching data: {response.status_code} {response.text}")

    data = response.json()
    df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close"])
    df["date"] = pd.to_datetime(df["timestamp"], unit="ms")
    df = df.set_index("date").drop(columns=["timestamp"])
    return df

from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import NearestNeighbors

def estimate_ate_all_events(df_analysis, event_matrix, confounder_col='confounder_price', outcome_col='volatility_3d'):
    '''
    For each event type in event_matrix, compute the Average Treatment Effect (ATE)
    using 1-to-1 propensity score matching.
    '''
    results = []

    for event in event_matrix.columns:
        df_analysis = df_analysis.copy()
        df_analysis['treatment'] = df_analysis[event]
        treatment = df_analysis['treatment']
        outcome = df_analysis[outcome_col]

        treated_mask = treatment == 1
        control_mask = treatment == 0

        if treated_mask.sum() == 0 or control_mask.sum() == 0:
            continue

        model = LogisticRegression()
        model.fit(df_analysis[[confounder_col]], treatment)
        scores = model.predict_proba(df_analysis[[confounder_col]])[:, 1]

        nn = NearestNeighbors(n_neighbors=1)
        nn.fit(scores[control_mask].reshape(-1, 1))
        _, indices = nn.kneighbors(scores[treated_mask].reshape(-1, 1))

        matched_controls = indices.flatten()
        treated_outcomes = outcome[treated_mask].values
        control_outcomes = outcome[control_mask].iloc[matched_controls].values

        ate = treated_outcomes.mean() - control_outcomes.mean()
        results.append((event, round(ate, 2)))

    return results


