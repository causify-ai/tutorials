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
# ## This notebook is used to extract the VCs from GPs linkedin connections

# %%
import logging

import ck_marketing.linkedin.profile_filtering as cmliprfi
from ck_marketing.hunterio.hunterapi import GoogleSheetsHelper
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
google_creds_path = "service.json"
google_sheet_helper = GoogleSheetsHelper(google_creds_path)

# %%
df = google_sheet_helper.read_sheet(
    "1oJ8wHXWDBeyVW4WQt08oC3X3Nl7HCnqClalSvOj5wNs"
)

# %%
words = ["Partner", "VC", "invest", "Venture", "Director"]

# %%
filtered_df_VC = cmliprfi.filter_df(df, "title", words, "keep")
filtered_df_non_VC = cmliprfi.filter_df(df, "title", words, "remove")

# %%
file_id = "1oJ8wHXWDBeyVW4WQt08oC3X3Nl7HCnqClalSvOj5wNs"
sheet = google_sheet_helper.google_account.open_by_key(file_id)
sheet.add_worksheet(title="VC", rows="100", cols="20")
sheet.add_worksheet(title="non_VC", rows="100", cols="20")
google_sheet_helper.write_results(file_id, filtered_df_VC, "VC")
google_sheet_helper.write_results(file_id, filtered_df_non_VC, "non_VC")
print(
    f"Filtered DataFrames written in Google Sheet with file ID '{file_id}' successfully."
)

# %% [markdown]
# ## Some Stats

# %%
df_clean = google_sheet_helper.read_sheet(
    "1oJ8wHXWDBeyVW4WQt08oC3X3Nl7HCnqClalSvOj5wNs", "cleaned_profiles"
)

# %%
# Count the total number of 'FP' and 'FN'
fp_count = df_clean[df_clean["Predicted"] == "FP"].shape[0]
fn_count = df_clean[df_clean["Predicted"] == "FN"].shape[0]
tp_count = df_clean[df_clean["Predicted"] == "TP"].shape[0]
tn_count = df_clean[df_clean["Predicted"] == "TN"].shape[0]


print(f"Total number of FP: {fp_count}")
print(f"Total number of FN: {fn_count}")
print(f"Total number of FP: {tp_count}")
print(f"Total number of FN: {tn_count}")


# %%
# Filter rows with 'FP' and 'FN'
fp_rows = df_clean[df_clean["Predicted"] == "FP"][["fullName", "title"]]
fn_rows = df_clean[df_clean["Predicted"] == "FN"][["fullName", "title"]]

print("Rows with FP:")
print(fp_rows)

print("Rows with FN:")
print(fn_rows)
