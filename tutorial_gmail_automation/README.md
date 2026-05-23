# Gmail Automation 

This project is a Python-based utility to connect to Gmail, authenticate using OAuth 2.0, and retrieve emails based on a custom search query. The results are processed and displayed in a Pandas DataFrame. The utility also extracts unique email addresses from senders and email content.

## Features

- OAuth 2.0 authentication using `credentials.json`
- Retrieve emails using Gmail API with custom search queries
- Display email metadata (sender, subject, date, snippet) in a DataFrame
- Extract and list unique email addresses from sender fields and message bodies
- Designed to work inside a Jupyter Notebook environment

---

## Google Cloud Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (or select an existing one).
3. Enable the **Gmail API** for the project.
4. Navigate to **APIs & Services > Credentials**, click **Create Credentials > OAuth 2.0 Client ID**.
5. Choose **Desktop App** as the application type.
6. Download the `credentials.json` file and place it in the root directory of your project (same folder as the notebook).


## Usage

1. Clone this repository or download the notebook.
2. Make sure `credentials.json` is in the project directory.
3. Open tutorial_gmail_automation.ipynb in Jupyter Notebook and run all cells:
    -The first time, you will be prompted to authorize access via a browser.
    -Once authenticated, a token.json will be saved for future sessions.
4. Modify the search_query variable inside the notebook to filter emails (e.g., 'subject:invoice', 'after:2024/01/01').
