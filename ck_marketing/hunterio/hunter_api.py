"""
Import as:

import ck_marketing.hunterio.hunter_api as cmhuhuap
"""

import functools
import logging
import os
import re
from typing import Any, Callable, Dict, List, Tuple, Union

import pandas as pd
import requests
from tqdm.autonotebook import tqdm

import ck_marketing.process_automation.hyamm as cmprauhy
import helpers.hcache_simple as hcacsimp
import helpers.hdbg as hdbg
import helpers.hprint as hprint

_LOG = logging.getLogger(__name__)


API_KEY = os.environ["HUNTER_API_KEY"]


# #############################################################################
# Account
# #############################################################################


def get_account_info() -> Dict[str, Any]:
    """
    {'searches': {'available': 5000, 'over_quota': 0, 'used': 20},
    'verifications': {'available': 10000, 'over_quota': 0, 'used': 169}}
    """
    url = f"https://api.hunter.io/v2/account?api_key={API_KEY}"
    response = requests.get(url)
    response.raise_for_status()
    # {'data': {'calls': {'_deprecation_notice': 'Sums the searches and the '
    #                                            'verifications, giving an unprecise '
    #                                            'look of the available requests',
    #                     'available': 15000,
    #                     'used': 189},
    #           'email': 'crypto@crypto-kaizen.com',
    #           'first_name': 'Crypto',
    #           'last_name': 'Crypto',
    #           'plan_level': 2,
    #           'plan_name': 'Growth',
    #           'requests': {'searches': {'available': 5000,
    #                                     'over_quota': 0,
    #                                     'used': 20},
    #                        'verifications': {'available': 10000,
    #                                          'over_quota': 0,
    #                                          'used': 169}},
    #           'reset_date': '2025-01-25',
    #           'team_id': 4401155}}
    data = response.json()
    result = data["data"]["requests"]
    result["reset_date"] = data["data"]["reset_date"]
    return result


# #############################################################################
# Enrich
# #############################################################################


# {'data': {'accept_all': False,
#           'company': 'BraunHagey & Borden',
#           'domain': 'braunhagey.com',
#           'email': 'chase@braunhagey.com',
#           'first_name': 'Lauren',
#           'last_name': 'Chase',
#           'linkedin_url': 'https://www.linkedin.com/in/lauren-chase-97128560',
#           'phone_number': None,
#           'position': 'Counsel',
#           'score': 99,
#           'sources': [{'domain': 'braunhagey.com',
#                        'extracted_on': '2018-10-24',
#                        'last_seen_on': '2024-12-18',
#                        'still_on_page': True,
#                        'uri': 'http://braunhagey.com/lauren-chase'},
#                       {'domain': 'braunhagey.squarespace.com',
#                        'extracted_on': '2021-06-12',
#                        'last_seen_on': '2024-10-31',
#                        'still_on_page': True,
#                        'uri': 'http://braunhagey.squarespace.com/lauren-chase'},
#                       {'domain': 'braunhagey.com',
#                        'extracted_on': '2024-09-18',
#                        'last_seen_on': '2024-09-18',
#                        'still_on_page': True,
#                        'uri': 'http://braunhagey.com/news'}],
#           'twitter': None,
#           'verification': {'date': '2024-12-31', 'status': 'valid'}},
#  'meta': {'params': {'company': 'BraunHagey Borden LLP',
#                      'domain': None,
#                      'first_name': 'Lauren',
#                      'full_name': None,
#                      'last_name': 'Chase',
#                      'max_duration': None}}}


def enrich_intrinsic(
    first_name: str,
    last_name: str,
    company: str,
    is_company: bool,
    *,
    issue_warnings: bool = True,
) -> Dict[str, Any]:
    hdbg.dassert_isinstance(first_name, str)
    hdbg.dassert_isinstance(last_name, str)
    hdbg.dassert_isinstance(company, str)
    if first_name == "" or last_name == "" or company == "":
        _LOG.warning(
            "Missing information: first_name='%s' last_name='%s' company='%s'",
            first_name,
            last_name,
            company,
        )
        return {"error": "_missing_info_"}
    # Query.
    if is_company:
        tag = "company"
    else:
        tag = "domain"
    url = f"https://api.hunter.io/v2/email-finder?{tag}={company}&first_name={first_name}&last_name={last_name}&api_key={API_KEY}"
    # Parse the results.
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        if issue_warnings:
            _LOG.warning(
                "Error fetching email for '%s' '%s' at '%s': %s",
                first_name,
                last_name,
                company,
                e,
            )
        data = {"error": "_error_"}
    return data


import functools


# Decorator
def simple_cache(func: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Get the function name.
        func_name = func.__name__
        if func_name.endswith("_intrinsic"):
            func_name = func_name[: -len("_intrinsic")]
        hcacsimp.set_cache_property("system", func_name, "type", "json")
        # Get the cache.
        cache = hcacsimp.get_cache(func_name)
        # Get the key.
        # key = (args, frozenset(kwargs.items()))
        key = args
        key = str(key)
        _LOG.debug("key=%s", key)
        # Get the cache properties.
        cache_perf = hcacsimp.get_cache_perf(func_name)
        _LOG.debug("cache_perf is None=%s", cache_perf is None)
        # Update the performance stats.
        if cache_perf:
            hdbg.dassert_in("tot", cache_perf)
            cache_perf["tot"] += 1
        # Handle a forced refresh.
        force_refresh = hcacsimp.get_cache_property(
            "user", func_name, "force_refresh"
        )
        _LOG.debug("force_refresh=%s", force_refresh)
        if not force_refresh and key in cache:
            # Update the performance stats.
            if cache_perf:
                cache_perf["hits"] += 1
            # Retrieve the value from the cache.
            value = cache[key]
        else:
            # Update the performance stats.
            if cache_perf:
                cache_perf["misses"] += 1
            # Abort on cache miss.
            abort_on_cache_miss = hcacsimp.get_cache_property(
                "user", func_name, "abort_on_cache_miss"
            )
            _LOG.debug("abort_on_cache_miss=%s", abort_on_cache_miss)
            if abort_on_cache_miss:
                raise ValueError("Cache miss for key='%s'" % key)
            # Report on cache miss.
            report_on_cache_miss = hcacsimp.get_cache_property(
                "user", func_name, "report_on_cache_miss"
            )
            _LOG.debug("report_on_cache_miss=%s", report_on_cache_miss)
            if report_on_cache_miss:
                _LOG.debug("Cache miss for key='%s'", key)
                return "_cache_miss_"
            # Access the intrinsic function.
            value = func(*args, **kwargs)
            # Update cache.
            cache[key] = value
            _LOG.debug("Updating cache with key='%s' value='%s'", key, value)
        return value

    return wrapper


enrich = simple_cache(enrich_intrinsic)


# #############################################################################
# Find email
# #############################################################################


# TODO(gp): This is deprecated since enriching the data is more general.
def find_email_intrinsic(
    first_name: str,
    last_name: str,
    company: str,
    is_company: bool,
    *,
    issue_warnings: bool = True,
) -> str:
    """
    Find the email address for a given name and company using Hunter.io.

    This function sends a request to the Hunter.io API to find an email
    address based on the provided first name, last name, and company name.
    This function is specific to the company name.

    :param first_name: The first name of the person.
    :param last_name: The last name of the person.
    :param company: The company name where the person works.
    :return: The found email address or a special value
        - `_missing_info_`: not all the info is available to perform a query
        - `_nan_`: hunter.io did not find an email address
        - `_error_`: hunter.io returned an error
    """
    data = enrich(first_name, last_name, company, is_company)
    if "error" in data:
        return data["error"]
    #
    email = "_nan_"
    if "data" in data and "email" in data["data"]:
        email = data["data"]["email"]
    if email is None:
        if issue_warnings:
            _LOG.warning(
                "Email not found for '%s' '%s' at '%s'",
                first_name,
                last_name,
                company,
            )
        email = "_nan_"
    hdbg.dassert_ne(str(email), "None")
    return email


find_email = simple_cache(find_email_intrinsic)


def find_bulk_emails(
    df: pd.DataFrame,
    first_name_col: str,
    last_name_col: str,
    company_col: str,
    *,
    is_company: bool = True,
    incremental: bool = True,
    target_email_col: str = "hunterio.email",
) -> pd.DataFrame:
    """
    Find email addresses in bulk using Hunter.io for each row in the DataFrame.

    Hunter.io does not provide a direct endpoint for bulk email
    extraction where we can input multiple domains at once and get the
    results in a single API call. So we need to make individual API
    calls for each domain and handle the aggregation of results at our
    end. This function takes company name as parameter.

    :param df: DataFrame with specified columns for first name, last
        name, and company.
    :param first_name_col: The column name for first names.
    :param last_name_col: The column name for last names.
    :param company_col: The column name for company names.
    :return: DataFrame with an additional column
        'hunter_extracted_email' containing the found email addresses,
        or None
    """
    hdbg.dassert(not df.empty, "DataFrame is empty")
    hdbg.dassert_in(first_name_col, df.columns)
    hdbg.dassert_in(last_name_col, df.columns)
    hdbg.dassert_in(company_col, df.columns)
    # Create or reuse the target column.
    if target_email_col in df.columns:
        _LOG.warning(
            "Column '%s' already exists in DataFrame. Overwriting values.",
            target_email_col,
        )
    else:
        df[target_email_col] = ""
    # Process the data frame.
    num_updates = 0
    for idx, row in tqdm(df.iterrows(), total=df.shape[0]):
        if incremental and row[target_email_col] != "":
            continue
        email = find_email(
            row[first_name_col],
            row[last_name_col],
            row[company_col],
            is_company=is_company,
        )
        df.loc[idx, target_email_col] = email
        num_updates += 1
    # Report stats.
    _LOG.info(
        "Updated %s rows with email addresses",
        hprint.perc(num_updates, df.shape[0]),
    )
    return df


# #############################################################################
# Verify email
# #############################################################################


def verify_email_intrinsic(email: str) -> str:
    """
    Verify an email address using hunter.io.

    :param email: email address to verify.
    :return: the verification status from hunter.io
        - 'valid'
        - 'accept_all'
        - 'invalid'
        - 'risky'
        - 'unknown'
        or a special value
        - `_missing_info_`: not all the info is available to perform a query
        - `_nan_`: hunter.io did not respond
        - `_error_`: hunter.io returned an error
    """
    assert 0
    hdbg.dassert_isinstance(email, str)
    val = ""
    # Check if it's a special value from `find_email()`.
    if email == "" or email.startswith("_"):
        val = "_missing_info_"
    # Check if it's a valid email.
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    m = re.match(pattern, email)
    if not m:
        _LOG.warning("Invalid email address: %s", email)
        val = "_error_"
    #
    if val == "":
        url = f"https://api.hunter.io/v2/email-verifier?email={email}&api_key={API_KEY}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            val = data.get("data", {}).get("status", "_nan_")
        except requests.exceptions.RequestException as e:
            _LOG.warning("Error verifying email %s: %s", email, e)
            val = "_error_"
    hdbg.dassert_ne(str(email), "None")
    return val


verify_email = simple_cache(verify_email_intrinsic)


def verify_bulk_emails(
    df: pd.DataFrame,
    email_col: str,
    *,
    incremental: bool = True,
    target_verification_col: str = "hunterio.email_verification",
) -> pd.DataFrame:
    """
    Verify emails in bulk using Hunter.io.

    :param df: contains the column containing email addresses to verify.
    :param email_col: column name for email addresses.
    :return: original df with an additional column 'hunter_verification'
        containing verification results.
    """
    hdbg.dassert_in(email_col, df.columns)
    # Create or reuse the target column.
    if target_verification_col in df.columns:
        _LOG.warning(
            "Column '%s' already exists in DataFrame. Overwriting values.",
            target_verification_col,
        )
    else:
        df[target_verification_col] = ""
    # Process the data frame.
    num_updates = 0
    for idx, row in tqdm(df.iterrows(), total=df.shape[0]):
        if incremental and row[target_verification_col] != "":
            continue
        # Verify the email.
        val = verify_email(row[email_col])
        # Update.
        df.loc[idx, target_verification_col] = val
        num_updates += 1
    # Report stats.
    _LOG.info(
        "Processed %s with verification",
        hprint.perc(num_updates, df.shape[0]),
    )
    return df


# #############################################################################
# Process email.
# #############################################################################


def _get_email_and_verification(
    first_name: str,
    last_name: str,
    company: str,
    is_company: bool,
) -> (str, str):
    """
    Get the email address and its verification status.
    """
    # If there is no email address, find one.
    email = find_email(
        first_name,
        last_name,
        company,
        is_company,
    )
    # If the email address is a token, then mark the value as invalid.
    if email.startswith("_"):
        verification_val = "invalid"
    else:
        verification_val = "valid"
    return email, verification_val


def process_email(
    df: pd.DataFrame,
    first_name_col: str,
    last_name_col: str,
    company_col: str,
    is_company: bool,
    *,
    mode: str = "AssumeEmailValid",
    dry_run: bool = False,
    prefix: str = "hunterio.",
) -> pd.DataFrame:
    """
    Process the DataFrame to find and verify email addresses.

    :param mode: The mode of processing.
        - `FromScratch`: ignore the email even if it exists, and verify that
        - `AssumeEmailValid`: use the email that already existed, if any, and
           verify it. If there is no email, find one.
    """
    # Columns to assign.
    email_col = "email"
    email_verification_col = "email_verification"
    # Enable cache perf.
    func_names = ["find_email", "verify_email"]
    if dry_run:
        hcacsimp.reset_cache_property()
        for func_name in func_names:
            _LOG.warning("Computing stats for '%s'", func_name)
            hcacsimp.enable_cache_perf(func_name)
            # hyamm.set_cache_property(func_name, "abort_on_cache_miss", True)
            hcacsimp.set_cache_property("system", func_name, "type", "json")
            print(hcacsimp.cache_property_to_str(func_name))
    # Process the data frame.
    for idx, row in tqdm(df.iterrows(), total=df.shape[0]):
        hdbg.dassert_isinstance(row, pd.Series)
        first_name = row[first_name_col]
        last_name = row[last_name_col]
        company = row[company_col]
        #
        if mode == "FromScratch":
            email_val, email_verification_val = _get_email_and_verification(
                first_name,
                last_name,
                company,
                is_company,
            )
        elif mode == "AssumeEmailValid":
            email_val = row[email_col]
            if email_val != "":
                # If there is an email address, use it, but verify it.
                email_verification_val = verify_email(email_val)
            else:
                # If there is no email address, find one.
                email_val, email_verification_val = _get_email_and_verification(
                    first_name,
                    last_name,
                    company,
                    is_company,
                )
        else:
            raise ValueError("Invalid mode='%s'" % mode)
        # Update dataframe.
        df.loc[idx, prefix + email_col] = email_val
        df.loc[idx, prefix + email_verification_col] = email_verification_val
    #
    if dry_run:
        for func_name in func_names:
            print(hcacsimp.get_cache_perf_stats(func_name))
            hcacsimp.disable_cache_perf(func_name)
    return df


# #############################################################################
# Process_enrich
# #############################################################################


def process_enrich(
    df: pd.DataFrame,
    first_name_col: str,
    last_name_col: str,
    company_col: str,
    is_company: bool,
    *,
    mode: str = "AssumeEmailValid",
    prefix: str = "hunterio.",
    dry_run: bool = False,
    enrich_kwargs: Union[Dict[str, Any], None] = None,
) -> pd.DataFrame:
    """
    Process a contact df to enrich it with additional information from
    Hunter.io.

    This function adds columns like:
    'hunterio.company_name', 'hunterio.company_domain', 'hunterio.email',
    'hunterio.linkedin_url', 'hunterio.job_title'

    :param df: The DataFrame to process.
    :param first_name_col: The column name for first names.
    :param last_name_col: The column name for last names.
    :param company_col: The column name for company names.
    :param is_company: Whether the company is specified.
    :param mode: The mode of processing.
    :param prefix: The prefix for new columns.
    :param enrich_kwargs: Additional keyword arguments for enrichment.
    :returns: The enriched DataFrame.
    """
    df = df.copy()
    if enrich_kwargs is None:
        enrich_kwargs = {}
    # Map from hunter.io to Contact_df columns.
    #   'company': 'BraunHagey & Borden',
    #   'domain': 'braunhagey.com',
    #   'email': 'chase@braunhagey.com',
    #   'first_name': 'Lauren',
    #   'last_name': 'Chase',
    #   'linkedin_url': 'https://www.linkedin.com/in/lauren-chase-97128560',
    #   'phone_number': None,
    #   'position': 'Counsel',
    cols_map = {
        "company": "company_name",
        "domain": "company_domain",
        "email": None,
        "linkedin_url": None,
        "position": "job_title",
    }
    cols_map = cmprauhy._resolve_None_in_cols_map(cols_map)
    # Create new columns, if needed.
    for v in cols_map.values():
        hdbg.dassert_is_not(v, None)
        col_name = prefix + v
        if col_name not in df.columns:
            df[prefix + v] = ""
    # Enable cache perf.
    func_name = "enrich"
    if dry_run:
        _LOG.warning("Computing stats for '%s'", func_name)
        hcacsimp.reset_cache_property()
        hcacsimp.enable_cache_perf(func_name)
        # hyamm.set_cache_property(func_name, "abort_on_cache_miss", True)
        hcacsimp.set_cache_property(func_name, "report_on_cache_miss", True)
        print(hcacsimp.cache_property_to_str(func_name))
    # Process the data frame.
    for idx, row in tqdm(df.iterrows(), total=df.shape[0]):
        if mode == "FromScratch":
            # Extract the first/last name and company.
            # TODO(gp): Factor this out.
            hdbg.dassert_in(first_name_col, row)
            first_name = row[first_name_col]
            hdbg.dassert_in(last_name_col, row)
            last_name = row[last_name_col]
            hdbg.dassert_in(company_col, row)
            company = row[company_col]
            # Get the data.
            data = enrich(
                first_name, last_name, company, is_company, **enrich_kwargs
            )
            # Extract the result.
            if "data" not in data:
                # _LOG.warning(
                #     f"No data for '{first_name}' '{last_name}' at " f"'{company}'"
                # )
                pass
            else:
                # Assign values to columns.
                for k, v in cols_map.items():
                    val = data["data"].get(k, "_nan_")
                    if str(val) == "None":
                        val = "_nan_"
                    df.loc[idx, prefix + v] = val
        elif mode == "AssumeEmailValid":
            raise ValueError
        else:
            raise ValueError
    # Report stats.
    if dry_run:
        print(hcacsimp.get_cache_perf_stats(func_name))
        hcacsimp.disable_cache_perf(func_name)
    return df


# #############################################################################
# Merge enriched value
# #############################################################################


def get_is_changed(
    srs1: pd.Series, srs2: pd.Series
) -> Tuple[List[str], List[str]]:
    """
    Compare two series and determine the merged values and their states.

    :param srs1: The first series to compare.
    :param srs2: The second series to compare.
    :returns: A tuple containing two lists: merged values and their
        states.
    """
    merged_val_srs = []
    merged_state_srs = []
    # Scan the two series.
    for val1, val2 in zip(srs1, srs2):
        is_nan1 = val1 in ("", "_nan_")
        is_nan2 = val2 in ("", "_nan_")
        if is_nan1 and is_nan2:
            # Both undefined.
            merged_val = "_nan_"
            merged_state = "_nan_"
        elif not is_nan1 and is_nan2:
            # Only the first one has a value.
            merged_val = val1
            merged_state = "_left_"
        elif is_nan1 and not is_nan2:
            # Only the second one has a value.
            merged_val = val2
            merged_state = "_right_"
        else:
            # They have both a value.
            merged_val = val1 if len(val1) > len(val2) else val2
            merged_state = "_improved_"
        # Update.
        _LOG.debug(hprint.to_str("val1 val2 merged_val merged_state"))
        merged_val_srs.append(merged_val)
        merged_state_srs.append(merged_state)
    # Return.
    return merged_val_srs, merged_state_srs


def merge_hunterio_values(
    contact_df: pd.DataFrame, *, prefix: str = "hunterio."
) -> pd.DataFrame:
    """
    Merge Hunter.io values into the contact DataFrame.

    :param contact_df: The contact DataFrame to process.
    :param prefix: The prefix for Hunter.io columns.
    :returns: The DataFrame with merged values.
    """
    contact_df = contact_df.copy()
    hdbg.dassert_no_duplicates(contact_df.columns)
    # Get the columns to process.
    col_names = []
    for col_name in contact_df.columns:
        if col_name.startswith(prefix):
            # Create the mapping between the columns with the prefix and not.
            prefix_col_name = col_name
            col_name2 = col_name[len(prefix) :]
            hdbg.dassert_in(col_name2, contact_df.columns)
            # Merge values.
            merged_val_srs, merged_state_srs = get_is_changed(
                contact_df[col_name2], contact_df[prefix_col_name]
            )
            contact_df[col_name2] = merged_val_srs
        else:
            col_names.append(col_name)
    # Extract the columns.
    hdbg.dassert_no_duplicates(col_names)
    contact_df = contact_df[col_names]
    return contact_df


# #############################################################################


def get_diagnostic_df(
    contact_df: pd.DataFrame, *, prefix: str = "hunterio."
) -> pd.DataFrame:
    """
    Generate a diagnostic DataFrame by comparing original and enriched data.

    :param contact_df: The original contact DataFrame.
    :param prefix: The prefix used for enriched columns.
    :returns: A DataFrame with diagnostic information.
    """
    contact_df = contact_df.copy()
    # Column names to return.
    col_names = [
        "first_name",
        "last_name",
    ]
    # Get the columns to process.
    for col_name in contact_df.columns:
        if col_name.startswith(prefix):
            # Create the mapping between the columns with the prefix and not.
            prefix_col_name = col_name
            col_name = col_name[len(prefix) :]
            _LOG.info("Found: " + hprint.to_str("col_name prefix_col_name"))
            hdbg.dassert_in(col_name, contact_df.columns)
            # Merge values.
            merged_val_srs, merged_state_srs = get_is_changed(
                contact_df[col_name], contact_df[prefix_col_name]
            )
            contact_df["merged." + col_name] = merged_val_srs
            # Update the columns to return.
            col_names.extend(
                [
                    col_name,
                    prefix_col_name,
                    "merged." + col_name,
                ]
            )
    # Extract the data frame to return.
    contact_df = contact_df[col_names]
    return contact_df


# hash                           003075018c71251c1de74dbfc2cec0fd
# timestamp
# first_name                                                Kevin
# last_name                                                Harper
# email                           kharper@downtown-associates.com
# email_verification
# linkedin_url
# job_title
# job_title_description
# company_name                           Downtown Associates, LLC
# company_domain
# city                                     Kennett Square, PA, US
# origin                                          hedge_fund_list
# stages
# restrictions
# industry
# category                                             hedge_fund
# notes
# hunterio.email                  kharper@downtown-associates.com
# hunterio.email_verification                             invalid


def get_email_stats(
    diagnostics_df: pd.DataFrame, col_name: str, is_email_verification: bool
) -> Dict[str, Any]:
    hdbg.dassert_in(col_name, diagnostics_df.columns)
    #
    only_perc = True
    reverse = True
    res = {}
    if is_email_verification:
        # In the case of `email_verifications`, the tokens are all the values.
        tokens = diagnostics_df[col_name].unique()
    else:
        # In the case of `email`, the tokens are all the values that do not
        # contain an `@`.
        tokens = [v for v in diagnostics_df[col_name].unique() if "@" not in v]
    tokens = sorted(tokens, reverse=reverse)
    res["token values"] = tokens
    #
    mask = diagnostics_df[col_name] != ""
    res["non-empty"] = int(sum(mask))
    res["non-empty [%]"] = hprint.perc(sum(mask), len(mask), only_perc=only_perc)
    #
    mask = diagnostics_df[col_name].isin(set(tokens))
    res["tokens"] = int(sum(mask))
    res["tokens [%]"] = hprint.perc(sum(mask), len(mask), only_perc=only_perc)
    # Compute the breakdown of the tokens.
    vals_df = diagnostics_df[mask]
    dict_ = vals_df.groupby(col_name).count().iloc[:, 0].to_dict()
    dict_ = dict(sorted(dict_.items(), key=lambda item: item[1], reverse=reverse))
    # hdbg.dassert_is_subset(dict_, email_verification_tokens)
    res["token counts"] = dict_
    res["token counts [%]"] = {
        k: hprint.perc(v, len(vals_df), only_perc=only_perc)
        for k, v in dict_.items()
    }
    if is_email_verification:
        res["token counts"]["!reachable"] = res["token counts"].get(
            "accept_all", 0
        ) + res["token counts"].get("valid", 0)
        res["token counts [%]"]["!reachable"] = hprint.perc(
            res["token counts"]["!reachable"],
            diagnostics_df.shape[0],
            only_perc=only_perc,
        )
    return res


def get_stats(diagnostics_df: pd.DataFrame) -> Dict[str, Any]:
    # email_verification_tokens = [
    #     '',
    #     'valid',
    #     'accept_all',
    #     'invalid',
    #     'risky',
    #     'unknown',
    #     '_missing_info_',
    #     '_nan_',
    #     '_error_'
    # ]
    res = {}
    res["total"] = diagnostics_df.shape[0]
    res["email"] = get_email_stats(
        diagnostics_df, "email", is_email_verification=False
    )
    res["hunterio.email"] = get_email_stats(
        diagnostics_df, "hunterio.email", is_email_verification=False
    )
    #
    srs = diagnostics_df["is_changed.email"] != False
    res["is_changed.email"] = hprint.perc(srs.sum(), len(srs))
    #
    res["email_verification"] = get_email_stats(
        diagnostics_df, "email_verification", is_email_verification=True
    )

    res["hunterio.email_verification"] = get_email_stats(
        diagnostics_df,
        "hunterio.email_verification",
        is_email_verification=True,
    )
    #
    srs = diagnostics_df["is_changed.email_verification"] != False
    res["is_changed.email_verification"] = hprint.perc(srs.sum(), len(srs))
    return res


def _extract_from_dict(dict_: Dict[str, Any], tuple_: Tuple) -> Any:
    """
    Extract a value from a nested dictionary using a tuple of keys.

    :param dict_: The dictionary to extract the value from.
    :param tuple_: A tuple of keys representing the path to the value.
    :return: The extracted value.
    """
    # Navigate the dictionary using the tuple of keys.
    dict_tmp = dict_
    for t in tuple_:
        hdbg.dassert_in(t, dict_tmp.keys())
        dict_tmp = dict_tmp[t]
    # Extract the last value.
    val = dict_tmp
    hdbg.dassert_isinstance(
        val, (str, int, float), "The last value needs to be a scalar"
    )
    return val


def extract_from_dict(
    dict_: Dict[str, Any],
    to_extract: List[Tuple],
) -> pd.Series:
    """
    Extract values from a nested dictionary and return them as a pandas Series.

    :param dict_: The dictionary to extract values from.
    :param to_extract: A list of tuples representing the paths to the values to extract.
    :return: A pandas Series containing the extracted values.
    ```
    to_extract = [
        ("email", "tokens [%]"),
        ("email", "non-empty [%]"),
        ("email", "valid [%]"),
    ]

      email/tokens [%] email/non-empty [%] email/valid [%]
    0            0.00%             100.00%         100.00%  100.00%
    ```
    """
    vals = {}
    for v in to_extract:
        val = _extract_from_dict(dict_, v)
        key = "/".join(v[1:])
        vals[key] = val
    srs = pd.Series(vals)
    return srs


def get_stats_df(stats_dict: pd.DataFrame) -> pd.DataFrame:
    """
    Generate a DataFrame containing statistics extracted from a nested
    dictionary.

    :param stats_dict: A DataFrame containing the statistics data.
    :return: A DataFrame with the extracted statistics.
    ```
                     ail/tokens [%]    invalid accept_all  valid unknown   _nan_  None _error_ disposable
    email                     0.00%        NaN        NaN    NaN     NaN    NaN    NaN     NaN        NaN
    hunterio.email            0.00%     50.93%     26.64%  8.72%   7.94%  4.98%  0.47%   0.16%      0.16%
    ```
    """

    def _build_email_df(
        col_name1: str, col_name2: str, prefix: str
    ) -> pd.DataFrame:
        to_extract = [
            (col_name1, "tokens [%]"),
            (col_name1, "non-empty [%]"),
        ]
        srs1 = extract_from_dict(stats_dict, to_extract)
        srs2 = pd.Series(stats_dict[col_name2]["token counts [%]"]).sort_index()
        srs = pd.concat([srs1, srs2])
        stats_df = srs.to_frame().T
        stats_df.index = [col_name1]
        return stats_df

    df1 = _build_email_df("email", "email_verification", "email")
    df2 = _build_email_df(
        "hunterio.email", "hunterio.email_verification", "email"
    )
    df = pd.concat([df1, df2])
    return df


def get_is_changed_stats(stats_df: pd.DataFrame) -> None:
    for col_name in stats_df.columns:
        if col_name.startswith("is_changed."):
            is_changed = stats_df[col_name]
            print(col_name, hprint.perc(is_changed.sum(), len(is_changed)))
