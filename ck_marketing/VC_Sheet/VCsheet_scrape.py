# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.15.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
# Shaunak Dhande

# %%
# !pip install requests --upgrade --user
# !pip install selenium beautifulsoup4 pandas openpyxl --user
# !pip install webdriver_manager --user


# %%
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# %%
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# URL to be loaded
url = "https://www.vcsheet.com/investors?stages=seed%7Cseries-a&sectors=fintech%7Cai-devtools%7Cgeneralist%7Cproptech&geographies=usa"
driver.get(url)

# Scroll to the end of the page to load all dynamic content
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  # wait for new content to load
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height


page_source = driver.page_source
driver.quit()

soup = BeautifulSoup(page_source, "html.parser")


# %%
soup.text

# %%
investors_soup = soup.find_all(
    "div", class_="list-item vert-list less-spacing w-dyn-item"
)
base_url = "https://www.vcsheet.com"
all_investor_links = []
for i in investors_soup:
    investor_link = i.find("a", class_="full-click center w-inline-block")["href"]
    investor_complete_link = base_url + investor_link
    all_investor_links.append(investor_complete_link)


# %%
print(all_investor_links)

# %%
investors_data = []
for link in all_investor_links:
    response = requests.get(link)
    investor_soup = BeautifulSoup(response.content, "html.parser")
    name = (
        investor_soup.find("h1").get_text(strip=True)
        if investor_soup.find("h1")
        else ""
    )
    title = (
        investor_soup.find("div", class_="align-row wrapping").get_text(
            strip=True
        )
        if investor_soup.find("div", class_="align-row wrapping")
        else ""
    )
    email = (
        investor_soup.find(
            "a", class_="list-card contact-card email w-inline-block"
        )["href"]
        if investor_soup.find("a", "list-card contact-card email w-inline-block")
        else ""
    )
    email = email.replace("mailto:", "")
    linkedin = (
        investor_soup.find(
            "a", class_="list-card contact-card linkedin w-inline-block"
        )["href"]
        if investor_soup.find(
            "a", "list-card contact-card linkedin w-inline-block"
        )
        else ""
    )
    print(name)
    print(title)
    print(email)
    print(linkedin)
    print(link)
    investors_data.append(
        {
            "Name": name,
            "Title": title,
            "Email": email,
            "LinkedIn": linkedin,
            "Website": link,
        }
    )


# %%
# Convert the list to a DataFrame
df = pd.DataFrame(investors_data)

# Save to CSV and XLSX
df.to_excel("VCSheet_Query1.xlsx", index=False)

# Display the DataFrame
df.head()

# %%
