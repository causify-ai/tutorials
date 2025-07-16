# %% [markdown]
# # Description

# %% [markdown]
# This script reads data, extracts mails of people using HunterIO and Dropcontact and writes it back to google sheet

# %%
#!sudo /bin/bash -c "(source /venv/bin/activate; pip install --upgrade google-api-python-client)"

# %%
import logging

import ck_marketing.hunterio.hunter_api as cmhuhuap
import helpers.hdbg as hdbg
import helpers.henv as henv
import helpers.hprint as hprint
from ck_marketing.hunterio.hunter_api import GoogleSheetsHelper

# %%
# Configure logger.
hdbg.init_logger(verbosity=logging.INFO)
_LOG = logging.getLogger(__name__)

# Print system signature.
_LOG.info("%s", henv.get_system_signature()[0])

# Configure the notebook style.
hprint.config_notebook()

# %%
# Google Drive Setup.
google_creds_path = "service.json"
google_sheet_helper = GoogleSheetsHelper(google_creds_path)


# %%
file_id = "1--ERHzSPVWgfFqjXQwGhFv4siH-RJIwoNr6iZC1pHJ8"
sheet = google_sheet_helper.google_account.open_by_key(file_id)
money_df = google_sheet_helper.read_sheet(file_id)

# %%
len(money_df)

# %%
money_df.tail()

# %%
money_df[["firstName", "lastName"]] = money_df["fullname"].str.split(
    " ", n=1, expand=True
)

# %%
title_clean = "cleaned_profiles"
cleaned_profiles_tab = sheet.add_worksheet(
    title=title_clean, rows="100", cols="20"
)
google_sheet_helper.write_results(file_id, money_df, title_clean)

# %%
money_df.tail()

# %%
merged_df = cmhuhuap.hunter_drop_emails(
    "firstName",
    "lastName",
    "companyName",
    title_clean,
    hunter_api_key,
    google_creds_path,
    file_id,
    dropcontact_api_key,
)
