# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# CONTENTS:
#

# %%
import time

import pandas as pd
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# %%
# Refer 'docs/work_tools/selenium.how_to_guide.md' for installation and other info

# %%
# Define the path to the ChromeDriver executable
chrome_driver_path = "helpers/selenium_creds/chromedriver"

# %%
# Setup Selenium ChromeDriver with specific options
chrome_options = Options()
# Disable sandboxing for security testing
chrome_options.add_argument("--no-sandbox")
# Overcome limited resource problems
chrome_options.add_argument("--disable-dev-shm-usage")
# Set the browser window size to 1920x1080
chrome_options.add_argument("--window-size=1920,1080")
# Initialize the Chrome WebDriver with the specified options and service path
driver = webdriver.Chrome(
    service=Service(chrome_driver_path), options=chrome_options
)

# %%
# URLs and login credentials
login_url = "https://connect.money2020.com/money2020usa2024/app/home/network/list/82807?page=1&sort=name"
username = os.getenv("username")
password = os.getenv("password")

# %%
# Open the login page
driver.get(login_url)

# %%
# Fill the login form
button = driver.find_element(
    By.CSS_SELECTOR, "[data-test='loginSSOButton']"
).click()

# %%
username_input = driver.find_element(By.NAME, "username")
password_input = driver.find_element(By.NAME, "password")
username_input.send_keys(username)
password_input.send_keys(password)
login_button = driver.find_element(By.NAME, "action")
login_button.click()

# %%
driver.get(login_url)

# %%
while True:
    try:
        # Wait for the "Load More" button to be clickable
        load_more_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[data-test='searchLoadMoreButton']")
            )
        )
        # Click the button using JavaScript
        driver.execute_script("arguments[0].click();", load_more_button)
        # Wait a bit to let new data load before the next iteration
        time.sleep(2)
    except Exception as e:
        # Break the loop if the button is no longer found or clickable
        print("No more 'Load More' button found or an error occurred:", e)
        break

# Proceed with further actions after all data is loaded
print("All data loaded.")

# %%
element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "div.is-flex.flex-column"))
)

# Once found, get the innerHTML or text of the element
data = element.get_attribute("innerHTML")

# %%
soup = bs(data, "html.parser")

# %%
target = soup.find("div", class_="is-flex flex-column gap")

# %%
target_2 = target.find_all("app-profile-card")

# %%
results = []

for i in target_2:
    name_elem = i.find("a", class_="link-primary")
    title_elem = i.find("p", class_="text")
    location_elem = i.find_all("small")
    name = name_elem.get_text(strip=True) if name_elem else "None"
    title = title_elem.get_text(strip=True) if title_elem else "None"
    if len(location_elem) == 3:
        location = location_elem[1].get_text(strip=True)
    elif len(location_elem) > 3:
        location = location_elem[3].get_text(strip=True)
    elif len(location_elem) < 3:
        location = "None"
    if "Error" in location or "•" in location:
        location = "None"
    job_elements = i.find_all("p", class_="text")
    job_title_full = (
        job_elements[1].get_text(strip=True) if len(job_elements) > 1 else "None"
    )
    if " at " in job_title_full:
        job_title, company_name = job_title_full.split(" at ", 1)
    else:
        job_title = job_title_full
        company_name = "None"
    results.append(
        {
            "fullname": name,
            "location": location,
            "jobTitle": job_title,
            "companyName": company_name.strip(),
        }
    )
    print("a row doneeee")
df = pd.DataFrame(results)


# %%
driver.quit()

# %%
df.tail(4)

# %%
df.to_csv("money20/20_Attandees.csv", index=False)
