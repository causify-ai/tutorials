# %%
#!sudo /bin/bash -c "(source /venv/bin/activate; pip install --upgrade google-api-python-client)"

# %%
import importlib
import json
import os
import time

import openai
import pandas as pd

import helpers.hgoogle_file_api as hgofiapi
import helpers.hopenai as hopenai

importlib.reload(hgofiapi)


# %%
openai.api_key = os.getenv("OPENAI_API_KEY")

# %%
creds = hgofiapi.get_credentials()
url = "https://docs.google.com/spreadsheets/d/1o07XnIArFdIjz0jTZuyPkldxBczhQhMywdF9Xe9kNmo/edit?gid=474229599#gid=474229599"
company_df = hgofiapi.read_google_file(url, credentials=creds)

# %%
company_df.head()


# %%
def company_profiles_extract(company_name):
    time.sleep(5)
    print(f"Searching for {company_name}.... ")
    user_prompt = f"""
    For the company {company_name}

    Context:
    Identify key decision-makers at a specified company. For companies with fewer than 10,000 employees, provide the full executive team (CEO, CFO, COO, Chief Strategy Officer, etc.) along with any dedicated corporate development leaders. Use publicly available sources such as the company’s leadership page, press releases, reputable business directories (e.g., Crunchbase, PitchBook, Bloomberg), and LinkedIn profiles to gather names, job titles, company size, and source links.

    Action:

    Search Scope:

    Identify key executives and corporate development leaders (e.g., VP/Director/Head of Corporate Development, M&A, or Strategy & Business Development leads) using multiple sources.
    If the company has fewer than 10,000 employees, also retrieve the full executive team, including but not limited to CEO, CFO, COO, CSO, and any additional C-level roles.
    Explicitly search LinkedIn to supplement and cross-check information from the company’s leadership page and other public directories.
    Data Sources:

    Primary: LinkedIn profiles (for current and comprehensive leadership details).
    Secondary: Company leadership pages, press releases, and respected business directories.
    Data Compilation:

    Compile a structured list that includes:
    Name
    Job Title
    Company
    Company Size (confirm whether it’s <10,000 employees)
    Source Link (LinkedIn profile, company website, or another reliable source)

    Please return the data in a JSON-like format (list of dictionaries), like this:

    [
        {{
            "Name": "Jacob R. Dyer",
            "Job Title": "VP of Corporate Development",
            "Company": "Shield AI",
            "Company Size": "<10,000 employees",
            "Source Link": "https://www.linkedin.com/in/jacobdyer"
        }},
        ...
    ]

    Additional Notes:

    When only one result appears from the company’s website, make sure to cross-check with LinkedIn to identify any additional executives or corporate development leaders.
    Given that executive teams and roles can change quickly, confirm the information with multiple sources.
    This prompt is designed for business professionals, investors, M&A teams, recruiters, and competitive intelligence analysts who need comprehensive and up-to-date leadership details.
    Forward‐Thinking Enhancements:
    Multi-Source Validation:
    Including LinkedIn as a mandatory source ensures you capture a wider set of leadership profiles, which is especially useful if the company’s official website lists only a limited number of executives.

    Role Expansion:
    By explicitly instructing a search for additional leadership roles (e.g., Director of M&A or Head of Corporate Strategy) on LinkedIn, the prompt minimizes the risk of missing out on key decision-makers in smaller or mid-sized companies.

    Dynamic Updates:
    Emphasize cross-referencing multiple sources (company pages, LinkedIn, business directories) to accommodate the rapid changes often seen in leadership teams.

    Only return the table and nothing else. Also, return a dataframe of the table and not a string.
    """
    # Define the system instructions for the assistant.
    system_instructions = """
    You are an expert business researcher and data analyst specializing in corporate intelligence and market research.
    Your approach is methodical and strategic, ensuring data accuracy by filtering out outdated information and cross-verifying with multiple authoritative sources.
    """
    extract = hopenai.get_completion(
        user=user_prompt,
        system=system_instructions,
        model="gpt-4o-mini",
        temperature=0.7,
    )
    cleaned_extract = extract.strip("```json\n").strip("```")
    # Check if the response is empty or contains only whitespace.
    if not cleaned_extract.strip():
        print("Error: Empty or invalid response received.")
        return pd.DataFrame()

    # Convert the cleaned string (JSON-like format) into a Python object (list of dictionaries).
    try:
        data = json.loads(cleaned_extract)
    except json.JSONDecodeError as e:
        print(f"Error parsing response: {e}")
        print(f"Response content: {cleaned_extract}")
        return pd.DataFrame()
    df = pd.DataFrame(data)
    return df


# %%
df_list = []
i = 0
for company_name in company_df["companyName"].iloc[:50]:
    print(company_name)
    i = i + 1
    new_data = company_profiles_extract(company_name)
    df_list.append(new_data)
print("companies done")


# %%
row_list = []
for df in df_list:
    row_list.extend(df.to_dict("records"))

# %%
final_df = pd.DataFrame(row_list)


# %%
company_df = hgofiapi.write_to_google_sheet(final_df, url, credentials=creds)

# %%
extracted_profiles_df = hgofiapi.read_google_file(
    url, "chatgpt_extract", credentials=creds
)

# %%
extracted_profiles_df.shape
