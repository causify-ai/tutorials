"""
Import as:

import ck_marketing.process_automation.hyamm as cmprauhy
"""

import glob
import hashlib
import logging
import re
from typing import Any, Dict, List, Tuple, Union

import gspread_pandas
import numpy as np
import pandas as pd
from IPython.display import display
from tqdm.autonotebook import tqdm

import helpers.hdbg as hdbg

# import helpers.hcache as hcache
import helpers.hpandas as hpandas
import helpers.hprint as hprint
import helpers.hsystem as hsystem

_LOG = logging.getLogger(__name__)


# #############################################################################
# Contact df
# #############################################################################


# @hcache.cache(set_verbose_mode=False)
# @hcache_simple.simple_cache(cache_type="pickle", write_through=True)
def get_cached_sheet_to_df(url: str, sheet_name: str) -> pd.DataFrame:
    _LOG.info("Reading data from url='%s' sheet_name='%s'" % (url, sheet_name))
    spread = gspread_pandas.Spread(url)
    df = spread.sheet_to_df(sheet=sheet_name, index=None)
    return df


def get_cached_sheet_to_df2(url: str, sheet_name: str) -> pd.DataFrame:
    _LOG.info("Reading data from url='%s' sheet_name='%s'" % (url, sheet_name))
    spread = gspread_pandas.Spread(url)
    df = spread.sheet_to_df(sheet=sheet_name, index=None)
    return df


contact_schema = [
    "hash",
    "origin",
    # When it was scraped.
    "timestamp",
    "first_name",
    "last_name",
    # Email.
    "email",
    "email_verification",
    "linkedin_url",
    "job_title",
    "job_title_description",
    "company_name",
    "company_domain",
    "city",
    # Seed,Convertible Note,Series A,Pre-Seed
    "stages",
    "restrictions",
    "industry",
    # Angel, VC, PE, Family Office, Corporate VC, Accelerator, Incubator
    "category",
    "notes",
]


# cols_map = {
#     "origin": "origin",
#     # When it was scraped.
#     "timestamp": "timestamp",
#     "first_name": "first_name",
#     "last_name": "last_name",
#     # Email.
#     "email": "email",
#     "email_verification": "email_verification",
#     "linkedin_url": "linkedin_url",
#     "job_title": "job_title",
#     "job_title_description": "job_title_description",
#     "company_name": "company_name",
#     "company_domain": "company_domain",
#     "city": "city",
#     # Seed,Convertible Note,Series A,Pre-Seed
#     "stages": "stages",
#     "restrictions": "restrictions",
#     "industry": "industry",
#     # Angel, VC, PE, Family Office, Corporate VC, Accelerator, Incubator
#     "category": "category",
#     "notes": "notes",
# }


_ColumnMap = Dict[str, str]


def _resolve_None_in_cols_map(cols_map: _ColumnMap) -> _ColumnMap:
    """
    Resolve the `None` values in a column mapping, since `None` means pass-
    through.
    """
    cols_map_out = {}
    for k, v in cols_map.items():
        if v is None:
            v = k
        cols_map_out[k] = v
    print(cols_map_out)
    hdbg.dassert_no_duplicates(cols_map_out.keys())
    hdbg.dassert_no_duplicates(cols_map_out.values())
    return cols_map_out


def _rename_columns_to_contact_schema(
    df: pd.DataFrame,
    cols_map: _ColumnMap,
) -> Tuple[pd.DataFrame, _ColumnMap]:
    """
    Rename the columns of a DataFrame to match the Contact schema.
    """
    df = df.copy()
    # Resolve the pass-through columns, marked with a target value of `None`.
    cols_map = _resolve_None_in_cols_map(cols_map)
    # Rename the columns, making sure that they are all available.
    hdbg.dassert_is_subset(
        cols_map.keys(),
        df.columns,
    )
    hdbg.dassert_no_duplicates(df.columns.tolist())
    df.rename(columns=cols_map, inplace=True, errors="raise")
    hdbg.dassert_no_duplicates(df.columns.tolist())
    return (df, cols_map)


def split_first_last_name(df: pd.DataFrame, name_col: str) -> pd.DataFrame:
    df = df.copy()
    df.insert(1, "first_name", "")
    df.insert(2, "last_name", "")
    for idx, v in enumerate(df[name_col]):
        data = v.split()
        if len(data) > 0:
            df.loc[idx, "first_name"] = data[0]
        if len(data) > 1:
            df.loc[idx, "last_name"] = " ".join(data[1:])
    return df


# The difference between `normalize()` and `sanity_check()` is that:
# - `normalize()` performs some transformations to the data;
# - `sanity_check()` just checks that the data is in the correct format.Q

# We distinguish tokens as:
# - "empty space": the data is missing since there was no attempt to fill it in
# - a "nan": the data was attempted to be filled in, and was not found


def normalize_contact_schema(
    df: pd.DataFrame, cols_map: _ColumnMap
) -> pd.DataFrame:
    """
    Normalize a dataframe to use the Contact schema, based on the column reamp.

    The output has:
    - The columns in the Contact schema.
    - All tokens are marked as `_..._` to separate them from actual values
    - Empty values means that the data was not attempted

    :param df: The DataFrame to normalize.
    :param cols_map: A dictionary mapping the original column names to
        the new column names.
    """
    df = df.copy()
    _LOG.debug(hprint.to_str("df.columns"))
    # 1) Convert data into Contact schema.
    df, cols_map = _rename_columns_to_contact_schema(df, cols_map)
    _LOG.debug(hprint.to_str("df.columns"))
    df = df[cols_map.values()]
    hdbg.dassert_is_subset(
        df.columns, contact_schema, "All columns must be in contact schema"
    )
    # 2) Create missing columns.
    for col in contact_schema:
        if col not in df.columns:
            df[col] = ""
    hdbg.dassert_eq(sorted(df.columns), sorted(contact_schema))
    # 3) Remove empty spaces from all columns.
    for col in df.columns:
        df[col] = df[col].str.strip()
    # 4) Use only canonical values for `email` column.
    if "email" in df.columns:
        # Create a mask where the '@' symbol is absent.
        mask = df["email"].apply(lambda x: "@" not in str(x))
        # Find unique values where '@' is missing.
        token_values = df["email"][mask].unique()   
        replacement_dict = {email: np.nan for email in token_values if email not in ["", "nan"]}
        df["email"] = df["email"].replace(replacement_dict)
        corrected_token_values = df["email"][mask].unique()
        hdbg.dassert_is_subset(corrected_token_values, ["", "nan", np.nan])
    # 5) Use only canonical values for `email_verification` column.
    if "email_verification" in df.columns:
        hdbg.dassert_is_subset(
            df["email_verification"].unique(),
            ["", "valid", "accept_all", "unknown", "invalid"],
        )
        df["email_verification"] = df["email_verification"].replace(
            {
                "accept_all": "_accept_all_",
                "valid": "_valid_",
                "unknown": "_unknown_,",
                "invalid": "_invalid_",
            }
        )
    # Reorder columns.
    hdbg.dassert_no_duplicates(df.columns.to_list())
    df = df[contact_schema]
    return df


# #############################################################################


# error
# baseUrl                              https://www.linkedin.com/sales/lead/ACwAAATw5f...
# timestamp                            2023-11-09T20:34:20.691Z
# linkedinProfileUrl                   https://www.linkedin.com/in/adam-alfi-52891823/
# email                                aalfi@iconiqcapital.com
# linkedinProfile                      https://www.linkedin.com/in/adam-alfi-52891823/
# description                          Partner at ICONIQ / Growth Stage Technology In...
# headline                             Partner at ICONIQ
# location                             San Francisco, California, United States
# imgUrl
# firstName                            Adam
# lastName                             Alfi
# fullName                             Adam Alfi
# subscribers                          6445
# connectionDegree                     2nd
# vmid                                 ACoAAATw5fABJ5ZF-SwciO6SM_wl4NHzQsymiys
# userId                               82896368
# linkedinSalesNavigatorUrl            https://www.linkedin.com/sales/people/ACoAAATw...
# connectionsCount                     500
# connectionsUrl                       https://www.linkedin.com/search/results/people...
# mutualConnectionsUrl                 https://www.linkedin.com/search/results/people...
# mutualConnectionsText                Greg Kotchick is a mutual connection
# mailFromDropcontact                  aalfi@iconiqcapital.com
# company                              ICONIQ Capital
# companyUrl                           https://www.linkedin.com/company/6376200/
# jobTitle                             Partner
# jobDescription
# jobLocation
# jobDateRange                         Dec 2022 - Present
# jobDuration                          1 yr
# company2                             ICONIQ Capital
# companyUrl2                          https://www.linkedin.com/company/6376200/
# jobTitle2                            Principal, ICONIQ Growth
# jobLocation2                         San Francisco Bay Area
# jobDateRange2                        2021 - Dec 2022
# jobDuration2                         2 yrs
# school                               Georgetown University
# schoolUrl                            https://www.linkedin.com/company/4794/
# schoolDegree
# schoolDateRange
# school2                              ESCI-UPF
# schoolDegree2
# schoolDateRange2
# qualificationFromDropContact         nominative@pro
# civilityFromDropContact              Mr
# phoneNumberFromDropContact           +1 415-967-7763
# websiteFromDropContact               www.iconiqcapital.com
# twitter
# twitterProfileUrl
# website
# birthday
# companyWebsite                       http://www.iconiqcapital.com
# allSkills                            Spanish, Operations Management, Data Analysis,...
# skill1                               Spanish
# endorsement1
# skill2                               Operations Management
# endorsement2
# skill3                               Data Analysis
# endorsement3
# skill4                               Financial Analysis
# endorsement4
# skill5                               Logistics Management
# endorsement5
# skill6                               Manufacturing
# endorsement6
# profileId                            adam-alfi-52891823
# schoolUrl2                           https://www.linkedin.com/company/701578/
# jobDescription2                      ICONIQ Growth is a tech focused direct investm...
# schoolDescription
# schoolDescription2
# mail
# phoneNumber
# facebookUrl


def get_scraped_data_from_LinkedIn(
    normalize: bool = True, verbose: bool = False
) -> pd.DataFrame:
    """
    E.g., Search4.FinTech_VC_in_US.SalesNavigator.
    """
    # Read two tabs from a gsheet.
    url = (
        "https://docs.google.com/spreadsheets/d/1Lbnyvbb28Cv-y0k"
        "-nrG1NSES9F6rxesGoHZV2LOJ6wA/"
    )
    gsheet_names = ("ScrapeProfile", "ScrapeProfile2")
    dfs = []
    for gsheet_name in gsheet_names:
        df_tmp = get_cached_sheet_to_df(url, gsheet_name)
        if verbose:
            display(df_tmp.head(1))
        dfs.append(df_tmp)
    df = pd.concat(dfs).drop_duplicates()
    df = df.loc[:, df.columns.str.strip() != '']
    #
    if normalize:
        df["origin"] = "Search4.FinTech_VC_in_US"
        cols_map = {
            "timestamp": None,
            "origin": None,
            "linkedinProfileUrl": "linkedin_url",
            "firstName": "first_name",
            "lastName": "last_name",
            "email": None,
            "jobTitle": "job_title",
            "description": "job_title_description",
            "jobLocation": "city",
            "company": "company_name",
            # "companyWebsite": "company_domain",
        }
        df_out = normalize_contact_schema(df, cols_map)
    else:
        df_out = df
    return df_out


# #############################################################################


# profileUrl                  https://www.linkedin.com/sales/lead/ACwAAABGC0...
# fullName                    Zhenya Loginov
# firstName                   Zhenya
# lastName                    Loginov
# companyName                 Accel
# title                       Partner
# companyId                   17412
# companyUrl                  https://www.linkedin.com/sales/company/17412
# regularCompanyUrl           https://www.linkedin.com/company/17412
# summary
# titleDescription            I invest and help European and Israeli founder...
# industry                    Venture Capital and Private Equity Principals
# companyLocation             Palo Alto, California, United States
# location                    Palo Alto, California, United States
# durationInRole              10 months in role
# durationInCompany           10 months in company
# pastExperienceCompanyName
# pastExperienceCompanyUrl
# pastExperienceCompanyTitle
# pastExperienceDate
# pastExperienceDuration
# connectionDegree            Out of Network
# profileImageUrl             https://media.licdn.com/dms/image/C5103AQHLVkA...
# sharedConnectionsCount      0
# name                        Zhenya Loginov
# vmid                        ACwAAABGC0cBTaYzMWKXyySFD4zZyoPI59OadWk
# linkedInProfileUrl          https://www.linkedin.com/in/ACwAAABGC0cBTaYzMW...
# isPremium                   TRUE
# isOpenLink                  FALSE
# query                       https://www.linkedin.com/sales/search/people?q...
# timestamp                   2024-07-11T18:03:01.973Z
# defaultProfileUrl           https://linkedin.com/in/zhenyaloginov
# hunter_extracted_email      zloginov@accel.com
# hunter_verification         valid
# dropcontact_mail            NaN
# all_emails                  NaN


def _extract_and_validate_email(df: pd.DataFrame) -> str:
    """
    Extract and validate the email from a transposed DataFrame.
    """
    # List of possible email sources.
    email_fields = [
        "hunter_extracted_email",
        "dropcontact_mail",
        "all_emails",
    ]
    # Extract email values from the relevant fields.
    email_values = df[email_fields]
    num_values = [
        set([str(v) for v in row if (str(v) != "" and str(v) != "nan")])
        for _, row in email_values.iterrows()
    ]
    num_values_out = []
    for val in num_values:
        if len(val) > 1:
            raise ValueError("Multiple emails found: {%s}" % ", ".join(sorted(val)))
        elif len(val) == 1:
            val = list(val)[0]
        elif len(val) == 0:
            val = "nan"
        num_values_out.append(val)
    return num_values_out


def get_scraped_data_from_LinkedIn2(
    normalize: bool = True, verbose: bool = False
) -> pd.DataFrame:
    """
    E.g., Accel_search_export.gsheet.
    """
    # Accel_search_export.gsheet
    # Andreessen Horowitz (a16z)_search_export.gsheet
    # Benchmark Capital_search_export.gsheet
    # Bessemer Venture Partners_search_export.gsheet
    # General Catalyst_search_export.gsheet
    # Greylock Partners_search_export.gsheet
    # Index Ventures_search_export.gsheet
    # Insight Partners_search_export.gsheet
    # Kleiner Perkins_search_export.gsheet
    # Sequoia Capital_search_export.gsheet
    #
    # > find /Users/saggese/Library/CloudStorage/GoogleDrive-gp@kaizen-tech.io/Shared\ drives/Cold\ outreach/\!All_VC_lists -name "*search_export*" -print0 | sort -z  | xargs -0 -n 1 cat
    # {"":"WARNING! DO NOT EDIT THIS FILE! ANY CHANGES MADE WILL BE LOST!","doc_id":"1tgKVlDMVJJkPPyulTU1ibkBcGLKXeVjLTYN8jhQ9c3M","resource_key":"","email":"gp@kaizen-tech.io"}
    # https://docs.google.com/spreadsheets/d/1tgKVlDMVJJkPPyulTU1ibkBcGLKXeVjLTYN8jhQ9c3M/edit?gid=1151734371#gid=1151734371
    # {"":"WARNING! DO NOT EDIT THIS FILE! ANY CHANGES MADE WILL BE LOST!","doc_id":"1p7mKeeUuUS4a2OsHnTbWpe5Fscp8mvjocsWRL8ya6PA","resource_key":"","email":"gp@kaizen-tech.io"}
    urls = """
1tgKVlDMVJJkPPyulTU1ibkBcGLKXeVjLTYN8jhQ9c3M
1p7mKeeUuUS4a2OsHnTbWpe5Fscp8mvjocsWRL8ya6PA
1Iz9ypwENHwSU-meGknkrH_q7Gbg-CK6pArMQcxNvF3s
1y3bVUkC2qaZWFwkY9xvOcoUnqXEIDEC06mjUdiwXNNc
1RQMhAOpiu8BTyiNUl9O6DrmovEYAFqPPyBhiPD9uEZA
197W6s8K4tOzSdoT11rk3huGTxlttzXxpkWruHHzyeDQ
1xSYf8Hzg7vPmP_pSBe4NMkANX013FuTQR2SJgOr8AqU
1Gf6dVplfK-ufHoGdY3RchlcapQY2Ig5gopM2YMOTuz4
1EzsnB-a0cmiWpl2A9-McNrTR4D_jXJY9UB0byy8PuIA
1Ric5JLQOwkj9m4iwZtSo46VzOI0XDEMdeJZBEO4fPQ8
1rmImy9VByGf1cNKbYmUVh7ktojtRpXL4QLdvPLAB8C4
"""
    urls = urls.split()
    urls = [
        "https://docs.google.com/spreadsheets/d/" + url
        for url in urls
        if url != ""
    ]
    _LOG.debug("urls=\n%s", urls)
    dfs = []
    # urls = urls[:2]
    for url in tqdm(urls):
        # _LOG.debug("Reading %s", url)
        df = get_cached_sheet_to_df(url, "hunter_verification")
        if verbose:
            display(df.head(1))
        dfs.append(df)
        # time.sleep(20)
    # Concat.
    df2 = pd.concat(dfs, axis=0)
    if verbose:
        display(df2.head(2))
    #
    df2["email"] = _extract_and_validate_email(df2)
    # Convert to contact schema.
    if normalize:
        df2["origin"] = "VC_search_export"
        cols_map = {
            "timestamp": None,
            "origin": None,
            "linkedInProfileUrl": "linkedin_url",
            "firstName": "first_name",
            "lastName": "last_name",
            "email": None,
            "hunter_verification": "email_verification",
            "title": "job_title",
            "titleDescription": "job_title_description",
            "companyName": "company_name",
            "companyLocation": "city",
        }
        df_out = normalize_contact_schema(df2, cols_map)
    else:
        df_out = df2
    return df_out


# #############################################################################


# linkedinProfileUrl                   https://www.linkedin.com/in/robtoews/
# email
# firstName                            Rob
# lastName                             Toews
# company                              Radical Ventures
# jobTitle                             Partner
# Email                                rob@radical.vc
# Score                                97
# Verification status                  valid
# Position
# Twitter
# Linkedin
# Phone number
# Company                              Radical Ventures
# Source 1                             http://weeklyvoice.com/canadian-companies-prio...
# Source 2                             http://salt.org/speakers/rob-toews
# Source 3                             http://radical.vc/how-accurate-were-our-2023-a...
# Source 4                             http://radical.vc/neurips-2022-and-whats-next-...
# Source 5                             http://nationalposttoday.com/ai-skills-in-dema...


def get_scraped_data_from_LinkedIn3(
    normalize: bool = True, verbose: bool = False
) -> pd.DataFrame:
    """
    Search7.AI_VC_in_US.gsheet.
    """
    url = "https://docs.google.com/spreadsheets/d/12qmHUo6sTuFpLQcdw22EaA3xsJ9ERuiCJdhDyF-2elM"
    gsheet_name = "test-590999-valid"
    df = get_cached_sheet_to_df2(url, gsheet_name)
    # TODO(gp): Eisenbug. It's unclear why there is this column due to caching.
    if "email" in df.columns:
        del df["email"]
    if verbose:
        display(df.head(1))
    if normalize:
        df["origin"] = "Search7.AI_VC_in_US"
        cols_map = {
            "origin": None,
            "linkedinProfileUrl": "linkedin_url",
            "firstName": "first_name",
            "lastName": "last_name",
            "Email": "email",
            "Verification status": "email_verification",
            "Position": "job_title_description",
            "company": "company_name",
        }
        df_out = normalize_contact_schema(df, cols_map)
    else:
        df_out = df
    return df_out


# #############################################################################


# email_first           aagarwal@insightpartners.com
# first_name                            Anika
# last_name                           Agarwal
# job_title                 Managing Director
# company_name               Insight Partners
# company_domain          insightpartners.com
# city            New York, New York, United States
# linkedin_id                             NaN
# created_date                            NaN
# list_name                               NaN
# YAMM                                    NaN
# email_second                            NaN
# phone                                   NaN
# company_phone                           NaN
# middle_name                             NaN
# url                                     NaN
# company_id                              NaN
# hunter_verification              accept_all


def get_scraped_data_from_LinkedIn4(
    normalize: bool = True, verbose: bool = False
) -> pd.DataFrame:
    """
    VC Tier 1 - Partners
    """
    url = "https://docs.google.com/spreadsheets/d/1WU_u-4gKDb5NE-u1xwMrkFWDT77PoNQuku0pcj3fbNY/edit?gid=1063998981#gid=1063998981"
    #
    dfs = []
    for gsheet_name in ("Sheet1", "Sheet2", "Sheet3"):
        df_tmp = get_cached_sheet_to_df(url, gsheet_name)
        if verbose:
            display(df_tmp.head(1))
        dfs.append(df_tmp)
    df = pd.concat(dfs)
    #
    df_tmp = get_cached_sheet_to_df(url, "validity_merged_df")
    df = df.merge(
        df_tmp[["email_first", "hunter_verification"]],
        how="outer",
        on="email_first",
    )
    #
    if normalize:
        df["origin"] = "VC Tier 1"
        cols_map = {
            "origin": None,
            "url": "linkedin_url",
            "first_name": None,
            "last_name": None,
            "email_first": "email",
            "hunter_verification": "email_verification",
            "job_title": None,
            "company_name": None,
            "company_domain": None,
            "city": None,
        }
        df_out = normalize_contact_schema(df, cols_map)
    else:
        df_out = df
    return df_out


# #############################################################################


# email_first               rodriguez@foundersfund.com
# First name                                 Rodriguez
# last_name                                       Keig
# job_title                                    Founder
# company_name                           Founders Fund
# company_domain                      foundersfund.com
# city               New York, New York, United States
# linkedin_id                               1107202338
# created_date                              2024-05-13
# list_name                             VC List Tier 2
# docsend_link  https://docsend.com/view/v9itej52tumaupih?emai...
# link                               Kaizen pitch deck
# Merge status                                 BOUNCED
# email_verification                           invalid


def get_scraped_data_from_LinkedIn5(
    normalize: bool = True, verbose: bool = False
) -> pd.DataFrame:
    """
    VC_Tier_2_Partners.
    """
    url = "https://docs.google.com/spreadsheets/d/17gxl8o_lS9zOsuJMmX1CSZJfZUBx0UZ66eaAlYutfaA/edit?gid=1525085692#gid=1525085692"
    #
    dfs = []
    target_sheet_names = "VC-20240525-1 VC-20240520-4 VC-20240520-3 VC-20240520-2 VC-20240520".split()
    for gsheet_name in target_sheet_names:
        df_tmp = get_cached_sheet_to_df(url, gsheet_name)
        if verbose:
            display(df_tmp.head(1))
        dfs.append(df_tmp)
    df = pd.concat(dfs)
    #
    df["email_verification"] = np.where(
        df["Merge status"] != "BOUNCED", "valid", "invalid"
    )
    #
    if normalize:
        df["origin"] = "VC Tier 2"
        cols_map = {
            "origin": None,
            "First name": "first_name",
            "last_name": "last_name",
            "email_first": "email",
            "email_verification": None,
            "job_title": None,
            "company_name": None,
            "company_domain": None,
            "city": None,
        }
        df_out = normalize_contact_schema(df, cols_map)
    else:
        df_out = df
    return df_out


# #############################################################################


# Name                                             Michael Gilroy
# First name                                              Michael
# Title         Co-COO of Growth, Co-Head of Fintech, General ...
# Email                                        mgilroy@coatue.com
# Connect                                         Connect20240530


def _get_last_name(x: str) -> str:
    x2 = x.split()
    if len(x2) > 1:
        return " ".join(x2[1:])
    else:
        return x


def get_scraped_data_from_VCSheet(
    normalize: bool = True, verbose: bool = False
) -> pd.DataFrame:
    """
    VCSheet_Query1.
    """
    url = (
        "https://docs.google.com/spreadsheets/d"
        "/1U8jJYZbC1oyZpsSWhCCe6SDpAH8e6R2yRDeFauHVcj0/edit?gid=1769984900"
        "#gid=1769984900"
    )
    #
    gsheet_name = "Sheet1"
    df = get_cached_sheet_to_df(url, gsheet_name)
    if verbose:
        display(df.head(1))
    #
    df["last_name"] = df["Name"].apply(lambda x: _get_last_name(x))
    df["company_name"] = df["Title"].apply(lambda x: x.split("@")[1])
    #
    if normalize:
        df["origin"] = "VCSheet_Query1"
        cols_map = {
            "origin": None,
            "LinkedIn": "linkedin_url",
            "First name": "first_name",
            "last_name": "last_name",
            "Email": "email",
            "Title": "job_title",
            "company_name": None,
        }
        df_out = normalize_contact_schema(df, cols_map)
    else:
        df_out = df
    return df_out


# #############################################################################


# Investor                             Angels FTW
# Domain                               https://www.joinodin.com/
# Main Country                         Worldwide
# Investor Category                    Angel Investment Group,Angel Investor,Venture ...
# Overview                             Keep your cap table clean with Odin. Learn mor...
# Main City
# Industries                           Administrative Services, Agriculture and Farm...
# Stages                               Seed,Convertible Note,Series A,Pre-Seed
# Fund Restrictions
# Fund Restriction Notes
# Contact 1 First Name
# Contact 1 Last Name
# Contact 1 Email
# Contact 1 Linkedin
# Contact 1 Title
# Contact 2 First Name
# Contact 2 Last Name
# Contact 2 Email
# Contact 2 Linkedin
# Contact 2 Title
# Portfolio
# Categories
# Second Country
# Second City
# Approved                             true
# Created                              2022-11-28T16:51:37.000Z
# origin                               Euro-VC-LinkedIn


def get_scraped_data_from_EuroVC(
    normalize: bool = True, verbose: bool = False
) -> pd.DataFrame:
    """
    Euro-VCs.
    """
    url = "https://docs.google.com/spreadsheets/d/1r3_drVggRB61KvNPxlf58sEwNoUvU_aquLwGLDyUSKI"
    #
    gsheet_name = "Sheet1"
    df = get_cached_sheet_to_df(url, gsheet_name)
    if verbose:
        display(df.head(1))
    #
    print(df.shape)
    for col in df.columns:
        df[col] = df[col].str.replace(r"[^\x00-\x7F]+", "", regex=True)
    if verbose:
        display(df.head(1))
    df["stages"] = df["Stages"] + "/" + df["Investor Category"]
    df["restrictions"] = (
        df["Fund Restrictions"] + "." + df["Fund Restriction Notes"]
    )
    # Reshape the DataFrame by pivoting Contact 1 and Contact 2 into rows.
    cols = [x for x in df.columns if not x.startswith("Contact ")]
    print(cols)
    df_contact1 = df[
        cols
        + [
            "Contact 1 First Name",
            "Contact 1 Last Name",
            "Contact 1 Email",
            "Contact 1 Linkedin",
            "Contact 1 Title",
        ]
    ].rename(columns=lambda x: x.replace("Contact 1 ", ""))
    df_contact2 = df[
        cols
        + [
            "Contact 2 First Name",
            "Contact 2 Last Name",
            "Contact 2 Email",
            "Contact 2 Linkedin",
            "Contact 2 Title",
        ]
    ].rename(columns=lambda x: x.replace("Contact 2 ", ""))
    # Concatenate the two DataFrames to stack them as rows
    df = pd.concat([df_contact1, df_contact2], ignore_index=True)
    valid_mask = df["First Name"] != ""
    print(
    "Removed %s rows with empty first name"
    % hprint.perc((~valid_mask).sum(), df.shape[0])
    )
    df = df[valid_mask]
    if verbose:
        display(df.head(1))
    #
    if normalize:
        df["origin"] = "Euro-VC-LinkedIn"
        cols_map = {
            "origin": None,
            "Linkedin": "linkedin_url",
            "First Name": "first_name",
            "Last Name": "last_name",
            "Email": "email",
            "Title": "job_title",
            "Domain": "company_name",
            "stages": None,
            "restrictions": "restrictions",
            "Created": "timestamp",
            "Main City": "city",
            "Overview": "notes",
        }
        df_out = normalize_contact_schema(df, cols_map)
    else:
        df_out = df
    return df_out


# #############################################################################


# Person                               Vasudev Bailey
# First name                           Vasudev
# Email                                vb@av.co
# Urls                                 https://www.linkedin.com/in/baileyv
# Companies                            Artis Ventures (AV)
# Portfolio companies                  YouTube, Lemonaid Health, Activ Surgical, Tast...
# Fund type                            Venture Fund
# Fund stage                           Seed;Pre-Seed;Series A;Series B;Series C;Series D
# Fund focus                           Health;Entertainment & Media;AI & Machine Lear...
# Location                             San Francisco;California
# Twitter Link                         http://twitter.com/artisventures
# LinkedIn Link                        http://www.linkedin.com/company/artis-ventures
# Facebook Link                        http://www.facebook.com/pages/ARTIS-Ventures/3...
# Number of Investments                101
# Number of Exits                      27
# Fund Description                     ARTIS Ventures is a financial services firm th...
# Founding Year                        2001
# Description
# origin                               Folkapp


def _remove_duplicates(input_string: str) -> str:
    # Split the string into a list of words.
    words = input_string.split()
    # Use a set to track words we've seen.
    seen = set()
    result = []
    # Iterate over each word in the list.
    for word in words:
        # If the word hasn't been seen, add it to the result.
        if word.lower() not in seen:
            result.append(word)
            # Add the lowercase version to handle case-insensitive duplicates.
            seen.add(word.lower())
    return " ".join(result)


def get_scraped_data_from_FolkApp(
    normalize: bool = True, verbose: bool = False
) -> pd.DataFrame:
    """
    Folkapp.
    """
    # Read data.
    url = "https://docs.google.com/spreadsheets/d/1j6_mI5r05-P6smXMGOq3f0bpmyc7p2W0n7mY8gGbpY0/edit?gid=0#gid=0"
    gsheet_name = "Sheet1"
    df = get_cached_sheet_to_df(url, gsheet_name)
    if verbose:
        display(df.head(1))
    #
    if normalize:
        df["origin"] = "Folkapp"
        df["Person_modified"] = df["Person"].apply(_remove_duplicates)
        df["is_person_modified"] = df["Person"] != df["Person_modified"]

        def _extract_last_name(x):
            vals = x.split()
            if len(vals) > 1:
                return vals[-1]
            else:
                return ""

        df["last_name"] = [_extract_last_name(x) for x in df["Person"]]
        #
        cols_map = {
            "origin": None,
            "Urls": "linkedin_url",
            "First name": "first_name",
            "last_name": "last_name",
            "Email": "email",
            "Description": "job_title",
            "Companies": "company_name",
            "Fund type": "category",
            "Fund stage": "stages",
            "Fund focus": "industry",
            "Location": "city",
        }
        df_out = normalize_contact_schema(df, cols_map)
        # Some LinkedIn urls are websites and not LinkedIn urls.
        df_out["is_linkedin"] = [
            "linkedin.com" in x for x in df_out["linkedin_url"]
        ]
        srs_tmp = df_out["linkedin_url"].copy()
        df_out["linkedin_url"] = np.where(df_out["is_linkedin"], srs_tmp, "")
        df_out["company_domain"] = np.where(df_out["is_linkedin"], "", srs_tmp)
        del df_out["is_linkedin"]
    else:
        df_out = df
    return df_out


# #############################################################################

# profileUrl                    https://www.linkedin.com/in/grahamcpeck/
# firstName                                                    Graham C.
# lastName                                                          Peck
# fullName                                                Graham C. Peck
# title                Co-Founder @ DealSend & Attaq Vector | Partner...
# connectionSince                               2024-12-26T21:09:08.000Z
# profileImageUrl      https://media.licdn.com/dms/image/v2/C5603AQHT...
# timestamp                                     2024-12-29T01:14:30.420Z
# connectedProfileUrl                  https://linkedin.com/in/gpsaggese
# connectedUsername                               Giacinto Paolo Saggese


def get_scraped_data_from_Phantom_LIn_Connections_Exports(
    normalize: bool, verbose: bool = False
) -> pd.DataFrame:
    """
    Load data from PhantomBuster "LinkedIn Connections Export".
    """
    # Read data.
    url = "https://cache1.phantombooster.com/jqWbRHyznhM/XagiLTpuGYZGRsi4q9Exrg/result.csv"
    df = pd.read_csv(url)
    if verbose:
        display(df.head(1))
    #
    if normalize:
        df["origin"] = "GP_LIN_Connections"
        cols_map = {
            "timestamp": None,
            "origin": None,
            "profileUrl": "linkedin_url",
            "firstName": "first_name",
            "lastName": "last_name",
            "title": "job_title",
        }
        df_out = normalize_contact_schema(df, cols_map)
    else:
        df_out = df
    return df_out


# #############################################################################


# Company       21st Century Digital Industries Fund
# Full Name                       Richard B. Steward
# First Name                              Richard B.
# Last Name                                  Steward
# Address 1                    960 Pines Lake Dr. W.
# Address2
# City                                         Wayne
# State                                           NJ
# Zip                                          07470
# Country                                         US
# Phone                                 973-839-8776
# Fax                                   973-839-2185
# Email                           rstew10446@aol.com

def get_data_from_hedge_fund_list(
    normalize: bool = True, verbose: bool = False
) -> pd.DataFrame:
    """
    Hedge fund list.
    """
    # Read data.
    url = "https://docs.google.com/spreadsheets/d/10h8NtGDx4GQL8JWWJHEkD1GS685nYIZOIJMXiiz7pqA"
    gsheet_name = "Hedge Fund Contacts"
    df = get_cached_sheet_to_df(url, gsheet_name)
    if verbose:
        display(df.head(1))
    #
    print('Input data...',df[:1].to_csv())
    if normalize:
        df["origin"] = "hedge_fund_list"
        print('Input data...',df[:1].to_csv())
        df["City"] = df["City"] + ", " + df["State"] + ", " + df["Country"]
        print('Input data...',df[:1].to_csv())
        df["category"] = "hedge_fund"
        print('Input data...',df[:1].to_csv())
        #
        cols_map = {
            "origin": None,
            "First Name": "first_name",
            "Last Name": "last_name",
            "Email": "email",
            "Company": "company_name",
            "category": None,
            "City": "city",
        }
        df_out = normalize_contact_schema(df, cols_map)
        print('Input data...',df_out[:1].to_csv())
    else:
        df_out = df.copy()
    return df_out


# #############################################################################

# companyIndustry                                                            Design
# companyName                                                                   FYC Labs
# firstName                                                                       Justin
# lastName                                                                       Fortier
# linkedinCompanyUrl                               https://linkedin.com/company/fyc-labs
# linkedinCompanySlug                                                           fyc-labs
# linkedinFollowersCount                                                            3063
# linkedinHeadline                                          Founder + CEO/CTO @ FYC Labs
# linkedinIsHiringBadge                                                            FALSE
# linkedinIsOpenToWorkBadge                                                        FALSE
# linkedinJobDateRange                                                Oct 2012 - Present
# linkedinJobLocation                                          California, United States
# linkedinJobTitle                     Chief Executive Officer / Chief Technical Officer
# linkedinPreviousCompanySlug                                               opengrantsio
# linkedinPreviousJobDateRange                                        Nov 2022 - Present
# linkedinPreviousJobDescription
# linkedinPreviousJobTitle                                      Chief Technology Officer
# linkedinPreviousSchoolDegree                                           Master's degree
# linkedinProfileId                                                            244286678
# linkedinProfileSlug                                                     justinffortier
# linkedinProfileUrl                              https://linkedin.com/in/justinffortier
# linkedinProfileUrn                             ACoAAA6PhNYBqKRF_PWQKs6zWnxk3-WzKXiXN6k
# linkedinSchoolUrl                           https://linkedin.com/school/ucsantabarbara
# linkedinSchoolCompanySlug                                               ucsantabarbara
# linkedinSchoolDegree                                           Bachelor of Arts (B.A.)
# linkedinSchoolName                                                    UC Santa Barbara
# linkedinSkillsLabel                  Marketing, Leadership, Competitive Analysis, M...
# location                                             Folsom, California, United States
# previousCompanyName                                                         OpenGrants
# connectionDegree                                                                   1st
# refreshedAt                                                   2024-12-31T02:08:03.997Z
# mutualConnectionsUrl                 https://www.linkedin.com/search/results/people...
# connectionsUrl                       https://www.linkedin.com/search/results/people...
# linkedinConnectionsCount                                                           500
# profileUrl                                 https://www.linkedin.com/in/justinffortier/
# linkedinDescription                  I love creating and working with amazing compa...
# linkedinJobDescription               FYC is a web development and graphic design ag...
# linkedinPreviousJobLocation                          Folsom, California, United States
# linkedinPreviousSchoolUrl            https://linkedin.com/school/san-diego-state-un...
# linkedinPreviousSchoolCompanySlug                           san-diego-state-university
# linkedinPreviousSchoolDescription    The focus of my Masters Degree was on persuasi...
# linkedinPreviousSchoolName                                  San Diego State University
# linkedinSchoolDescription            UCSB Club Hockey, Law and Society Study Groups...
# linkedinPreviousSchoolDateRange
# linkedinSchoolDateRange


def get_data_from_GP_LIn_connections(
    normalize: bool = True, verbose: bool = False
) -> pd.DataFrame:
    """
    GP LinkedIn connections.
    """
    # Read data.
    url = "https://docs.google.com/spreadsheets/d/19ziUmqbPaUO73cqlJB1F9y-j1Oq98nMzo6wTmzyVnwg"
    gsheet_name = "Sheet1"
    df = get_cached_sheet_to_df(url, gsheet_name)
    if verbose:
        display(df.head(1))
    #
    if normalize:
        df["origin"] = "GP_LIn_connections"
        df["job_title_description"] = (
            df["linkedinHeadline"]
            + "; "
            + df["linkedinDescription"]
            + "; "
            + df["linkedinJobDescription"]
        )
        #
        cols_map = {
            "origin": None,
            # When it was scraped.
            "refreshedAt": "timestamp",
            "firstName": "first_name",
            "lastName": "last_name",
            # Email.
            # "email": "",
            # "email_verification": "",
            "linkedinProfileUrl": "linkedin_url",
            "linkedinJobTitle": "job_title",
            "job_title_description": None,
            "companyName": "company_name",
            # "company_domain": "",
            "location": "city",
            # Seed,Convertible Note,Series A,Pre-Seed
            # "stages": "",
            # "restrictions": "",
            # Angel, VC, PE, Family Office, Corporate VC, Accelerator, Incubator
            "companyIndustry": "category",
            # "notes": "",
        }
        df_out = normalize_contact_schema(df, cols_map)
    else: 
        df_out = df
    return df_out


# #############################################################################

# Name                                        Priyaluk (Neuy)
# Email                                       priyaluk_wij@tk-partners.net
# LinkedIn                                    https://www.linkedin.com
# Check sizes                                 100K USD min/ 2.5M USD max
# Open for more deals from other investors                        TRUE
# Ready to share my deal flow with others                         TRUE
# Can advise startups                                             TRUE
# Pre-seed                                                       FALSE
# Seed                                                            TRUE
# Series A                                                        TRUE
# Series B                                                       FALSE
# Series C+                                                      FALSE
# Other options
# Angel                                                           TRUE
# Angel Syndicate Lead                                           FALSE
# VC Fund                                                         TRUE
# Accelerator                                                     TRUE
# Family Office                                                   TRUE
# Private Equity Fund                                            FALSE
# Venture Studio                                                 FALSE
# Fund of Funds                                                  FALSE
# CVC                                                            FALSE
# Limited Partner                                                FALSE
# Other types
# Globally – everywhere                                          FALSE
# US                                                              TRUE
# Canada                                                         FALSE
# UK                                                              TRUE
# Europe                                                         FALSE
# Israel                                                         FALSE
# Latin America                                                  FALSE
# Middle East                                                    FALSE
# Africa                                                         FALSE
# Asia Pacific                                                    TRUE
# Other regions
# Agnostic – all industries                                      FALSE
# AI                                                             FALSE
# B2B                                                            FALSE
# B2C                                                            FALSE
# SaaS                                                           FALSE
# Fintech                                                        FALSE
# Healthcare                                                      TRUE
# Biotech                                                        FALSE
# Energy                                                          TRUE
# ClimateTech                                                    FALSE
# E-com & Retail                                                 FALSE
# Future of Work / HRtech                                        FALSE
# Mobility & Transportation                                      FALSE
# Marketing / Adtech                                             FALSE
# PropTech                                                        TRUE
# AgriTech                                                        TRUE
# SpaceTech                                                      FALSE
# Cybersecurity                                                  FALSE
# Blockchain / Crypto                                            FALSE
# Education                                                      FALSE
# Other sectors


def get_data_from_super_networking_gsheet(
    normalize: bool = True, verbose: bool = False
) -> pd.DataFrame:
    url = "https://docs.google.com/spreadsheets/d/1kxB15NcHcuhEVtD982qnvbx276J7fmDKvJx63rRpD0E/edit?gid=381241246#gid=381241246"
    df = get_cached_sheet_to_df(url, "List of investors")
    if verbose:
        display(df.head(1))
    # Add column.
    columns = df.iloc[0, :].tolist()
    columns = [v.split("\n")[0] if "\n" in v else v for v in columns]
    columns = [v.strip() for v in columns]
    df.columns = columns
    # Remove the first row.
    df = df.iloc[1:, :]
    if normalize:
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
        # Reindex.
        df.index = range(0, len(df))
        # Split names.
        df = split_first_last_name(df, "Name")
        # Add
        df["origin"] = "super_networking"
        cols_map = {
            "origin": None,
            "LinkedIn": "linkedin_url",
            "first_name": None,
            "last_name": None,
            "Email": "email",
        }
        df = _rename_columns_to_contact_schema(df, cols_map)
        # df_out = normalize_contact_schema(df, cols_map)
    if verbose:
        display(df.head(1))
    return df


def filter_super_networking_gsheet(df: pd.DataFrame) -> pd.DataFrame:
    # ['Email', 'LinkedIn',
    #
    # 'Check sizes',
    # 'Open for more deals from other investors', 'Ready to share my deal flow with others', 'Can advise startups',
    # 'Pre-seed', 'Seed', 'Series A', 'Series B', 'Series C+', 'Other options',
    #
    # 'Angel', 'Angel Syndicate Lead', 'VC Fund', 'Accelerator', 'Family Office',
    # 'Private Equity Fund', 'Venture Studio', 'Fund of Funds', 'CVC', 'Limited Partner', 'Other types',
    #
    # 'Globally – everywhere', 'US', 'Canada', 'UK',
    # 'Europe', 'Israel', 'Latin America', 'Middle East', 'Africa', 'Asia Pacific',
    # 'Other regions',
    #
    # 'Agnostic – all industries', 'AI', 'B2B', 'B2C', 'SaaS',
    # 'Fintech', 'Healthcare', 'Biotech', 'Energy', 'ClimateTech', 'E-com & Retail',
    # 'Future of Work / HRtech', 'Mobility & Transportation', 'Marketing / Adtech',
    # 'PropTech', 'AgriTech', 'SpaceTech', 'Cybersecurity', 'Blockchain / Crypto',
    # 'Education', 'Other sectors']
    col_names = [
        "Name",
        "first_name",
        "last_name",
        "email",
        "linkedin_url",
        "Check sizes",
        "Seed",
        "Series A",
        "Globally – everywhere",
        "US",
    ]
    #
    mask1 = df["Seed"] | df["Series A"]
    print("mask1=", mask1.sum())
    #
    mask2 = df["Globally – everywhere"] | df["US"]
    print("mask2=", mask2.sum())
    #
    mask3 = None
    col_names_tmp = [
        "Agnostic – all industries",
        "AI",
        "B2B",
        "SaaS",
        "Fintech",
        "Energy",
        "ClimateTech",
        "E-com & Retail",
        "Future of Work / HRtech",
        "Mobility & Transportation",
        "Marketing / Adtech",
        "PropTech",
        "AgriTech",
    ]
    col_names.extend(col_names_tmp)
    for col_name in col_names_tmp:
        mask_tmp = df[col_name]
        # print(col_name, mask_tmp.sum())
        if mask3 is None:
            mask3 = mask_tmp
        else:
            mask3 |= mask_tmp
    print("mask3=", mask3.sum())
    #
    mask = mask1 & mask2 & mask3
    print("mask=", mask.sum())
    #
    df2 = df[col_names][mask]
    return df2


# #############################################################################
# Process contact df.
# #############################################################################


def add_hash(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    keys = df["first_name"] + df["last_name"] + df["email"]
    df["hash"] = keys.apply(lambda x: hashlib.md5(x.encode()).hexdigest())
    df.set_index("hash", drop=True, inplace=True)
    df.sort_index(inplace=True)
    return df


def clean_up_contact_df(
    df: pd.DataFrame, *, allow_no_emails: bool = False, debug: str = ""
) -> pd.DataFrame:
    """
    Clean up the contact DataFrame by performing various operations.

    :param df: The DataFrame to clean up.
    :param allow_no_emails: Whether to allow rows with no emails.
    :param debug: The debug phase to stop at.
    :returns: The cleaned-up DataFrame.
    """
    result = {}
    # - Convert everything into strings.
    df = df.astype(str)
    # - Remove empty spaces.
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].str.strip()
    # - Remove duplicated rows unless they have non-null values.
    phase = "duplicated_emails"
    num_before = df.shape[0]
    valid_mask = df.apply(
        lambda row: row["email"] == "", axis=1
    ) | ~df.duplicated(subset=["email"])
    num_after = valid_mask.sum()
    result[phase] = hprint.perc(num_before - num_after, num_before)
    if debug == phase:
        display(df[~valid_mask])
        assert 0
    df = df[valid_mask]
    if not allow_no_emails:
        hdbg.dassert_ne((df["email"] != "").sum(), 0)
    # - Ensure that there are no duplicated emails.
    df_tmp = df[lambda row: row["email"] != ""]
    hdbg.dassert(not df_tmp.duplicated(subset=["email"]).any())
    # - Remove invalid emails.
    phase = "remove_invalid_emails"
    num_before = df.shape[0]
    valid_mask = (df["email"] == "") | df["email"].apply(is_valid_email)
    num_after = valid_mask.sum()
    result[phase] = hprint.perc(num_before - num_after, num_before)
    if debug == phase:
        display(df[~valid_mask])
        assert 0
    df = df[valid_mask]
    # - Remove names with Chinese characters.
    phase = "remove_chinese_names"
    num_before = df.shape[0]

    def contains_chinese(text: str) -> bool:
        chinese_characters = re.compile(r"[\u4E00-\u9FFF]")
        return bool(chinese_characters.search(text))

    valid_mask = df["first_name"].apply(lambda value: not contains_chinese(value))
    num_after = valid_mask.sum()
    result[phase] = hprint.perc(num_before - num_after, num_before)
    if debug == phase:
        display(df[~valid_mask])
        assert 0
    df = df[valid_mask]
    # - Remove rows with empty first name.
    phase = "remove_empty_first_names"
    num_before = df.shape[0]
    valid_mask = df["first_name"] != ""
    num_after = valid_mask.sum()
    result[phase] = hprint.perc(num_before - num_after, num_before)
    if debug == phase:
        display(df[~valid_mask])
        assert 0
    df = df[valid_mask]
    # - Move urls from the `company_domain` column.
    phase = "clean_company_names"
    num_before = df.shape[0]
    is_url = df["company_name"].apply(is_valid_url)
    result[phase] = hprint.perc(is_url.sum(), num_before)
    if debug == phase:
        display(df[is_url])
        assert 0
    srs = df["company_name"].copy()
    df["company_domain"] = np.where(is_url, srs, df["company_domain"])
    df["company_name"] = np.where(is_url, "", srs)
    # - Remove `nan` from the LinkedIn column.
    phase = "clean_linkedin_nans"
    is_nan = df["linkedin_url"].apply(lambda value: value == "nan")
    result[phase] = hprint.perc(is_nan.sum(), num_before)
    if debug == phase:
        display(df[is_nan])
        assert 0
    df["linkedin_url"] = np.where(is_nan, "", df["linkedin_url"])
    # - Move emails from the LinkedIn column to the `email` column.
    phase = "clean_linkedin_emails"
    is_email = df["linkedin_url"].apply(lambda value: is_valid_email(value))
    result[phase] = hprint.perc(is_email.sum(), num_before)
    if debug == phase:
        display(df[is_email])
        assert 0
    srs = df["linkedin_url"].copy()
    df["email"] = np.where(is_email, srs, df["email"])
    df["linkedin_url"] = np.where(is_email, "", srs)
    # - Move websites from the LinkedIn column to the `company_domain` column.
    phase = "clean_linkedin_websites"
    is_website = df["linkedin_url"].apply(
        lambda value: not is_linkedin_url(value) and is_valid_url(value)
    )
    result[phase] = hprint.perc(is_website.sum(), num_before)
    if debug == phase:
        display(df[is_website])
        assert 0
    srs = df["linkedin_url"].copy()
    df["company_domain"] = np.where(is_website, srs, df["company_domain"])
    df["linkedin_url"] = np.where(is_website, "", srs)
    # - Remove rows with empty emails.
    phase = "clean_emails"
    num_before = df.shape[0]
    invalid_mask = df["email"].str.contains("mailto:")
    result[phase] = hprint.perc(invalid_mask.sum(), num_before)
    if debug == phase:
        display(df[invalid_mask])
        assert 0
    df.loc[invalid_mask, "email"] = df.loc[invalid_mask, "email"].str.replace(
        "mailto:", ""
    )
    # Add hash.
    df = add_hash(df)
    # Sort.
    # df.sort_values(by=["first_name", "last_name"], inplace=True)
    # df.sort_values(by=["hash"], inplace=True)
    #
    result_df = pd.Series(result).to_frame()
    # result_df = result_df.T
    display(result_df)
    return df


# TODO(gp): Move to helpers somewhere.
email_regex = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def is_valid_email(email: str) -> bool:
    return bool(re.match(email_regex, email))


url_regex = re.compile(
    r"^(https?|ftp):\/\/([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,6}(\:[0-9]{1,5})?(\/[^\s]*)?$"
)


def is_valid_url(url: str) -> bool:
    return bool(re.match(url_regex, url))


def is_linkedin_url(url: str) -> bool:
    return "linkedin.com" in url


def assign_nans(df: pd.DataFrame, column: str, value: Any) -> pd.DataFrame:
    """
    Assign `value` to the `column` of `df` where the value is "nan".

    :param df: The DataFrame to modify.
    :param column: The column in which to replace "nan" values.
    :param value: The value to assign to "nan" entries.
    """
    df[column] = df[column].astype(str)
    mask = df[column] == "nan"
    # Assign the new value or keep the original value.
    df[column] = np.where(mask, value, df[column])
    # There should be no more nans.
    mask = df[column] == "nan"
    hdbg.dassert_eq(mask.sum(), 0)
    #
    return df


def sanity_check_contact_df(
    df: pd.DataFrame,
    *,
    verbose: bool = False,
    debug: str = "",
) -> None:
    """
    Perform a sanity check on the contact DataFrame.

    If one of the checks fails, print the invalid rows and raise an
    exception.

    :param df: The DataFrame to check.
    :param verbose: Whether to print detailed information.
    :param debug: The debug phase to stop at.
    """
    # Remove the columns that start with `campaign_`.
    col_names = [
        col_name
        for col_name in df.columns
        if not col_name.startswith("campaign_")
    ]
    df = df[col_names]
    if set(df.columns) != set(contact_schema):
        diff1 = set(df.columns.tolist()) - set(contact_schema)
        diff2 = set(contact_schema) - set(df.columns.tolist())
        _LOG.warning(
            "All columns must be in Contact schema: diff1=%s diff2=%s"
            % (diff1, diff2)
        )
    # 1) `linkedin_url` column has empty values or valid LinkedIn URLs.
    phase = "linkedin_url"
    valid_mask = df["linkedin_url"].apply(
        lambda value: value == "" or is_linkedin_url(value)
    )
    if debug == phase and not valid_mask.all():
        print("Invalid %s linkedin_url values" % (~valid_mask).sum())
        if verbose:
            display(df[~valid_mask])
        assert 0
    # 2) `email` column has empty values or valid emails.
    phase = "email"
    valid_mask = df["email"].apply(
        lambda value: value == "" or is_valid_email(value)
    )
    if debug == phase and not valid_mask.all():
        print("Invalid %s email values" % (~valid_mask).sum())
        if verbose:
            display(df[~valid_mask])
        assert 0
    # 3) `email_verification` column.
    phase = "email_verification"
    valid_mask = df["email_verification"].isin(
        ["valid", "accept_all", "invalid", "unknown", ""]
    )
    if debug == phase and not valid_mask.all():
        print("Invalid %s email_verification values" % (~valid_mask).sum())
        if verbose:
            display(df[~valid_mask])
        assert 0
    # Email and company domain if they are not empty, should match.
    cols = ["email", "company_domain"]
    df_tmp = df[cols].copy()
    df_tmp["email_domain"] = df_tmp["email"].str.extract(".*@(.*)")
    df_tmp["email_domain"] = df_tmp["email_domain"].str.lower()
    # Remove suffix.
    # df_tmp["email_domain"] = df_tmp["email_domain"].str.extract(r"^(?:https?:\/\/)?(?:www\.)?([^\/]+)\.[^\.]+$")
    assign_nans(df_tmp, "email_domain", "")
    df_tmp["actual_domain"] = df_tmp["company_domain"].str.extract(
        r"^(?:https?:\/\/)?(?:www\.)?(?:[^\/]+\.)?([^\/]+\.[^\/]+)"
    )
    df_tmp["actual_domain"] = df_tmp["actual_domain"].str.lower()
    # df_tmp["actual_domain"] = df_tmp["actual_domain"].str.extract(r"^([^\/]+)\.[^\.]+$")
    assign_nans(df_tmp, "actual_domain", "")
    df_tmp["both_specified"] = (df_tmp["email_domain"] != "") & (
        df_tmp["actual_domain"] != ""
    )
    df_tmp["is_equal"] = df_tmp["email_domain"] == df_tmp["actual_domain"]
    df_tmp["check"] = np.where(
        df_tmp["both_specified"], 2 * df_tmp["is_equal"] - 1, 0
    )
    df_tmp["check"] = df_tmp["check"].replace(
        {-1: "mismatch", 0: "nan", 1: "match"}
    )
    # TODO(gp): Lots of mismatches are like:
    # email_domain  actual_domain
    # 12    pointninecap.com    pointnine.com
    # 25    magiclab.co bumble.com
    # 85    eventures.vc    headline.com
    # 92    mobeus.co.uk    co.uk
    # 94    transi.st   efundsforschools.com
    # 113   gmail.com   alliancetechventures.com
    # 144   holtzbrinck.com holtzbrinck-digital.com
    # 170   metaprop.org    metaprop.vc
    # 185   benchmarkcapital.co.za  co.za
    # 199   nyaamerica.org  basisset.com
    # df_tmp.head()
    print((df_tmp["check"].value_counts() / df_tmp.shape[0]).to_dict())


def print_contact_df_stats(
    df: pd.DataFrame,
    *,
    debug: str = "",
    email_col: str = "email",
    email_verification_col: str = "email_verification",
) -> None:
    """
    Print statistics for a Contact df, without applying any modification.

    :param df: The DataFrame to analyze.
    :param debug: The debug phase to stop at.
    :param email_col: The name of the email column.
    :param email_verification_col: The name of the email verification
        column.
    """
    display(df.head(1))
    #
    result_df = {}
    result_df["num_rows"] = df.shape[0]
    # 1) Check if there are duplicates for sure.
    phase = "count_no_dups"
    df_no_dups = df.drop_duplicates(subset=["first_name", "last_name", "email"])
    num_rows_no_dups = df_no_dups.shape[0]
    result_df[phase] = hprint.perc(num_rows_no_dups, df.shape[0])

    if debug == phase and (num_rows_no_dups != df.shape[0]):
        duplicated = df.duplicated(subset=["first_name", "last_name", "email"])
        display(df[duplicated])
        assert 0
    df = df_no_dups
    # 2) Remove names with non-ASCII characters
    phase = "count_no_ascii"
    valid_ascii = df["first_name"].apply(lambda x: x.isascii())
    num_rows_only_ascii = valid_ascii.sum()
    result_df[phase] = hprint.perc(num_rows_only_ascii, df.shape[0])
    if debug == phase and (num_rows_only_ascii != df.shape[0]):
        display(df[valid_ascii])
        assert 0
    df = df[valid_ascii]
    # 3) Report stats about email.
    phase = "count_email"
    if email_col in df.columns:
        valid_mask = (df[email_col] != "") & (df[email_col] != "_nan_")
        num_valid = valid_mask.sum()
        result_df[phase] = hprint.perc(num_valid, df.shape[0])
        if debug == phase and (num_valid != df.shape[0]):
            display(df[~valid_mask])
            assert 0
    else:
        _LOG.warning("No 'email=%s' column", email_col)
    # 4) Report stats about email verification.
    phase = "count_email_verification"
    if email_verification_col in df.columns:
        valid_mask = [
            (not v.startswith("_")) and (v != "")
            for v in df[email_verification_col]
        ]
        num_valid = sum(valid_mask)
        result_df[phase] = hprint.perc(num_valid, df.shape[0])
        if debug == phase and (num_valid != df.shape[0]):
            display(df[~valid_mask])
            assert 0
    else:
        _LOG.warning("No '%s' column", email_verification_col)
    # 4) Check for same first / last name.
    phase = "count_name_dups"
    duplicated = df.duplicated(subset=["first_name", "last_name"])
    result_df[phase] = hprint.perc(duplicated.sum(), df.shape[0])
    # 5) Report origin.
    phase = "count_origin"
    col_name = "origin"
    valid_mask = df[col_name] != ""
    num_valid = sum(valid_mask)
    result_df[phase] = hprint.perc(num_valid, df.shape[0])
    if debug == phase and (num_valid != df.shape[0]):
        display(df[~valid_mask])
        assert 0
    #
    result_df = pd.Series(result_df).to_frame()
    display(result_df)


# TODO(gp): -> display_heatmap_contact_df
def print_contact_df_detailed_stats(
    df: pd.DataFrame, *, mode: str = "only_pct"
) -> None:
    """
    This is similar to `get_column_stats()` but it shows a heatmap of the stats
    and understands the semantics of a contact df.
    """
    stats_df = []

    def _perc(a: float, b: float) -> float:
        return hprint.perc(a, b, only_perc=True, use_float=True)

    for col_name in df.columns:
        # Compute the stats.
        type_ = str(df[col_name].dtype)
        num_empty_vals = int((df[col_name] == "").sum())
        num_tokens_vals = int((df[col_name] == "nan").sum())
        num_nan_vals = int((df[col_name] == "nan").sum())
        num_unique_vals = int(len(df[col_name].unique()))
        num_invalid_vals = int(
            (df[col_name] == "").sum() + (df[col_name] == "nan").sum()
        )
        num_valid_vals = df.shape[0] - num_invalid_vals
        # Package the results.
        stats_df_tmp = [
            col_name,
            type_,
            num_valid_vals,
            _perc(num_valid_vals, df.shape[0]),
            num_invalid_vals,
            _perc(num_invalid_vals, df.shape[0]),
            num_unique_vals,
            _perc(num_unique_vals, df.shape[0]),
            num_empty_vals,
            _perc(num_empty_vals, df.shape[0]),
            num_nan_vals,
            _perc(num_nan_vals, df.shape[0]),
        ]
        stats_df_tmp = pd.DataFrame(stats_df_tmp).T
        stats_df.append(stats_df_tmp)
    #
    stats_df = pd.concat(stats_df, axis=0)
    stats_df.columns = [
        "col_name",
        "type",
        "valid",
        "valid [pct]",
        "invalid",
        "invalid [pct]",
        "unique",
        "unique [pct]",
        "empty",
        "empty [pct]",
        "nan",
        "nan [pct]",
    ]
    stats_df.index = range(0, stats_df.shape[0])
    if mode == "only_pct":
        columns = [
            "col_name",
            "valid [pct]",
            "unique [pct]",
            "invalid [pct]",
            "empty [pct]",
            "nan [pct]",
        ]
        hdbg.dassert_is_subset(columns, stats_df.columns)
        stats_df = stats_df[columns]
        #
        stats_df.set_index("col_name", inplace=True)
        stats_df = stats_df.astype(float)
        display(hpandas.heatmap_df(stats_df))
    else:
        hpandas.heatmap_df(stats_df)


def add_info_to_result(
    result: Dict[str, Any], tag: str, a: float, b: float, info_mode: str
) -> Dict[str, Any]:
    if info_mode == "all":
        # 4225 / 7377 = 57.27%
        vals = [(tag, hprint.perc(a, b))]
    elif info_mode == "only_pct":
        # 57.27%
        vals = [(tag, hprint.perc(a, b, only_perc=True))]
    elif info_mode == "only_num":
        # 4225
        vals = [(tag, str(a))]
    elif info_mode == "num_pct":
        # 4225, 57.27%
        vals = [
            (tag, str(a)),
            (tag + " [%]", hprint.perc(a, b, only_perc=True)),
        ]
    elif info_mode == "num_den_pct":
        # 4225/7377, 57.27%
        vals = [
            (tag, hprint.perc(a, b, only_fraction=True)),
            (tag + " [%]", hprint.perc(a, b, only_perc=True)),
        ]
    else:
        raise ValueError("Invalid info_mode='%s'" % info_mode)
    for tag_tmp, val in vals:
        hdbg.dassert_not_in(tag_tmp, result.keys())
        result[tag_tmp] = val
    return result


def get_column_stats(
    contact_df: pd.DataFrame,
    col_name: Union[List[str], str],
    *,
    mode: str = "print_df",
    info_mode: str = "only_pct",
) -> Any:
    """
    Compute statistics for a column or list of columns in a contact_df.

    :param contact_df: The DataFrame containing the data.
    :param col_name: The column name or list of column names to compute
        stats for.
    :param mode: The mode of output
    :returns: The result in one of different formats
    """
    hdbg.dassert_isinstance(col_name, (str, list))
    # If a list of columns was passed compute the stats for each one.
    if isinstance(col_name, list):
        dfs = []
        for col_name_ in col_name:
            df_tmp = get_column_stats(
                contact_df, col_name_, mode="df", info_mode=info_mode
            )
            dfs.append(df_tmp)
        df = pd.concat(dfs)
        if mode == "df":
            return df
        elif mode == "print_df":
            display(df)
            return None
        else:
            raise ValueError("Invalid mode='%s'" % mode)
    # Collect results.
    result = {}
    #
    vals = contact_df[col_name]
    num_vals = len(vals)
    # result["num_vals"] = num_vals
    result = add_info_to_result(result, "num_vals", num_vals, None, "only_num")
    #
    unique_vals = vals.unique()
    num_unique_vals = len(unique_vals)
    # result["num_unique_vals"] = hprint.perc(num_unique_vals, num_vals)
    result = add_info_to_result(
        result, "num_unique_vals", num_unique_vals, num_vals, info_mode
    )
    #
    num_empty_vals = sum(t == "" for t in vals)
    # result["num_empty_vals"] = hprint.perc(num_empty_vals, num_vals)
    result = add_info_to_result(
        result, "num_empty_vals", num_empty_vals, num_vals, info_mode
    )
    #
    tokens = [t for t in vals if t.startswith("_")]
    num_tokens = len(tokens)
    # result["num_tokens"] = hprint.perc(num_tokens, num_vals)
    result = add_info_to_result(
        result, "num_tokens", num_tokens, num_vals, info_mode
    )
    #
    unique_tokens = sorted(list(set(tokens)))
    result["unique_tokens"] = "%s %s" % (
        len(unique_tokens),
        " ".join(unique_tokens),
    )
    # Return values.
    if mode in ("str", "print_str"):
        txt = ["%s=%s" % (k, v) for k, v in result.items()]
        txt = "\n".join(txt)
        if mode == "str":
            value = txt
        elif mode == "print_str":
            print(txt)
            value = None
        else:
            raise ValueError("Invalid mode='%s'" % mode)
    elif mode in ("df", "print_df"):
        df = pd.Series(result).to_frame().T
        df.index = [col_name]
        if mode == "df":
            value = df
        elif mode == "print_df":
            display(df)
            value = None
        else:
            raise ValueError("Invalid mode='%s'" % mode)
    else:
        raise ValueError("Invalid mode='%s'" % mode)
    return value


# #############################################################################
# Infer category
# #############################################################################


def infer_category(
    contact_df: pd.DataFrame,
    *,
    leave_debug_cols: bool = False,
    log_level: int = logging.DEBUG,
) -> pd.DataFrame:
    contact_df = contact_df.copy()
    src_col_names = contact_df.columns
    # Select the empty category.
    main_mask = contact_df["category"] == ""
    _LOG.log(
        log_level,
        "Empty category %s",
        hprint.perc(main_mask.sum(), len(main_mask)),
    )
    #
    masks = {}
    stats_df = []

    def _append_mask(mask, tag):
        mask = pd.Series(mask, index=main_mask.index)
        masks[tag] = mask & main_mask
        # print("%s: %s" % (tag, hprint.perc(sum(mask), len(mask))))
        stats_df.append([tag, sum(mask), 100.0 * sum(mask) / len(mask)])

    keyword = "vc"
    mask = [keyword in val.lower() for val in contact_df["company_domain"]]
    _append_mask(mask, "vc_in_domain")
    #
    keyword = "vc"
    mask = [keyword in val.lower() for val in contact_df["company_name"]]
    _append_mask(mask, "vc_in_name")
    #
    keyword = "venture"
    mask = [keyword in val.lower() for val in contact_df["company_name"]]
    _append_mask(mask, "venture_in_name")
    #
    mask = contact_df["stages"] != ""
    _append_mask(mask, "stages")
    #
    keyword = "partner"
    mask = [keyword in val.lower() for val in contact_df["job_title"]]
    _append_mask(mask, "partner_in_job")
    #
    keyword = "vc"
    mask = [keyword in val.lower() for val in contact_df["job_title"]]
    _append_mask(mask, "vc_in_job")
    #
    keyword = "invest"
    mask = [keyword in val.lower() for val in contact_df["job_title"]]
    _append_mask(mask, "invest_in_job")
    #
    keyword = "venture"
    mask = [keyword in val.lower() for val in contact_df["job_title"]]
    _append_mask(mask, "venture_in_job")
    #
    keyword = "director"
    mask = [keyword in val.lower() for val in contact_df["job_title"]]
    _append_mask(mask, "director_in_job")
    #
    keyword = "scout"
    mask = [keyword in val.lower() for val in contact_df["job_title"]]
    _append_mask(mask, "scout_in_job_title")
    #
    keyword = "eir"
    mask = [keyword in val.lower() for val in contact_df["job_title"]]
    _append_mask(mask, "eir_in_job_title")
    #
    keyword = "in residence"
    mask = [keyword in val.lower() for val in contact_df["job_title"]]
    _append_mask(mask, "in_residence_in_job_title")
    #
    keyword = "capital"
    mask = [keyword in val.lower() for val in contact_df["company_name"]]
    _append_mask(mask, "capital_in_company_name")
    # Compute the stats from the masks.
    stats_df = pd.DataFrame(stats_df, columns=["tag", "num", "pct [%]"])
    stats_df.sort_values(by="num", ascending=False, inplace=True)
    stats_df.set_index("tag", inplace=True)
    display(stats_df)
    # Decorate with the mask.
    for tag, mask in masks.items():
        contact_df[tag] = False
        contact_df.loc[mask, tag] = True
    # Mark as `is_vc` for the rows that have at lease one mask.
    contact_df["is_vc"] = contact_df[masks.keys()].sum(axis=1)
    _LOG.log(log_level, contact_df[masks.keys()].sum(axis=0))
    display(get_value_counts_stats_df(contact_df, "is_vc"))
    #
    contact_df["category"] = np.where(
        contact_df["is_vc"] > 0,
        "Venture Fund " "(inferred)",
        contact_df["category"],
    )
    #
    if not leave_debug_cols:
        contact_df = contact_df[src_col_names]
    #
    return contact_df


# TODO(gp): Move to hpandas
def get_value_counts_stats_df(
    df: pd.DataFrame, col_name: str, *, num_rows: int = 10
) -> pd.DataFrame:
    hdbg.dassert_in(col_name, df.columns)
    stats_df = df[col_name].value_counts().to_frame()
    stats_df["pct [%]"] = stats_df["count"] / len(df) * 100
    if num_rows > 0:
        stats_df = stats_df.head(num_rows)
    return stats_df


def head(
    df: pd.DataFrame, *, seed: Union[int, None] = None, num_rows: int = 2
) -> None:
    print("shape=", df.shape)
    print("columns=", df.columns.tolist())
    print()
    if seed is not None:
        np.random.seed(seed)
        index = np.random.choice(df.index, num_rows, replace=False)
        index = sorted(index)
        df = df.loc[index]
    else:
        df = df.head(num_rows)
    display(df)


# TODO(gp): Use hgoogle_api
def save_to_gsheet(
    df: pd.DataFrame,
    *,
    name: str = "display_tmp",
    use_timestamp: bool = False,
) -> None:
    """
    Save a DataFrame to a Google Sheet.

    :param df: The DataFrame to save.
    :param name: The name of the Google Sheet.
    :param use_timestamp: Whether to append a timestamp to the name.
    """
    if use_timestamp:
        timestamp = hsystem.get_timestamp()
        name += "." + timestamp
    # Save in gp/test.
    folder_id = "1HTyRpbb4tFqRxjX6yQgosmCcpVxcF6X9"
    client = gspread_pandas.Client()
    spreadsheet = client.create(name, folder_id=folder_id)
    # Connect to the newly created spreadsheet using Spread
    spread = gspread_pandas.Spread(spreadsheet.url)
    # create_sheet=True,
    # create_spread=True)
    print(spread.url)
    # Write DataFrame to the Google Sheet (this creates the sheet if it
    # doesn't exist).
    spread.df_to_sheet(df, index=True, sheet="Sheet1", start="A1", replace=True)
    _LOG.info("Saved to %s", name)


# #############################################################################
# Yamm
# #############################################################################


def normalize_yamm_schema(
    df: pd.DataFrame, cols_map: Dict[str, str]
) -> pd.DataFrame:
    """
    Normalize the schema of a YAMM DataFrame.

    :param df: The DataFrame to normalize.
    :param cols_map: A mapping of column names from the original schema
        to the desired schema.
    :return: The normalized DataFrame.
    """
    # Rename columns.
    hdbg.dassert_is_subset(
        cols_map.keys(),
        df.columns,
        "All columns to rename must be present in df",
    )
    df = df[cols_map.keys()]
    df_out = df.rename(columns=cols_map, inplace=False)
    return df_out


def get_yamm_results(normalize: bool = True) -> pd.DataFrame:
    """
    Get the results from all the YAMM campaigns.

    :return: The result df ``` hash origin
        campaign_name first_name email
        merge_status 0 a1f523b406e45311cbfb3e084474264f
        Wave1-20241210-folkapp1 campaign0_VC_causify Jovina
        jovina@pfmlp.com EMAIL_CLICKED 1
        9c07faa88042d6aea79318410c9daa5e Wave1-20241210-folkapp1
        campaign0_VC_causify Pen pen@innovating.capital
        EMAIL_OPENED 2 4d746ffd6d47c78fcf66672606bd609a
        Wave1-20241210-folkapp1 campaign0_VC_causify Thomas
        tbliska@cross.com EMAIL_SENT ```
    """
    data = [
        #
        (
            "Wave1-20241210-folkapp1",
            "campaign0_VC_causify",
            "https://docs.google.com/spreadsheets/d"
            "/1mwRy0yTTCnTR14npWe7xATBYLb7DV9Pt1a2p4DjloQA",
            ["YAMM-20241210", "YAMM-20241210-1", "YAMM-20241210-2"],
        ),
        #
        (
            "Wave2-20241210-folkapp1",
            "campaign0_VC_causify",
            "https://docs.google.com/spreadsheets/d"
            "/1eufg2XREYbXnCy8tygGKAkDigM0OE_fJRmnHTDxFQ8A",
            ["YAMM-2024-12-"],
        ),
        #
        (
            "campaign_1_batch1",
            "campaign1_VC_causify",
            "https://docs.google.com/spreadsheets/d"
            "/10bWbYHdzl5KvvccHI5grtquFraO29MFP3iBcwkuVj1A",
            ["Sheet1", "Sheet2"],
        ),
        #
        (
            "Campaign2_UMD_YAMM",
            "campaign2_VC_UMD",
            "https://docs.google.com/spreadsheets/d/1rpM5MeMtAwRvbV1fCngKD4"
            "-xe7Wc19ikvs7ljx9HIeA",
            ["2024-12-28", "2024-12-30", "2025-01-02"],
        ),
    ]
    #
    yamm_dfs = []
    cols = [
        "hash",
        "origin",
        "campaign_name",
        "first_name",
        "email",
        "Merge status",
    ]
    for origin, campaign_name, url, gsheet_names in data:
        for gsheet_name in gsheet_names:
            _LOG.debug("Reading %s -> %s", url, gsheet_name)
            yamm_df = get_cached_sheet_to_df(url, gsheet_name)
            yamm_df["origin"] = origin
            yamm_df["campaign_name"] = campaign_name
            _LOG.debug("Read %s -> %s", gsheet_name, yamm_df.shape[0])
            hdbg.dassert_is_subset(cols, yamm_df.columns)
            yamm_df = yamm_df[cols]
            yamm_dfs.append(yamm_df)
    #
    yamm_dfs = pd.concat(yamm_dfs)
    _LOG.info("Read %s rows", yamm_dfs.shape[0])
    #
    if normalize:
        cols_map = {
            "hash": "hash",
            "origin": "origin",
            "campaign_name": "campaign_name",
            "first_name": "first_name",
            "email": "email",
            "Merge status": "merge_status",
        }
        yamm_dfs = normalize_yamm_schema(yamm_dfs, cols_map)
        display(yamm_dfs.head())
        # Remove duplicates.
        num_before = yamm_dfs.shape[0]
        valid_mask = yamm_dfs.duplicated(
            subset=["first_name", "email", "campaign_name"]
        )
        num_after = (~valid_mask).sum()
        _LOG.info(
            "Removed %s duplicates"
            % hprint.perc(num_before - num_after, num_before)
        )
        yamm_dfs = yamm_dfs[~valid_mask]
    _LOG.info("Number of rows: %s", yamm_dfs.shape[0])
    return yamm_dfs


# Total sent    726      100%
# BOUNCED        20      2.8%     Email not delivered (e.g., email account deactivate)
# EMAIL_OPENED  266      36.6%    User opened email
# RESPONDED      24      3.4%     User responded
# EMAIL_CLICKED  31      4.4%     User clicked one link
# EMAIL_SENT    385      53.0%    Email sent but not opened
# UNSUBSCRIBED    0      0.0%     Unsubscribed
# DELIVERED     706      97.2%    Email was actually delivered
#   = total_sent - bounced


# TODO: -> get_yamm_stats
def yamm_stats(df: pd.DataFrame) -> Dict[str, int]:
    """
    Calculate statistics for a YAMM campaign DataFrame.

    :param df: The DataFrame containing YAMM campaign data.
    :return: A dictionary with counts of different email statuses.
    """
    # Group by merge status.
    col_name = "merge_status"
    hdbg.dassert_in(col_name, df.columns)
    df_stats = df.groupby(col_name)[col_name].count()
    vals = df_stats.to_dict()
    #
    yamm_status = {
        "BOUNCED": "bounced",
        "EMAIL_OPENED": "opened",
        "RESPONDED": "responded",
        "EMAIL_CLICKED": "clicked",
        "EMAIL_SENT": "unopened",
        "UNSUBSCRIBED": "unsubscribed",
    }
    vals2 = {}
    for k, v in yamm_status.items():
        vals2[v] = int(vals.get(k, 0))
    #
    vals2["total"] = df.shape[0]
    vals2["delivered"] = vals2["total"] - vals2["bounced"]
    return vals2


def yamm_stats_to_pct(obj: Union[pd.DataFrame, Dict], *, name: str = "") -> None:
    """
    Convert YAMM campaign statistics to percentages.

    :param obj: A DataFrame containing YAMM campaign data or a
        dictionary with YAMM campaign statistics.
    :param name: Optional name of the campaign
    :return: A DataFrame with the percentage statistics of the YAMM campaign.
    
        ```
           total  delivered  bounced  opened  responded  clicked  unopened  unsubscribed
        0  786.0       97.3      2.7    35.2        3.1      4.6      54.3           0.0
        ```
    """
    if isinstance(obj, pd.DataFrame):
        vals = yamm_stats(obj)
    elif isinstance(obj, dict):
        vals = obj
    else:
        raise ValueError("Invalid object type '%s'" % type(obj))
    #
    res = {}
    res["total"] = int(vals["total"])
    yamm_ordered = (
        "delivered bounced opened responded clicked unopened unsubscribed"
    ).split()
    for k in yamm_ordered:
        hdbg.dassert_lte(vals[k], vals["total"])
        res[k] = vals[k] / vals["total"]
        res[k] = float("%.1f" % (res[k] * 100))
    res = pd.Series(res)
    res = res.to_frame().T
    if name != "":
        res.index = [name]
    return res


def yamm_stats_by_campaign(yamm_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate YAMM campaign statistics for each campaign.

    :param yamm_df: The DataFrame containing YAMM campaign data.
    :return: A DataFrame with the statistics for each campaign. 
    ```
                            total   delivered bounced opened responded clicked  unopened unsubscribed
    campaign0_VC_causify    727.0   97.2      2.8     36.9   3.3       4.3     52.7      0.0
    campaign1_VC_causify    59.0    98.3      1.7     15.3   0.0       8.5     74.6      0.0
    campaign2_VC_UMD        249.0   99.2      0.8     49.0   3.6       2.4     43.8      0.4
    total                   1035.0  97.8      2.2     38.6   3.2       4.1     51.8      0.1
    ```
    """
    stats_dfs = []
    #
    for campaign_name, yamm_df_tmp in yamm_df.groupby("campaign_name"):
        stats_df = yamm_stats_to_pct(yamm_df_tmp, name=campaign_name)
        stats_dfs.append(stats_df)
    # Add the total.
    stats_df = yamm_stats_to_pct(yamm_df, name="total")
    stats_dfs.append(stats_df)
    # Create the final df.
    stats_dfs = pd.concat(stats_dfs)
    return stats_dfs


# #############################################################################


def _update_contact_df_with_yamm_df(
    contact_df: pd.DataFrame,
    campaign_id: str,
    yamm_df: pd.DataFrame,
    key_col: str,
) -> pd.DataFrame:
    if campaign_id not in contact_df.columns:
        contact_df[campaign_id] = ""
    # Create a mapping from key to index.
    hdbg.dassert_in(key_col, contact_df.columns)
    key_to_idx = {row[key_col]: idx for idx, row in contact_df.iterrows()}
    # For each row in the YAMM results, update the master list.
    num_updates = 0
    for _, row in yamm_df.iterrows():
        key = row[key_col]
        if key not in key_to_idx:
            _LOG.warning("Can't find key '%s' in the master list", key)
            continue
        merge_status = row["merge_status"]
        idx = key_to_idx[key]
        _LOG.debug("Updating %s %s", idx, merge_status)
        contact_df.loc[idx, campaign_id] = merge_status
        #
        num_updates += 1
    _LOG.info("num_updates=%s", hprint.perc(num_updates, yamm_df.shape[0]))
    return contact_df


def update_contact_df_with_yamm_df(
    contact_df: pd.DataFrame,
    yamm_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Update the master list with the YAMM results.

    :param contact_df: The master list DataFrame.
    :param yamm_df: The YAMM results DataFrame.
    """
    contact_df = contact_df.copy()
    #
    for campaign_id, yamm_df_tmp in yamm_df.groupby("campaign_name"):
        _LOG.info("Updating for campaign_id='%s'", campaign_id)
        contact_df = _update_contact_df_with_yamm_df(
            contact_df, campaign_id, yamm_df_tmp, "hash"
        )
    #
    return contact_df


# #############################################################################
# Select campaign
# #############################################################################


def select_campaign(
    contact_df: pd.DataFrame,
    campaign_col_name: str,
    type_: str,
    num_rows: int,
    *,
    seed: int = 1,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Select a subset of rows from the master list DataFrame for a campaign.

    :param contact_df: The master list DataFrame.
    :param campaign_col_name: The column name indicating the campaign
        status.
    :param type_: The type of selection (e.g., 'email', 'linkedin')
    :param num_rows: The number of rows to select.
    :param seed: The random seed for reproducibility.
    :return: A df containing the selected campaign
    """
    contact_df = contact_df.copy()
    if campaign_col_name not in contact_df.columns:
        contact_df[campaign_col_name] = ""
    # Filter the campaign_df.
    campaign_df = contact_df
    # 1) Remove the one already sent.
    col_name = campaign_col_name
    valid_mask = campaign_df[col_name] == ""
    print(
        "Selected %s from %s"
        % (hprint.perc(valid_mask.sum(), len(valid_mask)), col_name)
    )
    campaign_df = campaign_df[valid_mask]
    # 2) Select the type of campaign.
    if type_ == "email":
        # Select rows with email.
        col_name = "email"
        valid_mask = campaign_df[col_name] != ""
        print(
            "Selected %s from %s"
            % (hprint.perc(valid_mask.sum(), len(valid_mask)), col_name)
        )
        campaign_df = campaign_df[valid_mask]
        # Select rows with email verification.
        col_name = "email_verification"
        valid_mask = campaign_df[col_name].isin({"valid", "all_valid"})
        print(
            "Selected %s from %s"
            % (hprint.perc(valid_mask.sum(), len(valid_mask)), col_name)
        )
        campaign_df = campaign_df[valid_mask]
        #
        campaign_col_names = (
            "hash first_name last_name company_name email email_verification"
        ).split()
    elif type_ == "linkedin":
        # Select rows with LinkedIn.
        col_name = "linkedin_url"
        valid_mask = campaign_df[col_name] != ""
        print(
            "Selected %s from %s"
            % (hprint.perc(valid_mask.sum(), len(valid_mask)), col_name)
        )
        campaign_df = campaign_df[valid_mask]
        campaign_col_names = (
            "hash first_name last_name company_name linkedin_url"
        ).split()
    else:
        raise ValueError("Invalid type_='%s'" % type_)
    # 3) Pick random `num_rows` rows.
    campaign_df = campaign_df[campaign_col_names]
    campaign_df.sort_values(by=["hash"], inplace=True)
    campaign_df = campaign_df.reset_index(drop=True)
    index = campaign_df.index
    hdbg.dassert_eq(index[0], 0)
    hdbg.dassert_eq(index[-1], len(campaign_df) - 1)
    np.random.seed(seed)
    if num_rows < 0:
        num_rows = len(campaign_df)
    index = np.random.choice(index, num_rows, replace=False)
    index = sorted(index)
    campaign_df = campaign_df.iloc[index]
    # Update the master list.
    hashes = campaign_df["hash"]
    indices = contact_df["hash"].isin(hashes)
    contact_df.loc[indices, campaign_col_name] = "selected"
    return campaign_df, contact_df


def get_short_contact_df(contact_df: pd.DataFrame) -> pd.DataFrame:
    col_names = [
        "hash",
        "first_name",
        "last_name",
        "email",
        "linkedin_url",
        "company_name",
    ]
    col_names.extend(
        [
            col_name
            for col_name in contact_df.columns
            if col_name.startswith("campaign")
        ]
    )
    return contact_df[col_names]