"""
Scrape AI company data from Growjo.com.

Extract relevant company data and save the extracted data to Google Sheets.
"""

import logging
import requests
import pandas as pd
import bs4 as fba
import selenium.webdriver as webdriver
import selenium.webdriver.chrome.service as service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import warnings
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import gspread
import helpers.hgoogle_file_api as hgofiapi

_LOG = logging.getLogger(__name__)
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1o07XnIArFdIjz0jTZuyPkldxBczhQhMywdF9Xe9kNmo/edit?usp=sharing"
SHEET_NAME = "AIcompany_list_growjodata"
SERVICE_ACCOUNT_FILE = "<path_to_your_personal_keyfile_here>"

def fetch_ai_growjo_data() -> pd.DataFrame:
    """
    Scrape AI company data from `Growjo`.

    Extract AI company details such as rank, name, location, funding, employees, revenue, and key personnel.

    :return: extracted AI company details
    """
    base_url = "https://growjo.com/industry/AI/{}"
    page = 1
    data = []
    try:
        driver = webdriver.Chrome(service=service.Service(ChromeDriverManager().install()))
        while True:
            current_url = base_url.format(page)
            _LOG.info(f"Fetching data from {current_url}...")
            driver.get(current_url)
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tbody.jss78 tr"))
                )
            except TimeoutException:
                _LOG.info("No more pages available or table not found. Exiting loop.")
                break
            soup = fba.BeautifulSoup(response.content, "html.parser")
            table_body = soup.select_one("tbody.jss78")
            if not table_body:
                _LOG.error(f"Table body not found on page {page}. Stopping extraction.")
                break
            rows = table_body.find_all("tr")
            _LOG.info(f"Found {len(rows)} rows on page {page}.")
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 11:
                    data.append({
                        "Rank": cols[0].get_text(strip=True),
                        "Name": cols[1].get_text(strip=True),
                        "City": cols[2].get_text(strip=True),
                        "State": cols[3].get_text(strip=True),
                        "Country": cols[4].get_text(strip=True),
                        "Funding": cols[5].get_text(strip=True),
                        "Employees": cols[6].get_text(strip=True),
                        "Revenue": cols[7].get_text(strip=True),
                        "Predictive Score": cols[8].get_text(strip=True),
                        "Person Name": cols[9].get_text(strip=True),
                        "Title": cols[10].get_text(strip=True),
                    })
            page += 1
        driver.quit()
        _LOG.info(f"Extraction complete: {len(data)} rows collected across multiple pages.")
        extracted_data = pd.DataFrame(data)
        return extracted_data
    except Exception as e:
        _LOG.error(f"An error occurred during data extraction: {e}")
        driver.quit()
        return pd.DataFrame()

if __name__ == "__main__":
    _LOG.info("Script execution started.")
    ai_companies = fetch_ai_growjo_data()    
    if not ai_companies.empty:
        _LOG.info("Uploading scraped data to Google Sheets...")
        creds = hgofiapi.get_credentials(service_key_path=SERVICE_ACCOUNT_FILE)
        hgofiapi.write_to_google_sheet(ai_companies, SHEET_NAME, credentials=creds)
        _LOG.info("Data successfully saved to Google Sheets.")
    else:
        _LOG.warning("No data extracted. Skipping Google Sheets upload.")
    _LOG.info("Script execution completed.")

