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

# # Imports

# !sudo /bin/bash -c "(source /venv/bin/activate; pip install --quiet jupyterlab-vim)"
# !jupyter labextension enable

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

# +
# #!sudo /bin/f bash -c "(source /venv/bin/activate; pip install --upgrade google-api-python-client)"

import importlib
import ck_marketing.process_automation.hyamm as hyamm
importlib.reload(hyamm)

import ck_marketing.hunterio.hunter_api as cmhuhuap
importlib.reload(cmhuhuap)

import helpers.hopenai as hopenai
# -

# # Load data

#normalize = False
normalize = True
contact_df = hyamm.get_data_from_GP_LIn_connections(normalize)
print("shape=", contact_df.shape)
contact_df.head(2)

# +
#hyamm.save_to_gsheet(df, name="connects")

# +
#df.iloc[11]
# -

contact_df = hyamm.clean_up_contact_df(contact_df, allow_no_emails=True)

# # Enrich

#mode = "AssumeEmailValid"
mode = "FromScratch"
contact_df_tmp = cmhuhuap.process_enrich(contact_df, "first_name", "last_name", "company_name", mode=mode)
display(contact_df_tmp.head(2))

# ## Update cache

print(hyamm.cache_stats_to_str())

hyamm.flush_cache_to_disk()

# ## Merge

contact_df_tmp.columns

contact_df_tmp2 = cmhuhuap.merge_hunterio_values(contact_df_tmp)

contact_df_tmp2.head(2)

hyamm.save_to_gsheet(contact_df_tmp2)

# # Add emails

mode = "AssumeEmailValid"
#mode = "FromScratch"
contact_df_tmp3 = cmhuhuap.process_email(contact_df_tmp2, "first_name", "last_name", "company_name", mode=mode)
display(contact_df_tmp3.head(2))

# # Diagnostics

diagnostics_df = cmhuhuap.get_diagnostic_df(contact_df_tmp)
display(diagnostics_df.head(2))

hyamm.save_to_gsheet(diagnostics_df, name="diagnostics_df")

# +
stats_dict = cmhuhuap.get_stats(diagnostics_df)

if False:
    import pprint
    pprint.pprint(stats_dict, sort_dicts=False)

df_tmp = cmhuhuap.get_stats_df(stats_dict)
display(df_tmp)

cmhuhuap.get_is_changed_stats(diagnostics_df)
# -

hyamm.save_to_gsheet(contact_df_tmp, name="gp_connects")

# # Categorize

# +
#keyword = "Partner", "VC", "invest", "Venture", "Director
keyword = "partner"
mask = [keyword in val.lower() for val in contact_df_tmp["job_title"]]
print(hprint.perc(sum(mask), len(mask)))

keyword = "vc"
mask = [keyword in val.lower() for val in contact_df_tmp["job_title"]]
print(hprint.perc(sum(mask), len(mask)))

keyword = "invest"
mask = [keyword in val.lower() for val in contact_df_tmp["job_title"]]
print(hprint.perc(sum(mask), len(mask)))

keyword = "venture"
mask = [keyword in val.lower() for val in contact_df_tmp["job_title"]]
print(hprint.perc(sum(mask), len(mask)))

keyword = "director"
mask = [keyword in val.lower() for val in contact_df_tmp["job_title"]]
print(hprint.perc(sum(mask), len(mask)))

# +
keyword = "partner"
mask = [keyword in val.lower() for val in contact_df_tmp["job_title"]]
print(hprint.perc(sum(mask), len(mask)))

contact_df_tmp[mask].head(5)
# -

#print("\n".join(sorted(contact_df_tmp["category"].unique())))
print(contact_df_tmp["category"].value_counts())

keyword = "Venture Capital & Private Equity"
#mask = [keyword in val.lower() for val in contact_df_tmp["category"]]
mask = contact_df_tmp["category"] == keyword
print(hprint.perc(sum(mask), len(mask)))

display(contact_df_tmp[mask].head())

# +
col_names = ["hash", "first_name", "last_name", "email", "job_title", "linkedin_url", "company_name"]
df = contact_df_tmp[mask][col_names]
df = df.sort_values(by="company_name")

hyamm.save_to_gsheet(df, name="gp_vc_connects")