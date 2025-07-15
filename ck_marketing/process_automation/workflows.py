"""
Import as:

import ck_marketing.process_automation.workflows as cmprauwo
"""

import logging
import time
from typing import Optional

import gspread
import numpy as np
import pandas as pd
from google.oauth2.service_account import Credentials

import ck_marketing.dropcontact.drop_contact_api as cmddcoap
import helpers.hdbg as hdbg
import helpers.hgoogle_file_api as hgofiapi

_LOG = logging.getLogger(__name__)


# #############################################################################
# GoogleSheetsHelper
# #############################################################################


# TODO(gp): This doesn't belong here and also it's just part of the API, not
#  a class.
class GoogleSheetsHelper:

    def __init__(self, google_creds_path: str):
        """
        Initialize Google Sheets Helper with Google credentials.

        :param google_creds_path: The path to the Google credentials
            JSON file.
        """
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_file(
            google_creds_path, scopes=scope
        )
        self.google_account = gspread.authorize(creds)

    def create_new_sheet_from_df(
        self,
        df: pd.DataFrame,
        sheet_name: str,
        drive_folder_id: str,
        new_tab_name: str,
    ) -> str:
        """
        Create a new Google Sheet, rename the default tab, and write a
        DataFrame to it.

        :param sheet_name: name of the new Google Sheet.
        :param drive_folder_id: id of the Google Drive folder to create
            the sheet in.
        :param df: df to write to the Google Sheet.
        :param new_tab_name: name of new tab.
        :return: file_id.
        """
        # Create the Google Sheet and get the file ID.
        file_id = hgofiapi.create_empty_google_file(
            "sheet", sheet_name, drive_folder_id
        )
        hdbg.dassert_ne(
            file_id,
            0,
            "sheet_name='%s' in drive_folder_id='%s'",
            sheet_name,
            drive_folder_id,
        )
        # Open the Google Sheet by file ID.
        sheet = self.google_account.open_by_key(file_id)
        # Access the default tab (the first worksheet).
        default_worksheet = sheet.get_worksheet(0)
        # Rename the default tab to the desired name.
        default_worksheet.update_title(new_tab_name)
        # Write the DataFrame to the renamed default tab.
        self.write_results(file_id, df, new_tab_name)
        print(
            f"DataFrame written to Google Sheet '{new_tab_name}' in file ID '{file_id}' successfully."
        )
        return file_id

    def read_sheet(
        self, file_id: str, tab_name: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Read all records from the specified worksheet of the Google Sheets
        file.

        :param file_id: The ID of the Google Sheets file.
        :param tab_name: The name of the worksheet tab to read. If not
            provided, reads from the first worksheet.
        :return: DataFrame of records from the specified worksheet.
        """
        sheet = self.google_account.open_by_key(file_id)
        if tab_name:
            worksheet = sheet.worksheet(tab_name)
        else:
            worksheet = sheet.get_worksheet(0)
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        return df

    def write_results(
        self,
        file_id: str,
        results_df: pd.DataFrame,
        new_sheet_name: str = "hunter_results",
    ) -> None:
        """
        Write the results DataFrame to a new worksheet in the specified Google
        Sheets file.

        :param file_id: The ID of the Google Sheets file.
        :param results_df: The DataFrame containing the results to
            write.
        :param new_sheet_name: The name of the new worksheet where
            results will be saved.
        :return: None
        """
        sheet = self.google_account.open_by_key(file_id)
        try:
            new_worksheet = sheet.add_worksheet(
                title=new_sheet_name, rows="100", cols="20"
            )
        except gspread.exceptions.APIError:
            new_worksheet = sheet.worksheet(new_sheet_name)
        new_worksheet.clear()
        new_worksheet.update(
            "A1",
            [results_df.columns.values.tolist()] + results_df.values.tolist(),
        )
        _LOG.info(
            "Email extraction completed. Results saved in the new tab: %s",
            new_sheet_name,
        )


# Example usage:
# For bulk processing from Google Sheets using company name:
# process_records(api_key, google_creds_path, file_id, 'firstName', 'lastName', 'companyName', tab_name='Sheet1')

# For bulk processing from Google Sheets using company domain:
# process_records(api_key, google_creds_path, file_id, 'firstName', 'lastName', domain_col='domainName', use_domain=True, tab_name='Sheet1')

# For processing a single record using company name:
# single_record = {'first_name': 'Shaunak', 'last_name': 'Dhande', 'company': 'example'}
# process_records(api_key, google_creds_path, file_id, single_record=single_record)

# For processing a single record using company domain:
# single_record = {'first_name': 'Shaunak', 'last_name': 'Dhande', 'domain': 'example.com'}
# process_records(api_key, google_creds_path, file_id, single_record=single_record, use_domain=True)

# #############################################################################


def compute_email_statistics(
    results_df: pd.DataFrame, company_col_name: Optional[str]
) -> dict:
    """
    Compute statistics about email extraction results.

    :param results_df: dataFrame containing the email extraction
        results.
    :param company_col_name: name of company column.
    :return: statistics about emails found and not found, unique
        companies, and more.
    """
    total_records = len(results_df)
    emails_found = (
        results_df["hunter_extracted_email"]
        .apply(lambda x: pd.notna(x) and x != "")
        .sum()
    )
    emails_not_found = total_records - emails_found
    hdbg.dassert_in(company_col_name, results_df.columns)
    unique_companies = results_df[company_col_name].nunique()
    percentage_found = (emails_found / total_records) * 100
    top_companies = results_df[company_col_name].value_counts()
    _LOG.info("Total records processed: %d", total_records)
    _LOG.info("Emails found: %d", emails_found)
    _LOG.info("Emails not found: %d", emails_not_found)
    _LOG.info("Number of unique companies: %d", unique_companies)
    _LOG.info("Percentage of emails found: %.2f%%", percentage_found)
    _LOG.info("Companies by number of records:")
    _LOG.info("%s", top_companies)
    return {
        "total_records": total_records,
        "emails_found": emails_found,
        "emails_not_found": emails_not_found,
        "unique_companies": unique_companies,
        "percentage_found": percentage_found,
        "top_companies": top_companies.to_dict(),
    }


def process_records(
    api_key: str,
    google_creds_path: str,
    file_id: str,
    *,
    first_name_col: Optional[str] = None,
    last_name_col: Optional[str] = None,
    company_col: Optional[str] = None,
    domain_col: Optional[str] = None,
    single_record: Optional[dict] = None,
    use_domain: bool = False,
    tab_name: Optional[str] = None,
) -> Optional[pd.DataFrame]:
    """
    Process records from the Google Sheets file to find and append emails, or
    process a single record.

    This function reads records from a Google Sheets file or takes a
    single record, attempts to find emails using Hunter.io for each
    record, and writes the results back to a new worksheet in the same
    Google Sheets file. Give the column names in gsheet as parameters if
    you want to use bulk email extraction. For single email extraction,
    provide name and company strings. You can use this function with
    company name as well as company domain. Look at the example given at
    he end.

    :param api_key: api key for accessing Hunter.io services.
    :param google_creds_path: path to the Google credentials JSON
        file.
    :param file_id: id of the Google Sheets file containing the
        records.
    :param first_name_col: column name for first names (required for
        bulk processing).
    :param last_name_col: column name for last names (required for
        bulk processing).
    :param company_col: column name for company names (required for
        bulk processing).
    :param domain_col: column name for company domains (required for
        bulk processing if using domains).
    :param single_record: 'first_name', 'last_name',
        and 'company' or 'domain' keys for single record processing.
    :param use_domain: flag to use company domain instead of
        company name for email extraction.
    :param tab_name: name of the worksheet tab to read. If not
        provided, reads from the first worksheet.
    :return:
        - single record processing: found email address if successful.
        - bulk processing: dataFrame with results if emails are found.
        - Returns `None` in the following cases:
            - no data is found in the specified Google Sheets file.
            - no emails are found or an error occurs during email extraction.
            - `single_record` is not provided and the `use_domain` flag is set to `False` or `True`, but the relevant columns are not provided or are incorrect.
    """
    gs_helper = GoogleSheetsHelper(google_creds_path)
    hunter = HunterIO(api_key)
    if single_record:
        _LOG.info("Processing a single record")
        if use_domain:
            email = hunter.find_single_email_by_domain(
                single_record["first_name"],
                single_record["last_name"],
                single_record["domain"],
            )
        else:
            email = hunter.find_single_email(
                single_record["first_name"],
                single_record["last_name"],
                single_record["company"],
            )
        _LOG.info("Found email: %s", email)
        return email
    _LOG.info("Starting process to read records and find emails")
    df = gs_helper.read_sheet(file_id, tab_name)
    if df.empty:
        _LOG.warning("No data found in the Google Sheets file.")
    if use_domain:
        _LOG.info("Finding bulk emails using company domain")
        results_df = hunter.find_bulk_emails_by_domain(
            df, first_name_col, last_name_col, domain_col
        )
    else:
        _LOG.info("Finding bulk emails using company name")
        results_df = hunter.find_bulk_emails(
            df, first_name_col, last_name_col, company_col
        )
    if not results_df.empty:
        results_df.replace([np.inf, -np.inf, np.nan], "", inplace=True)
        _LOG.info("Writing results to Google Sheets")
        gs_helper.write_results(file_id, results_df, "hunter_results")
        stats = compute_email_statistics(results_df, company_col)
        _LOG.info("Process completed successfully. Statistics: %s", stats)
        return results_df
    _LOG.warning("No emails found or an error occurred during email extraction")
    raise ValueError(
        "No emails found or an error occurred during email extraction"
    )


def hunter_drop_emails(
    first_name_col: str,
    last_name_col: str,
    company_col: str,
    tab_name: str,
    hunter_api_key: str,
    google_creds_path: str,
    file_id: str,
    dropcontact_api_key: str,
) -> pd.DataFrame:
    """
    Extract all emails from HunterIO and DropContact.

    First HunterIO is called to get emails. Then dropcontact tries to
    find the emails not found with HunterIO. The function writes
    three tabs in the provided gogle sheet.`hunter_results`,
    `hunter_drop_emails` and `all_emails`. We also get statistics
    regarding the extractions from different platforms.

    :param first_name_col: name of column containing first names.
    :param last_name_col: name of column containing last names.
    :param company_col: name of column containing company names.
    :param first_name_col: name ofcolumn containing first names.
    :param tab_name: name of tab to read the sheet from.
    :param hunter_api_key: api key of HunterIO.
    :param google_creds_path: path to google creds.
    :param file_id: id of gsheet.
    :param dropcontact_api_key: api key of dropcontact.
    :return: dataframe with all extracted emails.
    """
    df_drop = process_records(
        api_key=hunter_api_key,
        google_creds_path=google_creds_path,
        file_id=file_id,
        first_name_col=first_name_col,
        last_name_col=last_name_col,
        company_col=company_col,
        tab_name=tab_name,
    )
    # wait for sheet write activity.
    time.sleep(5)
    missing_email_df = df_drop[
        df_drop["hunter_extracted_email"].isna()
        | (df_drop["hunter_extracted_email"] == "")
    ]
    # Prepare data for DropContact.
    first_names = missing_email_df[first_name_col].tolist()
    last_names = missing_email_df[last_name_col].tolist()
    company_names = missing_email_df[company_col].tolist()
    # Get emails from DropContact.
    dropcontact_results_df = cmddcoap.get_email_from_dropcontact(
        first_names, last_names, company_names, dropcontact_api_key
    )
    # Replace special float values with NaN.
    df_drop.replace([np.inf, -np.inf], np.nan, inplace=True)
    dropcontact_results_df.replace([np.inf, -np.inf], np.nan, inplace=True)
    # Rename columns in dropcontact_results_df to match df_drop.
    dropcontact_results_df.rename(
        columns={"first name": "firstName", "last name": "lastName"},
        inplace=True,
    )
    # Merge the dataframes on 'firstNames' and 'lastName', keeping only the 'email' column from dropcontact_results_df.
    merged_df = pd.merge(
        df_drop,
        dropcontact_results_df[["firstName", "lastName", "email"]],
        on=["firstName", "lastName"],
        how="left",
    )
    # Rename the 'email' column to 'dropcontact_mail'.
    merged_df.rename(columns={"email": "dropcontact_mail"}, inplace=True)
    # Count the non-null values in the 'dropcontact_mail' column.
    email_count = merged_df[
        merged_df["dropcontact_mail"].notna()
        & (merged_df["dropcontact_mail"] != "")
    ]["dropcontact_mail"].count()
    _LOG.info("Number of emails found : %d", email_count)
    _LOG.info(
        "Number of profile emails hunter could not find %d:",
        len(missing_email_df),
    )
    merged_df.replace({np.nan: "", np.inf: "", -np.inf: ""}, inplace=True)
    gs_helper = GoogleSheetsHelper(google_creds_path)
    gs_helper.write_results(file_id, merged_df, "hunter_drop_emails")
    time.sleep(10)
    merged_df["all_emails"] = (
        merged_df["hunter_extracted_email"]
        .fillna("")
        .replace("", pd.NA)
        .combine_first(merged_df["dropcontact_mail"])
    )
    merged_df.replace({np.nan: "", np.inf: "", -np.inf: ""}, inplace=True)
    gs_helper.write_results(file_id, merged_df, "all_emails")
    return merged_df
