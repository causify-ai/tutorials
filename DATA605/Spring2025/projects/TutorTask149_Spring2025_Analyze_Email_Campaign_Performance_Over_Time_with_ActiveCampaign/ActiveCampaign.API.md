
# ActiveCampaign API Tutorial

## Table of Contents

- [Introduction](#introduction)
- [Setup](#setup)
- [Authentication](#authentication)
- [API Functions](#api-functions)
- [Response Structure](#response-structure)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)

---

## Introduction

This tutorial introduces the **ActiveCampaign** API and how to interact with it using Python.  
We use the `/api/3/campaigns` endpoint to retrieve campaign metadata, including campaign names, timestamps, and engagement statistics.

The native REST API is accessed using the `requests` library, and environment variables are used to securely store credentials.

---

## Setup

Install the required packages using pip:

```bash
pip install python-dotenv requests pandas
```

Ensure you have a `.env` file that contains:

```env
ACTIVE_CAMPAIGN_API_URL=https://<your-api-domain>
ACTIVE_CAMPAIGN_API_KEY=your_api_key_here
```

Load the environment variables in Python using:

```python
from dotenv import load_dotenv
load_dotenv()
```

---

## Authentication

ActiveCampaign uses token-based authentication via HTTP headers.

```python
import os

API_KEY = os.getenv("ACTIVE_CAMPAIGN_API_KEY")
HEADERS = {
    "Api-Token": API_KEY,
    "Content-Type": "application/json"
}
```

---

## API Functions

Fetching campaign data:

```python
import requests

url = f"{API_URL}/api/3/campaigns"
response = requests.get(url, headers=HEADERS)
```

Recommended wrapper function:

```python
import pandas as pd

def get_campaigns():
    response = requests.get(f"{API_URL}/api/3/campaigns", headers=HEADERS)
    if response.status_code == 200:
        return pd.DataFrame(response.json().get("campaigns", []))
    else:
        raise Exception(f"API error: {response.status_code} - {response.text}")
```

---

## Response Structure

The JSON response looks like:

```json
{
  "campaigns": [
    {
      "id": "1",
      "name": "Weekly Update",
      "cdate": "2024-01-05T13:25:00-05:00"
    },
    ...
  ]
}
```

You typically convert this into a DataFrame for analysis.

---

## Error Handling

Example:

```python
if response.status_code != 200:
    raise Exception(f"API error: {response.status_code} - {response.text}")
```

Common errors:
- `401 Unauthorized`: Invalid/missing token
- `403 Forbidden`: Access denied
- `429 Too Many Requests`: Rate limited
- `500 Internal Server Error`: Try again later

---

## Best Practices

- Use `.env` files for API tokens
- Use wrapper functions for clarity and reuse
- Log all API requests and errors
- Minimize unnecessary API calls during development (use caching)
