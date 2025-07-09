"""
Scrape Fortune 500 company data from `50pros.com`.

Extract the data and save the data to Google Sheets.
"""

import logging
import pandas as pd
import gspread
import bs4 as fba
import selenium.webdriver as webdriver
import selenium.webdriver.chrome.service as service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from google.oauth2.service_account import Credentials
import helpers.hgoogle_file_api as hgofiapi

_LOG = logging.getLogger(__name__)
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1v1H8JqQiomN3YdC5HI6lLsD97dDfFMzVLJXaDq_FFWw/edit?usp=sharing"
SHEET_NAME = "Company_list_target"
SERVICE_ACCOUNT_FILE = "<path_to_your_personal_keyfile_here>"

def fetch_fortune500_companies() -> pd.DataFrame:
    """
    Scrape Fortune 500 company data from `50pros.com`.

    Extracted information includes company name, website, revenue, CEO, etc.

    :return: extracted info about Fortune 500 companies
    """
    url = "https://www.50pros.com/fortune500"
    companies = []
    try:
        driver = webdriver.Chrome(service=service.Service(ChromeDriverManager().install()))
        driver.get(url)
        # Wait for iframe to load.
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe")))
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        _LOG.info(f"Found {len(iframes)} iframe(s) on the page.")
        # Switch to the second iframe containing the table.
        driver.switch_to.frame(iframes[1])
        _LOG.info("Switched to the iframe containing the company table.")
        # Wait for the table to load.
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "table")))
        # Parse table content.
        soup = fba.BeautifulSoup(response.content, "html.parser")
        driver.quit()
        # Extract rows from the table.
        rows = soup.select("table tbody tr")
        _LOG.info(f"Found {len(rows)} company rows in the table.")
        # Extract relevant details from each row.
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 8:
                companies.append({
                    "Name": cols[1].get_text(strip=True),
                    "Industry": cols[2].get_text(strip=True),
                    "City": cols[3].get_text(strip=True),
                    "Website": cols[5].get_text(strip=True),
                    "Employees": cols[6].get_text(strip=True),
                    "Revenue (Millions)": cols[7].get_text(strip=True),
                    "CEO": cols[11].get_text(strip=True),
                })
        _LOG.info(f"Extracted {len(companies)} Fortune 500 company records.")
        extracted_data = pd.DataFrame(companies)
        return extracted_data
    except Exception as e:
        _LOG.error(f"Error occurred while fetching Fortune 500 data: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    _LOG.info("Script execution started.")
    df = fetch_fortune500_companies()
    if not df.empty:
        _LOG.info("Uploading scraped data to Google Sheets.")
        creds = hgofiapi.get_credentials(service_key_path=SERVICE_ACCOUNT_FILE)
        hgofiapi.write_to_google_sheet(df, SHEET_NAME, credentials=creds)
        _LOG.info("Data successfully saved to Google Sheets.")
    else:
        _LOG.warning("No data extracted. Skipping Google Sheets upload.")
    _LOG.info("Script execution completed.")
