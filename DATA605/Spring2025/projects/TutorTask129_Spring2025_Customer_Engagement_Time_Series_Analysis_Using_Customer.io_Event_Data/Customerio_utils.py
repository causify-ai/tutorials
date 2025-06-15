"""
Customer.io Data Simulation and Forecasting Script

This script generates mock users, simulates time-stamped event logs, and performs ARIMA forecasting
on daily user interaction counts.

References:
- Customer.io Python SDK: https://customer.io/docs/api
- Faker Library: https://faker.readthedocs.io
- ARIMA Model: https://www.statsmodels.org/
"""

import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from customerio import CustomerIO
from faker import Faker
import time
import random
from datetime import datetime, timedelta

# === Customer.io Setup ===
SITE_ID = "1d7fdb608de0a0a8cd66"
API_KEY = "4c9b87c8eae4e9729835"
cio = CustomerIO(site_id=SITE_ID, api_key=API_KEY)
faker = Faker()

def generate_users(num_users=1000, output_file="simulated_user_ids.csv"):
    """
    Generate simulated users and push them to Customer.io.

    :param num_users: Number of users to create
    :param output_file: Filename to save user IDs
    :return: List of user IDs
    """
    user_ids = []
    for _ in range(num_users):
        user_id = f"user_{faker.uuid4()[:8]}"
        email = faker.email()
        name = faker.name()

        cio.identify(id=user_id, email=email, name=name)
        user_ids.append(user_id)
        time.sleep(0.05)

    pd.DataFrame({"user_id": user_ids}).to_csv(output_file, index=False)
    print(f"Created and saved {num_users} users to '{output_file}'")
    return user_ids

def simulate_events(user_ids, output_file="simulated_event_log.csv", days_back=180):
    """
    Simulate behavioral events (e.g., clicks, logins) for each user.

    :param user_ids: List of Customer.io user IDs
    :param output_file: CSV to store simulated events
    :param days_back: Days in the past to simulate data
    :return: List of simulated event records
    """
    event_types = ["email_opened", "clicked", "app_login"]
    campaigns = ["Spring Sale", "Black Friday", "Summer Promo"]
    all_events = []

    for user_id in user_ids:
        for _ in range(random.randint(30, 60)):
            event_type = random.choice(event_types)
            campaign = random.choice(campaigns)
            days_ago = random.randint(0, days_back)
            timestamp = int((datetime.now() - timedelta(days=days_ago)).timestamp())
            device = random.choice(["iPhone", "Android", "Web"])

            cio.track(
                customer_id=user_id,
                name=event_type,
                data={"campaign": campaign, "device": device},
                timestamp=timestamp
            )

            all_events.append({
                "user_id": user_id,
                "event_name": event_type,
                "timestamp": pd.to_datetime(timestamp, unit="s"),
                "campaign": campaign,
                "device": device
            })
        time.sleep(0.2)

    pd.DataFrame(all_events).to_csv(output_file, index=False)
    print(f"Simulated events saved to '{output_file}'")
    return all_events

def retrieve_event_summary(filename="simulated_event_log.csv"):
    """
    Aggregate events into daily counts per event type.

    :param filename: CSV file with simulated event logs
    :return: DataFrame with rows as dates and columns as event types
    """
    df = pd.read_csv(filename)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["date"] = df["timestamp"].dt.date

    daily_counts = df.groupby(["date", "event_name"]).size().unstack(fill_value=0)
    return daily_counts



def forecast_arima(summary_df, event_types=["email_opened", "app_login", "clicked"], order=(1, 1, 1), steps=14):
    """
    Generate ARIMA forecasts for specified event types.

    Parameters:
        summary_df (pd.DataFrame): Time-indexed DataFrame with event columns.
        event_types (list): List of columns to forecast.
        order (tuple): ARIMA order (p,d,q).
        steps (int): Number of future steps to forecast.

    Returns:
        dict: {event_name: {"y_true": actual values, "y_pred": forecast values, "dates": test index}}
    """
    results = {}

    for event in event_types:
        # Prepare series
        series = summary_df[event]
        series.index = pd.to_datetime(series.index)
        series = series.asfreq("D").fillna(0)

        # Train-test split
        train = series[:-steps]
        test = series[-steps:]

        # Fit ARIMA model
        model = ARIMA(train, order=order)
        model_fit = model.fit(start_params=[0.1]*model.k_params, method_kwargs={'warn_convergence': False})

        # Forecast
        forecast = model_fit.forecast(steps=steps)
        forecast.index = test.index

        # Store results
        results[event] = {
            "y_true": test.values,
            "y_pred": forecast.values,
            "dates": test.index
        }

    return results