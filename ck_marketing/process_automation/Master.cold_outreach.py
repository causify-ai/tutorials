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
# This Master notebook is a pipeline to extracting and validating profiles with emails using APIS of PhantomBustor, DropContact, Googlesheets and HunterIO.

# %%
# #!sudo /bin/bash -c "(source /venv/bin/activate; pip install --upgrade google-api-python-client)"


# %%
import logging
import os

import ck_marketing.hunterio.hunter_api as cmhuhuap
import ck_marketing.linkedin.profile_filtering as cmliprfi
import helpers.hdbg as hdbg
import helpers.henv as henv
import helpers.hprint as hprint
from ck_marketing.hunterio.hunter_api import GoogleSheetsHelper, HunterIO
from ck_marketing.linkedin.phantom_api.phantombustorrrr import Phantom

# %%
# Configure logger.
hdbg.init_logger(verbosity=logging.INFO)
_LOG = logging.getLogger(__name__)

# Print system signature.
_LOG.info("%s", henv.get_system_signature()[0])

# Configure the notebook style.
hprint.config_notebook()

# %% [markdown]
# # Phantom Bustor - Extract Profiles

# %%
# Get the API keys from the environment variables.
phantom_api_key = os.getenv("Phantom_API_KEY")
hunter_api_key = os.getenv("Hunter_API_KEY")
dropcontact_api_key = os.getenv("Drop_API_KEY")

# %%
# Initialize the Phantom instance.
phantom = Phantom(phantom_api_key)

# %%
sales_nav = os.getenv("sales_nav_query")
link = os.getenv("linkedin_cookie")
agent_name = 'Sequoia Capital'

# %%
phantom.create_sales_nav_phantom(agent_name, sales_nav, link)

# %%
# Get and print all agents and their IDs.
agents = phantom.get_all_agents()
print("List of all agents and their IDs:\n")
for agent in agents:
    print(f"Agent Name: {agent['name']}, Agent ID: {agent['id']}")

# %%
# Get agent ID and name.
AGENT_ID = "4773837904519897"

# %%
specific_agent_name = phantom.get_agent_name(AGENT_ID)
print(f"Selected Phantom: {specific_agent_name}")

# %%
# Launch the agent and get the results in a DataFrame.
df = phantom.launch_and_get_df(AGENT_ID)
print("DataFrame is fetched")

# %%
# Google Drive Setup.
google_creds_path = "service.json"
google_sheet_helper = GoogleSheetsHelper(google_creds_path)
drive_folder_id = "1fpsUZ8Nd52FGKxOuqVf11hzEetwvVoDq"
sheet_name = f"{specific_agent_name}_search_export"
tab_name = "search_export"

# %%
file_id = google_sheet_helper.create_new_sheet_from_df(
    df, sheet_name, drive_folder_id, tab_name
)

# %% [markdown]
# # Clean Profiles

# %%
words = ["talent"]
filtered_df = cmliprfi.filter_df(df, "title", words, "remove")

# %%
sheet = google_sheet_helper.google_account.open_by_key(file_id)
title_clean = "cleaned_profiles"
cleaned_profiles_tab = sheet.add_worksheet(
    title=title_clean, rows="100", cols="20"
)
google_sheet_helper.write_results(file_id, filtered_df, title_clean)

# %% [markdown]
# # HunterIO & Dropcontact - Extract emails

# %%
merged_df = cmhuhuap.hunter_drop_emails(
    "firstName",
    "lastName",
    "companyName",
    "Sheet1",
    hunter_api_key,
    google_creds_path,
    file_id,
    dropcontact_api_key,
)

# %% [markdown]
# # HunterIO - Verify emails

# %%
hunter_instance = HunterIO(hunter_api_key)
verified_df = hunter_instance.verify_emails(merged_df, "all_emails")

# %%
cleaned_profiles_tab = sheet.add_worksheet(
    title="hunter_verification", rows="100", cols="20"
)
google_sheet_helper.write_results(file_id, verified_df, "hunter_verification")

# %% [markdown]
# # Final dataframe

# %%
final_df = verified_df[
    [
        "fullName",
        "firstName",
        "lastName",
        "profileUrl",
        "title",
        "all_emails",
        "hunter_verification",
    ]
]
# Step 2: Filter out rows where 'hunter_extracted_email' is empty.
final_df = final_df[
    final_df["all_emails"].notna() & (final_df["all_emails"] != "")
]

cleaned_profiles_tab = sheet.add_worksheet(
    title="final_df", rows="100", cols="20"
)
google_sheet_helper.write_results(file_id, final_df, "final_df")

# %% [markdown]
# #  Delete Phantom

# %%
phantom.delete_phantom(AGENT_ID)
