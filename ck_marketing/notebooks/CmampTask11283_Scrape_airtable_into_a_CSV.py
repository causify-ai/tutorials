# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.6
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# CONTENTS:
#

# %load_ext autoreload
# %autoreload 2
# %matplotlib inline

# +
# !sudo /bin/bash -c "(source /venv/bin/activate; pip install --quiet jupyterlab-vim)"
# !sudo /bin/bash -c "source /venv/bin/activate && pip install google-api-python-client"

# !jupyter labextension enable


# +
import logging

import pandas as pd

# /venv/lib/python3.12/site-packages/gspread_pandas/spread.py:401: FutureWarning: Downcasting behavior in `replace` is deprecated and will be removed in a future version. To retain the old behavior, explicitly call `result.infer_objects(copy=False)`. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)` .replace("", np.nan)
pd.set_option("future.no_silent_downcasting", True)

import helpers.hdbg as hdbg
import helpers.henv as henv
import helpers.hprint as hprint

# hcache.get_global_cache_info()
# hcache.clear_global_cache("all")


# +
hdbg.init_logger(verbosity=logging.INFO)

_LOG = logging.getLogger(__name__)

_LOG.info("%s", henv.get_system_signature()[0])

hprint.config_notebook()
# -

from ck_marketing.process_automation.workflows import GoogleSheetsHelper as GSH

gsheet_helper = GSH()

df_air = gsheet_helper.read_sheet("10t1YxmCTu3Kl8q3QsT-CqWWuXgg28bxtrpkNUnHp8Zo")

df_air.head()

len(df_air)

df_air[10:15]


def fix_shifted_rows(df):
    for index, row in df.iterrows():
        if row["Name"] == "Open":
            df.loc[index, "Name"] = row["Email"]
            df.loc[index, "Email"] = row["City"]
            df.loc[index, "City"] = row["State"]
            df.loc[index, "State"] = row["Website"]
            df.loc[index, "Website"] = row["Error_row"]
            df.loc[index, "Error_row"] = ""
    return df


df_air_cleaned = fix_shifted_rows(df_air)

len(df_air_cleaned)

df_air_cleaned[10:15]

gsheet_helper.write_results(
    "10t1YxmCTu3Kl8q3QsT-CqWWuXgg28bxtrpkNUnHp8Zo", df_air_cleaned, "cleaned_data"
)
