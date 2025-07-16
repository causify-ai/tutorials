"""
Scrape AI company data from `Datamation.com`.

Extract the data and save the data to Google Sheets.
"""

import requests
import pandas as pd
import bs4 as fba
import re
import logging
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from typing import List
import helpers.hgoogle_file_api as hgofiapi

_LOG = logging.getLogger(__name__)
JSON_KEYFILE = "<path_to_your_personal_keyfile_here>"
SHEET_NAME = "Company_list_target_AIcompanies"

def scrape_ai_companies() -> pd.DataFrame:
    """
    Scrape AI company data from `Datamation.com`.

    Extract company names, headquarters, annual revenue, and Glassdoor scores.

    :return: extracted details about AI companies
    """
    url = "https://www.datamation.com/featured/ai-companies/"
    response = requests.get(url)
    soup = fba.BeautifulSoup(response.content, "html.parser")
    companies = []
    for company in soup.find_all("h3"):
        company_name = company.text.strip()
        details_section = company.find_next_sibling()
        paragraphs = []
        while details_section and details_section.name == "p":
            paragraphs.append(details_section.text.strip())
            details_section = details_section.find_next_sibling()
        headquarters, revenue, glassdoor_score = "N/A", "N/A", "N/A"
        # Reset the flag for each company.
        found_match = False
        for text in paragraphs:
            if "Headquarters:" in text:
                headquarters = text.split("Headquarters:", maxsplit=1)[-1].strip()
                found_match = True
            if "Annual Revenue:" in text:
                revenue = text.split("Annual Revenue:", maxsplit=1)[-1].strip()
                found_match = True
            if "Glassdoor Score:" in text:
                glassdoor_score = text.split("Glassdoor Score:", maxsplit=1)[-1].strip()
                found_match = True
        if found_match:
            companies.append({
                "Company Name": company_name,
                "Headquarters": headquarters,
                "Annual Revenue": revenue,
                "Glassdoor Score": glassdoor_score
            })
        else:
            _LOG.debug("Skipping company due to missing data: %s", company_name)
    _LOG.info("Scraped %d AI companies.", len(companies))
    ai_companies_data = pd.DataFrame(companies)
    return ai_companies_data

if __name__ == "__main__":
    _LOG.info("Script execution started.")
    ai_companies_df = scrape_ai_companies()
    if not ai_companies_df.empty:
        _LOG.info("Uploading scraped data to Google Sheets...")
        creds = hgofiapi.get_credentials(service_key_path=JSON_KEYFILE)
        hgofiapi.write_to_google_sheet(ai_companies_df, SHEET_NAME, credentials=creds)
        _LOG.info("Data successfully saved to Google Sheets.")
    else:
        _LOG.warning("No data extracted. Skipping Google Sheets upload.")
    _LOG.info("Script execution completed.")