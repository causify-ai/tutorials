# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.4
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
import datetime
import logging
import os

import pandas as pd
# /venv/lib/python3.12/site-packages/gspread_pandas/spread.py:401: FutureWarning: Downcasting behavior in `replace` is deprecated and will be removed in a future version. To retain the old behavior, explicitly call `result.infer_objects(copy=False)`. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)` .replace("", np.nan)
pd.set_option('future.no_silent_downcasting', True)

import helpers.hdbg as hdbg
import helpers.henv as henv
import helpers.hpandas as hpandas
import helpers.hprint as hprint
import helpers.hcache as hcache

#hcache.get_global_cache_info()
#hcache.clear_global_cache("all")

import config_root.config as cconfig

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

#gspread_pandas.conf.get_config()
print(gspread_pandas.conf.get_config()["project_id"])

# #!sudo /bin/f bash -c "(source /venv/bin/activate; pip install --upgrade google-api-python-client)"

import importlib
import ck_marketing.process_automation.hyamm as hyamm
importlib.reload(hyamm)

import ck_marketing.hunterio.hunter_api as cmhuhuap
importlib.reload(cmhuhuap)

#import helpers.hopenai as hopenai
# -

# # Load data

#normalize = False
normalize = True
df = hyamm.get_data_from_hedge_fund_list(normalize)
print("shape=", df.shape)
df.head(2)

contact_df = df

contact_df = hyamm.clean_up_contact_df(contact_df)

#mode = "AssumeEmailValid"
mode = "FromScratch"
#enrich_kwargs = {"issue_warnings": False}
enrich_kwargs = {}
contact_df_tmp = cmhuhuap.process_enrich(contact_df, "first_name", "last_name", "company_name", mode=mode)
display(contact_df_tmp.head(2))

hyamm.flush_cache_to_disk()

contact_df_enriched = cmhuhuap.merge_hunterio_values(contact_df)

contact_df_enriched = hpandas.filter_df(contact_df_enriched, "email", "_nan_", invert=True, check_value=False)

hyamm.sanity_check_contact_df(contact_df_enriched)

contact_df_enriched.head(2)

# +
mode = "AssumeEmailValid"
contact_df_enriched = cmhuhuap.process_email(contact_df_enriched, "first_name", "last_name", "company_name", mode=mode, is_company=True)

contact_df_enriched["email_verification"] = contact_df_enriched["hunterio.email_verification"]
# -

contact_df_enriched

hyamm.save_to_gsheet(contact_df_enriched, name="hedge_funds")

# # Diagnostics

assert 0

# +
diagnostics_df = cmhuhuap.get_diagnostic_df(contact_df_tmp)
display(diagnostics_df.head(2))

stats_dict = cmhuhuap.get_stats(diagnostics_df)

if False:
    import pprint
    pprint.pprint(stats_dict, sort_dicts=False)

df_tmp = cmhuhuap.get_stats_df(stats_dict)
display(df_tmp)
# -

hyamm.save_to_gsheet(contact_df_tmp, name="hedge_fund_updated")
