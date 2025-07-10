# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.7
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# !sudo /bin/bash -c "(source /venv/bin/activate; pip install --quiet jupyterlab-vim)"
# !jupyter labextension enable

# # Imports

# %load_ext autoreload
# %autoreload 2
# %matplotlib inline

# +
# %%
import logging

import pandas as pd

# /venv/lib/python3.12/site-packages/gspread_pandas/spread.py:401: FutureWarning: Downcasting behavior in `replace` is deprecated and will be removed in a future version. To retain the old behavior, explicitly call `result.infer_objects(copy=False)`. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)` .replace("", np.nan)
pd.set_option("future.no_silent_downcasting", True)

import helpers.hdbg as hdbg
import helpers.henv as henv
import helpers.hprint as hprint

# hcache.get_global_cache_info()
# hcache.clear_global_cache("all")


# %%
hdbg.init_logger(verbosity=logging.INFO)

_LOG = logging.getLogger(__name__)

_LOG.info("%s", henv.get_system_signature()[0])

hprint.config_notebook()

# +
import gspread

print(gspread.__version__)

import gspread_pandas

print(gspread_pandas.__version__)

# gspread_pandas.conf.get_config()
print(gspread_pandas.conf.get_config()["project_id"])

# #!sudo /bin/f bash -c "(source /venv/bin/activate; pip install --upgrade google-api-python-client)"

import importlib

import ck_marketing.process_automation.hyamm as cmprauhy

importlib.reload(hyamm)

import ck_marketing.hunterio.hunter_api as cmhuhuap

importlib.reload(cmhuhuap)

import ck_marketing.linkedin.linkedin_utils as cmliliut

# import helpers.hopenai as hopenai
# -

# # Load data

# +
url = "https://docs.google.com/spreadsheets/d/1kxB15NcHcuhEVtD982qnvbx276J7fmDKvJx63rRpD0E/edit?gid=381241246#gid=381241246"
df = cmprauhy.get_cached_sheet_to_df(url, "List of investors")

# Add column.
columns = df.iloc[0, :].tolist()
columns = [v.split("\n")[0] if "\n" in v else v for v in columns]
columns = [v.strip() for v in columns]
df.columns = columns

# Remove the first row.
df = df.iloc[1:, :]

display(df.head(1))

for col_name in df.columns:
    df[col_name] = df[col_name].str.strip()

# Convert to true/false.
for col_name in df.columns:
    # print("'%s': %s" % (col_name, df[col_name].unique()))
    if col_name in (
        "Name",
        "Email",
        "LinkedIn",
        "Check sizes",
        "Other options",
        "Other types",
        "Other regions",
        "Other sectors",
    ):
        continue
    # #col_name = "Pre-seed"
    hdbg.dassert_is_subset(df[col_name].unique(), ("TRUE", "FALSE"))
    df[col_name] = [(v == "TRUE") for v in df[col_name]]

df.index = range(0, len(df))

# # Split names.
# df.insert(1, "first_name", "")
# df.insert(2, "last_name", "")
# for idx, v in enumerate(df["Name"]):
#     data = v.split()
#     if len(data) > 0:
#         df.loc[idx, "first_name"] = data[0]
#     if len(data) > 1:
#         df.loc[idx, "last_name"] = " ".join(data[1:])
df = cmprauhy.split_first_last_name(df, "Name")

df["origin"] = "super_networking"
cols_map = {
    "origin": None,
    "LinkedIn": "linkedin_url",
    "first_name": None,
    "last_name": None,
    "Email": "email",
}
df = cmprauhy._rename_columns_to_contact_schema(df, cols_map)

#
display(df.head(10))
# -

normalize = True
df = cmprauhy.get_data_from_super_networking_gsheet(normalize)

# +
# df.iloc[1]
# -

# ## Clean up names

# +
df = cmliliut.clean_and_track_name_changes(df)

debug_df = cmliliut.get_debug_clean_name_df(df)
cmliliut.get_clean_name_stats(df)
# -

df = cmprauhy.add_hash(df)
df.head(1)

# +
# hyamm.save_to_gsheet(df)
# -

# Merge.
df = cmliliut.merge_clean_names_df(df)

df2 = cmprauhy.filter_super_networking_gsheet(df)

display(cmprauhy.head(df2, seed=1, num_rows=10))

# +
mask = [v != "" for v in df2["email"]]
print(hprint.perc(sum(mask), len(mask)))

mask = [v != "" for v in df2["linkedin_url"]]
print(hprint.perc(sum(mask), len(mask)))
# -

display(df2.head())

cmprauhy.save_to_gsheet(df2)
