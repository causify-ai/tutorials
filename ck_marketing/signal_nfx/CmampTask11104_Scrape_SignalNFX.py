# %%
import csv
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# %%
# Initialize the WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=options)
# Navigate to the website
url = "https://signal.nfx.com/investor-lists/top-ai-seed-investors"
driver.get(url)
# Wait for the page to load
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))


# %%
def click_load_more():
    num = 0
    while True:
        try:
            load_more_button = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//button[contains(text(), 'LOAD MORE INVESTORS')]",
                    )
                )
            )
            load_more_button.click()
            time.sleep(15)
            num += 1
            print(f"Clicked 'LOAD MORE INVESTORS' button {num} times.")
        except Exception as e:
            print(f"Error while clicking 'LOAD MORE INVESTORS': {e}")
            break


click_load_more()
# # Extract data from the page
# Extract the content of the "vc-search-card-grid" class


# %%
print("hello")

# %%
try:
    print("entered")
    container = driver.find_element(By.CSS_SELECTOR, "div.vc-search-card-grid")
    print("Now turning to html")
    container_html = container.get_attribute(
        "outerHTML"
    )  # Get the raw HTML of the container
except Exception as e:
    print(f"Error occurred while extracting container: {e}")
    container_html = ""

# %%
soup = BeautifulSoup(container_html, "html.parser")


# %%
# soup

# %%
elements = soup.find_all("div", class_="vc-search-card mb2")

# %%
data = []
for i in elements:
    try:
        info = i.find("div", class_="flex justify-between")
        name_info = info.find_all("a") if info else []
        fullName = name_info[0].text.strip() if len(name_info) > 0 else "N/A"
        company_name = name_info[1].text.strip() if len(name_info) > 1 else "N/A"
    except Exception as e:
        fullName = ""
        company_name = ""
        print(f"Error extracting name or company: {e}")
    # Extracting Position
    try:
        position = info.find_all("span")[1].text.strip()
    except Exception:
        position = ""
    # Extracting Money Info
    try:
        money_info = i.find("div", class_="mt2 flex flex-column")
        if money_info:
            sec = money_info.find_all("div")
            sweet_spot = sec[0].text.strip()
            range_info = sec[1].text.strip()
        else:
            sweet_spot = ""
            range_info = ""
    except Exception:
        sweet_spot = ""
        range_info = ""
    data.append([fullName, company_name, position, sweet_spot, range_info])


# %%
len(data)

# %%
# Define CSV file name
csv_file = "signalNFX_output.csv"
# Write data to CSV
with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(
        ["fullName", "companyName", "companyPosition", "sweetSpot", "rangePrice"]
    )
    writer.writerows(data)

print(f"CSV file '{csv_file}' has been created.")

# %%
