# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.15.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
# #!sudo /bin/bash -c "(source /venv/bin/activate; pip install --upgrade google-api-python-client)"

# %%
import logging
import os

import numpy as np

import ck_marketing.hunterio.hunterapi as cmahuhun
import ck_marketing.linkedin.profile_filtering as cmliprfi
import helpers.hgoogle_file_api as hgfiapi
from ck_marketing.hunterio.hunterapi import GoogleSheetsHelper, HunterIO
from ck_marketing.linkedin.phantombuster_api import Phantom

# %% [markdown]
# ## Extracting Profiles

# %%
# Get the API keys from the environment variables.
phantom_api_key = os.getenv("Phantom_API_KEY")
hunter_api_key = os.getenv("Hunter_API_KEY")

# %%
# Initialize the Phantom instance.
phantom = Phantom(phantom_api_key)

# %%
# Get and print all agents and their IDs.
agents = phantom.get_all_agents()
print("List of all agents and their IDs:\n")
for agent in agents:
    print(f"Agent Name: {agent['name']}, Agent ID: {agent['id']}")

# %%
# Get agent ID and name.
AGENT_ID = "1809505480671122"

# %%
specific_agent_name = phantom.get_agent_name(AGENT_ID)
print(f"Selected Phantom: {specific_agent_name}")

# %%
# Google Drive Setup.
google_creds_path = "service.json"
google_sheet_helper = GoogleSheetsHelper(google_creds_path)
drive_folder_id = "1fpsUZ8Nd52FGKxOuqVf11hzEetwvVoDq"
sheet_name = f"{specific_agent_name}_search_export"
tab_name = "search_export"

# %%
# Launch the agent and get the results in a DataFrame
phantom.launch_agent(AGENT_ID)
result_response_json = phantom.fetch_agent_results(AGENT_ID)
csv_url = phantom.get_csv_url(result_response_json.get("output", ""))
df = phantom.download_csv(csv_url)
df = df.replace([np.nan, np.inf, -np.inf], "", inplace=False)
print("DataFrame is fetched")
# print(df.head(2))

# %%
# Create the Google Sheet and get the file ID.
file_id = hgfiapi.create_empty_google_file("sheet", sheet_name, drive_folder_id)

if file_id:
    # Initialize Google Sheets Helper.
    google_sheets_helper = GoogleSheetsHelper(google_creds_path)

    # Open the Google Sheet by file ID.
    sheet = google_sheets_helper.google_account.open_by_key(file_id)

    # Access the default tab (the first worksheet).
    default_worksheet = sheet.get_worksheet(0)

    # Rename the default tab to the desired name.
    new_tab_name = "search_export"
    default_worksheet.update_title(new_tab_name)

    # Write the DataFrame to the renamed default tab.
    google_sheets_helper.write_results(file_id, df, new_tab_name)

    print(
        f"DataFrame written to Google Sheet '{new_tab_name}' in file ID '{file_id}' successfully."
    )
else:
    print("Failed to create the Google Sheet.")

# %% [markdown]
# ## Clean Profiles

# %%
# df = google_sheet_helper.read_sheet('1Etx_Ee9WihmgKAbn4PDN2JvAGWKFLydBAIdjYkuQRwY')
# file_id = '1Etx_Ee9WihmgKAbn4PDN2JvAGWKFLydBAIdjYkuQRwY'
sheet = google_sheet_helper.google_account.open_by_key(file_id)


# %%
words = [
    "sales",
    "research",
    "delivery",
    "income",
    "television",
    "talent",
    "climate",
    "voice",
    "media",
]


# %%
filtered_df = cmliprfi.filter_df(df, "title", words, "remove")

# %%
if file_id:
    # Create a new tab called 'cleaned_profiles'.
    cleaned_profiles_tab = sheet.add_worksheet(
        title="cleaned_profiles", rows="100", cols="20"
    )

    # Write the filtered DataFrame to the new tab.
    google_sheet_helper.write_results(file_id, filtered_df, "cleaned_profiles")

    print(
        f"Filtered DataFrame written to new tab 'cleaned_profiles' in Google Sheet with file ID '{file_id}' successfully."
    )
else:
    print("Failed to create the Google Sheet.")

# %% [markdown]
# ## Extracting emails using hunterio

# %%
# Set up logging to see print statements and warnings.
logging.basicConfig(level=logging.INFO)

first_name_col = "firstName"
last_name_col = "lastName"
company_col = "companyName"
tab_name = "cleaned_profiles"

cmahuhun.process_records(
    api_key=hunter_api_key,
    google_creds_path=google_creds_path,
    file_id=file_id,
    first_name_col=first_name_col,
    last_name_col=last_name_col,
    company_col=company_col,
    tab_name=tab_name,
)

# %% [markdown]
# ## Dropcontact for remaining emails

# %% [markdown]
# ### Waiting for API keys

# %% [markdown]
# ## Email Verification

# %%
# df_drop = google_sheet_helper.read_sheet("1Etx_Ee9WihmgKAbn4PDN2JvAGWKFLydBAIdjYkuQRwY", "hunter_results")
# file_id = '1Etx_Ee9WihmgKAbn4PDN2JvAGWKFLydBAIdjYkuQRwY'
# sheet = google_sheet_helper.google_account.open_by_key(file_id)


# %%
hunter_instance = HunterIO(hunter_api_key)
verified_df = hunter_instance.verify_emails(df_drop, "hunter_extracted_email")

# %%
if file_id:
    # Create a new tab.
    cleaned_profiles_tab = sheet.add_worksheet(
        title="hunter_verification", rows="100", cols="20"
    )

    # Write the filtered DataFrame to the new tab.
    google_sheet_helper.write_results(file_id, verified_df, "hunter_verification")

    print(
        f"DataFrame written to new tab 'hunter_verification' in Google Sheet with file ID '{file_id}' successfully."
    )
else:
    print("Failed to create the Google Sheet.")

# %% [markdown]
# ## Final dataframe

# %%
final_df = google_sheet_helper.read_sheet(
    "1Etx_Ee9WihmgKAbn4PDN2JvAGWKFLydBAIdjYkuQRwY", "hunter_verification"
)


# %%
final_df = final_df[
    [
        "fullName",
        "profileUrl",
        "title",
        "hunter_extracted_email",
        "hunter_verification",
    ]
]
# Step 2: Filter out rows where 'hunter_extracted_email' is empty.
final_df = final_df[
    final_df["hunter_extracted_email"].notna()
    & (final_df["hunter_extracted_email"] != "")
]


# %%
if file_id:
    # Create a new tab.
    cleaned_profiles_tab = sheet.add_worksheet(
        title="final_df", rows="100", cols="20"
    )
    # Write the filtered DataFrame to the new tab.
    google_sheet_helper.write_results(file_id, final_df, "final_df")
    print(
        f"DataFrame written to new tab 'hunter_verification' in Google Sheet with file ID '{file_id}' successfully."
    )
else:
    print("Failed to create the Google Sheet.")
