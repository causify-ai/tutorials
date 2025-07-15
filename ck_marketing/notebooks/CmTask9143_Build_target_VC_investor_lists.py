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
# This notebook is used for a one time task of finding emails and profiles of target VC investors

# %%
# #!sudo /bin/bash -c "(source /venv/bin/activate; pip install --upgrade google-api-python-client)"


# %%
import logging
import os

import numpy as np
import pandas as pd

import ck_marketing.dropcontact.dropcontact_api as cmdrdrap
import ck_marketing.hunterio.hunter_api as cmhuhuap
import helpers.hdbg as hdbg
import helpers.henv as henv
import helpers.hprint as hprint
from ck_marketing.hunterio.hunter_api import GoogleSheetsHelper, HunterIO

# %%
# Configure logger.
hdbg.init_logger(verbosity=logging.INFO)
_LOG = logging.getLogger(__name__)

# Print system signature.
_LOG.info("%s", henv.get_system_signature()[0])

# Configure the notebook style.
hprint.config_notebook()

# %%
hunter_api_key = os.getenv("Hunter_API_KEY")
dropcontact_api_key = os.getenv("Drop_API_KEY")
phantom_api_key = os.getenv("Phantom_API_KEY")

# %%
google_creds_path = "service.json"
google_sheet_helper = GoogleSheetsHelper(google_creds_path)

# %%
file_id = "1mkBjvGDjlwXe-h1OOZjCGzcU2iddkj8rZlCF-AAuyRY"


# %%
df = google_sheet_helper.read_sheet(file_id)


# %%
df["firstName"] = df["Name"].str.split().str[0]
df["lastName"] = df["Name"].str.split().str[-1]

# %%
sheet = google_sheet_helper.google_account.open_by_key(file_id)
tab_name = "cleaned_profiles_1"
cleaned_profiles_tab = sheet.add_worksheet(title=tab_name, rows="100", cols="20")
google_sheet_helper.write_results(file_id, df, tab_name)

# %% [markdown]
# # HunterIO - Extract emails

# %%
first_name_col = "firstName"
last_name_col = "lastName"
company_col = "Firm"

cmhuhuap.process_records(
    api_key=hunter_api_key,
    google_creds_path=google_creds_path,
    file_id=file_id,
    first_name_col=first_name_col,
    last_name_col=last_name_col,
    company_col=company_col,
    tab_name=tab_name,
)

# %% [markdown]
# # DropContact - Extract Remaining emails

# %%
df_drop = google_sheet_helper.read_sheet(file_id, "hunter_results")


# %%
missing_email_df = df_drop[
    df_drop["hunter_extracted_email"].isna()
    | (df_drop["hunter_extracted_email"] == "")
]

# %%
# Prepare data for DropContact
first_names = missing_email_df["firstName"].tolist()
last_names = missing_email_df["lastName"].tolist()
company_names = missing_email_df["Firm"].tolist()

# Get emails from DropContact
dropcontact_results_df = cmdrdrap.get_email_from_dropcontact(
    first_names, last_names, company_names, dropcontact_api_key
)

# %%
# Replace special float values with NaN
df_drop.replace([np.inf, -np.inf], np.nan, inplace=True)
dropcontact_results_df.replace([np.inf, -np.inf], np.nan, inplace=True)

# Rename columns in dropcontact_results_df to match df_drop
dropcontact_results_df.rename(
    columns={"first name": "firstName", "last name": "lastName"}, inplace=True
)

# Merge the dataframes on 'firstNames' and 'lastName', keeping only the 'email' column from dropcontact_results_df
merged_df = pd.merge(
    df_drop,
    dropcontact_results_df[["firstName", "lastName", "email"]],
    on=["firstName", "lastName"],
    how="left",
)

# Rename the 'email' column to 'dropcontact_mail'
merged_df.rename(columns={"email": "dropcontact_mail"}, inplace=True)

# Count the non-null values in the 'dropcontact_mail' column
email_count = merged_df[
    merged_df["dropcontact_mail"].notna() & (merged_df["dropcontact_mail"] != "")
]["dropcontact_mail"].count()
print(f"Number of emails found: {email_count}")
print(f"Number of profile emails hunter could not find: {len(missing_email_df)}")

# %%
merged_df.replace({np.nan: "", np.inf: "", -np.inf: ""}, inplace=True)
cleaned_profiles_tab = sheet.add_worksheet(
    title="hunter_drop_emails", rows="100", cols="20"
)
google_sheet_helper.write_results(file_id, merged_df, "hunter_drop_emails")

# %%
merged_df["all_emails"] = (
    merged_df["hunter_extracted_email"]
    .fillna("")
    .replace("", pd.NA)
    .combine_first(merged_df["dropcontact_mail"])
)
merged_df.replace({np.nan: "", np.inf: "", -np.inf: ""}, inplace=True)

# %%
cleaned_profiles_tab = sheet.add_worksheet(
    title="all_emails", rows="100", cols="20"
)
google_sheet_helper.write_results(file_id, merged_df, "all_emails")

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
# # Final sheet

# %%
final_df = verified_df
# Step 2: Filter out rows where 'hunter_extracted_email' is empty.
final_df = final_df[
    final_df["all_emails"].notna() & (final_df["all_emails"] != "")
]

cleaned_profiles_tab = sheet.add_worksheet(
    title="found_and_verified_mails", rows="100", cols="20"
)
google_sheet_helper.write_results(file_id, final_df, "found_and_verified_mails")
