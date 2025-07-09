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

# %% [markdown]
# # Description
#
# ## This notebook is used to extract the extract emails of potential profiles and create a outreach list from top VC companies.

# %%
# %load_ext autoreload
# %autoreload 2

import logging
import os

import numpy as np

import ck_marketing.hunterio.hunterapi as cmahuhun
import ck_marketing.linkedin.profile_filtering as cmliprfi
import helpers.hgoogle_file_api as hgfiapi
from ck_marketing.hunterio.hunterapi import GoogleSheetsHelper, HunterIO
from ck_marketing.linkedin.phantombuster_api import Phantom
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

# %% [markdown]
# ## Extracting Profiles - Phantom Bustor

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
AGENT_ID = "7890616458359264"

# %%
specific_agent_name = phantom.get_agent_name(AGENT_ID)
print(f"Selected Phantom: {specific_agent_name}")

# %%
# Google Drive Setup.
google_creds_path = "service.json"
google_sheet_helper = GoogleSheetsHelper(google_creds_path)
drive_folder_id = "1utxjyRBuLR1RxCpX_B5xm6fC5bYYp7Ex"
sheet_name = f"{specific_agent_name}_search_export"
tab_name = "search_export"

# %%
# Launch the agent and get the results in a DataFrame
phantom.launch_agent(AGENT_ID)
result_response_json = phantom.fetch_agent_results(AGENT_ID)

# %%
csv_url = phantom.get_csv_url(result_response_json.get("output", ""))
df = phantom.download_csv(csv_url)
df = df.replace([np.nan, np.inf, -np.inf], "", inplace=False)
print("DataFrame is fetched")
# print(df.head(2))

# %%
# Create the Google Sheet and get the file ID.
file_id = hgfiapi.create_empty_google_file("sheet", sheet_name, drive_folder_id)

# Initialize Google Sheets Helper.
google_sheets_helper = GoogleSheetsHelper(google_creds_path)
sheet = google_sheets_helper.google_account.open_by_key(file_id)
default_worksheet = sheet.get_worksheet(0)
new_tab_name = "search_export"
default_worksheet.update_title(new_tab_name)
# Write the DataFrame to the renamed default tab.
google_sheets_helper.write_results(file_id, df, new_tab_name)
print(
    f"DataFrame written to Google Sheet '{new_tab_name}' in file ID '{file_id}' successfully."
)


# %% [markdown]
# ## Clean Profiles - Filtering

# %%
words = []

# %%
filtered_df = cmliprfi.filter_df(df, "title", words, "keep")

# %%
cleaned_profiles_tab = sheet.add_worksheet(
    title="cleaned_profiles", rows="100", cols="20"
)
# Write the filtered DataFrame to the new tab.
google_sheet_helper.write_results(file_id, filtered_df, "cleaned_profiles")
print(
    f"Filtered DataFrame written to new tab 'cleaned_profiles' in Google Sheet with file ID '{file_id}' successfully."
)

# %% [markdown]
# ## Extracting emails - HunterIO

# %%
if False:
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
# ## Email Verification - HunterIO

# %%
if False:
    df_drop = google_sheet_helper.read_sheet(file_id, "hunter_results")
    hunter_instance = HunterIO(hunter_api_key)
    verified_df = hunter_instance.verify_emails(df_drop, "hunter_extracted_email")
    cleaned_profiles_tab = sheet.add_worksheet(
        title="hunter_verification", rows="100", cols="20"
    )
    google_sheet_helper.write_results(file_id, verified_df, "hunter_verification")
    print(
        f"Filtered DataFrame written to new tab in Google Sheet with file ID '{file_id}' successfully."
    )


# %% [markdown]
# ## Final dataframe

# %%
final_df = verified_df[
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

cleaned_profiles_tab = sheet.add_worksheet(
    title="final_df", rows="100", cols="20"
)
google_sheet_helper.write_results(file_id, final_df, "final_df")
print(
    f"Filtered DataFrame written to new tab in Google Sheet with file ID '{file_id}' successfully."
)
