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

# # Imports

# +
# # !sudo /bin/bash -c "(source /venv/bin/activate; pip install --quiet jupyterlab-vim)"
# # !jupyter labextension enable
# -

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


# import helpers.hopenai as hopenai
# -

# # Process Contact data

# ## Read  data

assert 0

# url = "https://docs.google.com/spreadsheets/d/1nlfOHLUo2iTuNtFb2T5ZJXZZnztAnr3WzG9Jm5lbk6I"
url = "https://docs.google.com/spreadsheets/d/1HanQiolicUToLgQFv1__cPOP4WLks5r7pHcgu2P8BjM"
contact_df = cmprauhy.get_cached_sheet_to_df(url, "Sheet1")
contact_df.set_index("hash", drop=True, inplace=True)
#
cmprauhy.head(contact_df)

contact_df = cmprauhy.clean_up_contact_df(contact_df)

cmprauhy.sanity_check_contact_df(contact_df)

cmprauhy.print_contact_df_stats(contact_df)

contact_df["origin"].value_counts()

stats_df = cmprauhy.print_contact_df_detailed_stats(contact_df)

# ## Enrich data

print(contact_df.shape)
contact_df.head(2)

cmprauhy.reset_cache_property()
# hyamm.set_cache_property("enrich", "abort_on_cache_miss", True)
print(cmprauhy.cache_property_to_str("enrich"))

cmprauhy.reset_mem_cache()

cmprauhy.cache_stats_to_str()

cmprauhy.force_cache_from_disk()

first_name = "Tyrome"
last_name = "Smith"
company_name = "Go In Now, LLC"
is_company = True
cmhuhuap.enrich(first_name, last_name, company_name, is_company)
# print(cmhuhuap.enrich)

func_name = "enrich"
cmprauhy.enable_cache_perf(func_name)
# hyamm.set_cache_property(func_name, "abort_on_cache_miss", True)
cmprauhy.set_cache_property(func_name, "report_on_cache_miss", True)

# mode = "AssumeEmailValid"
mode = "FromScratch"
# enrich_kwargs = {"issue_warnings": False}
enrich_kwargs = {}
contact_df2 = cmhuhuap.process_enrich(
    contact_df, "first_name", "last_name", "company_name", mode=mode
)
display(contact_df2.head(2))

print(cmprauhy.get_cache_perf_stats(func_name))
cmprauhy.disable_cache_perf(func_name)

print(contact_df2.columns)

cmhuhuap.get_column_stats(
    contact_df2, ["email", "email_verification", "hunterio.email"]
)

cmprauhy.flush_cache_to_disk()  # "find_email")

cmprauhy.flush_cache_to_disk()  # "find_email")
