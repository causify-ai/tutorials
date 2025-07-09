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
import helpers.hpandas as hpandas
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

# # Load Contact data

contact_dfs = []

# ## Search4.FinTech_VC_in_US.SalesNavigator

normalize = True
df_tmp = cmprauhy.get_scraped_data_from_LinkedIn(normalize)
contact_dfs.append(df_tmp)

cmprauhy.print_contact_df_stats(df_tmp)

# ## VC_search_export

normalize = True
df_tmp = cmprauhy.get_scraped_data_from_LinkedIn2(normalize)
contact_dfs.append(df_tmp)

cmprauhy.print_contact_df_stats(df_tmp)

# +
# hyamm.print_contact_df_detailed_stats(df_tmp)
# -

# ## Search7.AI_VC_in_US.gsheet

normalize = True
# normalize = False
df_tmp = cmprauhy.get_scraped_data_from_LinkedIn3(normalize)
contact_dfs.append(df_tmp)

cmprauhy.print_contact_df_stats(df_tmp)

# ## VC Tier 1 - Partners

normalize = True
df_tmp = cmprauhy.get_scraped_data_from_LinkedIn4(normalize)
contact_dfs.append(df_tmp)

cmprauhy.print_contact_df_stats(df_tmp)

# ## VC_Tier_2_Partners

normalize = True
df_tmp = cmprauhy.get_scraped_data_from_LinkedIn5(normalize)
contact_dfs.append(df_tmp)

cmprauhy.print_contact_df_stats(df_tmp)

# ## VCSheet

normalize = True
# normalize = False
df_tmp = cmprauhy.get_scraped_data_from_VCSheet(normalize)
contact_dfs.append(df_tmp)

cmprauhy.print_contact_df_stats(df_tmp)

# ## Euro-VCs

normalize = True
# normalize = False
df_tmp = cmprauhy.get_scraped_data_from_EuroVC(normalize)
contact_dfs.append(df_tmp)

cmprauhy.print_contact_df_stats(df_tmp)

# ## Folkapp

normalize = True
# normalize = False
df_tmp = cmprauhy.get_scraped_data_from_FolkApp(normalize)
contact_dfs.append(df_tmp)

cmprauhy.print_contact_df_stats(df_tmp)

# ## GP_LIn_Connections

normalize = True
# normalize = False
df_tmp = cmprauhy.get_data_from_GP_LIn_connections(normalize)
contact_dfs.append(df_tmp)

cmprauhy.print_contact_df_stats(df_tmp)

# # Concat all

contact_df = pd.concat(contact_dfs)
debug = ""
# debug = "duplicated_emails"
# debug = "remove_chinese_names"
# debug = "remove_empty_first_name"
# debug = "clean_company_names"
# debug = "clean_linkedin_emails"
# debug = "clean_linkedin_websites"
contact_df = cmprauhy.clean_up_contact_df(contact_df, debug=debug)
display(contact_df.head(2))

cmprauhy.print_contact_df_detailed_stats(contact_df)

cmprauhy.sanity_check_contact_df(contact_df)

cmprauhy.print_contact_df_stats(contact_df)

contact_df["origin"].value_counts()

cmprauhy.save_to_gsheet(contact_df)

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

# ## Clean up names

# +
contact_df = cmliliut.clean_and_track_name_changes(contact_df)

debug_df = cmliliut.get_debug_clean_name_df(contact_df)
cmliliut.get_clean_name_stats(contact_df)
# -

hpandas.filter_df(debug_df, "is_modified", True).head(2)

# +
contact_df = cmliliut.merge_clean_names_df(contact_df)

contact_df.head(1)
# -

# ## Enrich data

print(contact_df.shape)
contact_df.head(2)

# mode = "AssumeEmailValid"
mode = "FromScratch"
# dry_run = True
dry_run = False
# enrich_kwargs = {"issue_warnings": False}
enrich_kwargs = {}
contact_df2 = cmhuhuap.process_enrich(
    contact_df,
    "first_name",
    "last_name",
    "company_name",
    mode=mode,
    dry_run=dry_run,
)
display(contact_df2.head(1))

print(contact_df2.columns)

cmprauhy.get_column_stats(
    contact_df2,
    ["email", "email_verification", "hunterio.email"],
    info_mode="only_pct",
)

cmprauhy.flush_cache_to_disk()  # "find_email")

cmprauhy.flush_cache_to_disk()  # "find_email")

# ## Merge Hunter.io enrichment

print(contact_df2.columns)

del contact_df_enriched

contact_df3 = cmhuhuap.merge_hunterio_values(contact_df2)

cmprauhy.sanity_check_contact_df(contact_df3)

print(contact_df3.columns)

cmprauhy.head(contact_df3, num_rows=2)

cmprauhy.get_column_stats(contact_df3, ["email", "email_verification"])

stats_df = cmprauhy.print_contact_df_detailed_stats(contact_df3)

# +
# hyamm.save_to_gsheet(contact_df_enriched, name="contact_df_enriched")
# -

# ## Infer category

cmprauhy.get_value_counts_stats_df(contact_df3, "category")

contact_df_tmp = cmprauhy.infer_category(contact_df3)

# ## Validate email

cmhuhuap.get_account_info()

contact_df4 = contact_df3.copy()
print(contact_df4.shape)
contact_df4.head(2)

cmprauhy.print_contact_df_stats(contact_df4)

cmprauhy.enable_cache_perf("verify_email")
mode = "AssumeEmailValid"
dry_run = True
is_company = True
contact_df5 = cmhuhuap.process_email(
    contact_df4,
    "first_name",
    "last_name",
    "company_name",
    is_company,
    mode=mode,
    dry_run=dry_run,
)

cmprauhy.save_to_gsheet(contact_df5)

cmprauhy.print_contact_df_stats(contact_df5)

# +
# diagnostics_df = cmhuhuap.get_diagnostic_df(contact_df_tmp)
# display(diagnostics_df.head(2))

# import pprint
# pprint.pprint(cmhuhuap.get_stats(diagnostics_df), sort_dicts=False)
# -

cmprauhy.force_cache_from_disk()

cmprauhy.flush_cache_to_disk()  # "find_email")

print(cmprauhy.cache_stats_to_str())

cols = [
    "first_name",
    "last_name",
    "email",
    "company_name",
    "hunterio.email",
    "is_email_changed",
]
mask = contact_df_tmp["is_email_changed"]
contact_df_tmp.loc[mask][cols]

contact_df_tmp["hunterio.email_verification"].unique()

# ## Check category

contact_df_tmp2 = contact_df_tmp.copy()
display(contact_df_tmp2.head(1))

cmprauhy.get_value_counts_stats_df(contact_df_tmp2, "category", num_rows=20)

# +
# categories = ["Venture Fund (inferred)", "Venture Fund", "Venture Capital & Private Equity", "Accelerator", "Corporate VC", "Family Office"]
# contact_df_tmp2 = hpandas.filter_df(contact_df_tmp2, "category", categories)
# contact_df_tmp2 = hpandas.filter_df(contact_df_tmp2, "email", "_nan_", invert=True)

# +
# hpandas.filter_df(contact_df_tmp2, "category", "").head(3)
# -

contact_df_tmp2 = hpandas.filter_df(
    contact_df_tmp2, "category", ["Financial Services", "Family Office"]
)
# contact_df_tmp2 = hpandas.filter_df(contact_df_tmp2, "email", "_nan_", invert=True)
# mask = contact_df_tmp2["company_name"].isin(["Engineers Gate", "Teza Technologies", "RavenPack"])
# contact_df_tmp2 = contact_df_tmp2[~mask]

cmprauhy.sanity_check_contact_df(contact_df_tmp2)

# +
mode = "AssumeEmailValid"
contact_df_tmp3 = cmhuhuap.process_email(
    contact_df_tmp2,
    "first_name",
    "last_name",
    "company_name",
    mode=mode,
    is_company=True,
)

contact_df_tmp3["email_verification"] = contact_df_tmp3[
    "hunterio.email_verification"
]
# -

contact_df_tmp3.head()

cmprauhy.save_to_gsheet(contact_df_tmp3, name="financial")

cmprauhy.get_value_counts_stats_df(contact_df_tmp3, "origin", num_rows=20)

contact_df = contact_df_tmp3

# # YAMM pipeline

# ## Read and merge data

yamm_df = cmprauhy.get_yamm_results()

display(yamm_df.head(3))

yamm_df["campaign_name"].unique()

cmprauhy.yamm_stats_to_pct(yamm_df)

cmprauhy.yamm_stats_by_campaign(yamm_df)

# +
# hyamm.save_to_gsheet(yamm_df)
# -

# ## Load data

url = "https://docs.google.com/spreadsheets/d/1KosRM5j6cFz8mm3Aw-ctIncAPOLx5bF1bkcEFrHnJsY"
yamm_df = cmprauhy.get_cached_sheet_to_df(url, "Sheet1")
print(yamm_df.shape)
display(yamm_df.head(5))

# hyamm.yamm_stats(yamm_df)
cmprauhy.yamm_stats_to_pct(yamm_df)

# ## Update Contact_df with YAMM data

print(contact_df.shape)
contact_yamm_df = cmprauhy.update_contact_df_with_yamm_df(contact_df, yamm_df)
print(contact_yamm_df.shape)

# campaign_name = "campaign0_VC_causify"
campaign_name = "campaign2_VC_UMD"
# Pick the one already sent.
# df_tmp = hpandas.filter_df(contact_yamm_df, campaign_name, "", invert=True)
df_tmp = hpandas.filter_df(contact_yamm_df, campaign_name, "", invert=False)
cmprauhy.get_short_contact_df(df_tmp)

# +
# mask = yamm_df["campaign_name"] == "campaign2_VC_UMD"
# print(mask.sum())

# +
# mask2 = contact_yamm_df["campaign2_VC_UMD"] != ""
# print(mask2.sum())
# -

# # Extract YAMM / LIN campaign

assert 0

# campaign_col_name = "campaign0_VC_causify"
# campaign_col_name = "campaign1_VC_causify"
campaign_col_name = "campaign2_VC_UMD"
type_ = "email"
# type_ = "linkedin"
# num_rows = 10
num_rows = -1
campaign_df, contact_df2 = cmprauhy.select_campaign(
    contact_yamm_df, campaign_col_name, type_, num_rows, seed=2
)

contact_df2.head(2)

hpandas.filter_df(contact_df2, campaign_col_name, "selected").head(2)

print(campaign_df.shape)
campaign_df.head()

cmprauhy.save_to_gsheet(campaign_df, name="campaign_3_LIN_VC")

# # One-offs

#
(
    "Wave1-20241210-folkapp1",
    "campaign0_VC_causify",
    "https://docs.google.com/spreadsheets/d/1mwRy0yTTCnTR14npWe7xATBYLb7DV9Pt1a2p4DjloQA",
    ["YAMM-20241210", "YAMM-20241210-1", "YAMM-20241210-2"],
),
#
(
    "Wave2-20241210-folkapp1",
    "campaign0_VC_causify",
    "https://docs.google.com/spreadsheets/d/1eufg2XREYbXnCy8tygGKAkDigM0OE_fJRmnHTDxFQ8A",
    ["YAMM-2024-12-"],
),
#
(
    "campaign_1_batch1",
    "campaign1_VC_causify",
    "https://docs.google.com/spreadsheets/d/10bWbYHdzl5KvvccHI5grtquFraO29MFP3iBcwkuVj1A",
    ["Sheet1", "Sheet2"],
),
#
(
    "Campaign2_UMD_YAMM",
    "campaign2_VC_UMD",
    "https://docs.google.com/spreadsheets/d/1rpM5MeMtAwRvbV1fCngKD4"
    "-xe7Wc19ikvs7ljx9HIeA",
    ["2024-12-28"],
),

# +
# url = "https s://docs.google.com/spreadsheets/d/1rpM5MeMtAwRvbV1fCngKD4-xe7Wc19ikvs7ljx9HIeA"
# url = "https://docs.google.com/spreadsheets/d/1mwRy0yTTCnTR14npWe7xATBYLb7DV9Pt1a2p4DjloQA"
url = "https://docs.google.com/spreadsheets/d/1eufg2XREYbXnCy8tygGKAkDigM0OE_fJRmnHTDxFQ8A"
gsheet_name = "YAMM-2024-12-"
df = cmprauhy.get_cached_sheet_to_df(url, gsheet_name)
# display(df.head(3))

res_df = df.merge(
    contact_df, left_on="email", right_on="email", how="left"
)  # [["hash"] + df.columns.tolist()]
hash_ = res_df["hash"]
res_df = df.copy()
res_df.insert(0, "hash", hash_)

res_df.head()
# -

hpandas.filter_df(res_df, "hash", "", check_value=False)

cmprauhy.save_to_gsheet(res_df, name="test1")

url = "https://docs.google.com/spreadsheets/d/1zJtF9q6NC9hEM3arUxr7vzVNmSyfxrybcYNkOaisjC4/edit?gid=796026511#gid=796026511"
df = cmprauhy.get_cached_sheet_to_df(url, "SaaS Angel Investors (Globally)")

cmprauhy.save_to_gsheet(df)
