# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# CONTENTS:
#

# %%
import logging
import os
import time

import numpy as np
import pandas as pd
import requests

import helpers.hdbg as hdbg
import helpers.henv as henv
import helpers.hprint as hprint

# %%
# Configure logger.
hdbg.init_logger(verbosity=logging.INFO)
_LOG = logging.getLogger(__name__)

# Print system signature.
_LOG.info("%s", henv.get_system_signature()[0])

# Configure the notebook style.
hprint.config_notebook()

# %%
username = os.getenv("username")
password = os.getenv("password")
x_authorization = os.getenv("x-authorization")


# %% [markdown]
# The way to get authorizations and headers is to inspect the required ulrs and find GET-APIs which fetch us the data .

# %%
login_payload = {
    "username": username,
    "password": password,
}
login_url = "https://auth.money2020.com/u/login?state=hKFo2SBvWGgxWVlIRUpxeHdPeVBlVHJ2cEF4NmJ5ZVJ2WTBpb6Fur3VuaXZlcnNhbC1sb2dpbqN0aWTZIDNBbXBwOFZqSmFSZ2ZVVkxRemtmSE9GRVY5MDdHNldYo2NpZNkgWGlQeGhkQzRlMzRSYXlHelhjV3ZBNFVyYWcxTEV2WXU"
api_headers = {
    "x-authorization": x_authorization,
    "Content-Type": "application/json",
    "Accept": "application/json",
}


# %%
data_collection = []
max_retries = 3

with requests.Session() as session:
    session.post(login_url, data=login_payload)
    base_url = (
        "https://api-prod.grip.events/1/container/7381/search/extension/82807"
    )
    for page in range(1, 1001):
        url = f"{base_url}?order=asc&page={page}&sort=name"
        # Track retry attempts for the current page
        retries = 0
        # Initial backoff time (in seconds) if rate-limited
        backoff_time = 1
        # Retry logic: continue trying if the request fails, up to max_retries
        while retries < max_retries:
            response = session.get(url, headers=api_headers)
            print(f"Requesting page {page}: {response.status_code}")
            # Check for a rate limit error (HTTP 429)
            if response.status_code == 429:
                print("Rate limit exceeded. Waiting before retrying...")
                time.sleep(backoff_time)
                # The min() function caps the wait time to a maximum of 60 seconds
                # Double the wait time for rate limiting, capping it at 60 seconds to avoid excessive delays.
                backoff_time = min(backoff_time * 2, 60)
                # Increment retry counter and retry the request
                retries += 1
                continue
            try:
                result = response.json()
                # Stop if the request is unsuccessful (e.g., invalid response)
                if not result.get("success"):
                    print(f"Stopping at page {page} as request was unsuccessful.")
                    break

                data = result.get("data", [])
                if data:
                    data_collection.extend(data)
                    # Reset backoff time for next page
                    backoff_time = 1
                    break
                else:
                    # Retry if no data was returned for this page
                    print(f"No data found on page {page}, retrying...")
                    retries += 1
                    time.sleep(1)
            except requests.JSONDecodeError:
                print(f"Stopping at page {page} due to invalid JSON response.")
                print("Response content:", response.text)
                break
        # Wait 4 seconds before moving to the next page to avoid rate limits
        time.sleep(4)


# %%
processed_data = []
for i in data_collection:
    location = i.get("location", "")
    processed_data.append(
        {
            "id": i.get("id", ""),
            "firstName": (
                i.get("first_name", "").strip() if i.get("first_name") else ""
            ),
            "lastName": (
                i.get("last_name", "").strip() if i.get("last_name") else ""
            ),
            "location": (
                None
                if not isinstance(location, str) or "error" in location
                else location.strip()
            ),
            "companyName": (
                i.get("company_name", "").strip() if i.get("company_name") else ""
            ),
            "jobTitle": (
                i.get("job_title", "").strip() if i.get("job_title") else ""
            ),
        }
    )

df = pd.DataFrame(processed_data)


# %%
df.tail(6)

# %%
df.to_csv("money20-20_Attandees.csv_Requests", index=False)

# %%
df_new = pd.read_csv("money2020_data.csv")

# %%
df_new.head()

# %%
contact_sharings = []
is_connections = []
emails = []
phone_numbers = []

with requests.Session() as session:
    session.post(login_url, data=login_payload)
    for i in df_new["id"]:
        print(i)
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.5",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "x-authorization": "7d5af131-d25f-42e9-8289-d7f35f9deb34",
        }
        contact_url = f"https://api-prod.grip.events/1/container/7381/thing/{i}/contact_details"
        response = requests.get(contact_url, headers=headers)
        if response.status_code == 200:
            contact_response = response.json()
            # Extract fields, using None as default if missing
            contact_sharings.append(
                contact_response["data"].get("contact_sharing", None)
            )
            is_connections.append(
                contact_response["data"].get("is_connection", None)
            )
            emails.append(contact_response["data"].get("email", None))
            phone_numbers.append(
                contact_response["data"].get("phone_number", None)
            )
        elif response.status_code == 204:
            print("No content available for this request.")
            contact_sharings.append(None)
            is_connections.append(None)
            emails.append(None)
            phone_numbers.append(None)
        else:
            print(f"Failed to retrieve data. Status code: {response.status_code}")
            contact_sharings.append(None)
            is_connections.append(None)
            emails.append(None)
            phone_numbers.append(None)

df_new["contact_sharing"] = contact_sharings
df_new["is_connection"] = is_connections
df_new["email"] = emails
df_new["phone_number"] = phone_numbers


# %%
df_new.head(20)

# %%
df_new.to_csv("money20-20_Attandees_Contacts.csv", index=False)

# %%
conditions = [
    df_new["email"].notna(),
    (df_new["email"].isna()) & (df_new["contact_sharing"] == "connection"),
    (df_new["email"].isna()) & (df_new["contact_sharing"] != "connection"),
]
choices = [
    "email available as connected",
    "email available if connected",
    "email not available as private",
]
df_new["email_availability"] = np.select(conditions, choices)
email_availability_counts = (
    df_new["email_availability"].value_counts(normalize=True) * 100
)
for category, percentage in email_availability_counts.items():
    print(f"For {percentage:.1f}%, {category}.")
