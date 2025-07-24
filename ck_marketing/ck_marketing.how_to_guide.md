<!-- toc -->

- [Introduction](#introduction)
- [Abbreviations](#abbreviations)
- [Workflow](#workflow)
- [Main Flow](#main-flow)
- [Problems / Guidelines:](#problems--guidelines)
- [Conventions](#conventions)
- [Extracting Marketing Data](#extracting-marketing-data)
- [Tracxn](#tracxn)
  * [Introduction](#introduction-1)
  * [Code](#code)
  * [Workflow](#workflow-1)
    + [Company Flow](#company-flow)
    + [People Flow](#people-flow)
- [Phantombuster](#phantombuster)
  * [Introduction](#introduction-2)
  * [Code](#code-1)
  * [Workflow](#workflow-2)
- [Hunterio](#hunterio)
  * [Introduction](#introduction-3)
  * [Code](#code-2)
  * [Workflow](#workflow-3)
- [Dropcontact](#dropcontact)
  * [Introduction](#introduction-4)
  * [Code](#code-3)
  * [Workflows](#workflows)
- [Signal NFX](#signal-nfx)
  * [Introduction](#introduction-5)
  * [Code](#code-4)
  * [Workflows](#workflows-1)
- [Process Automation](#process-automation)
  * [Introduction](#introduction-6)
  * [Code](#code-5)
  * [Workflow](#workflow-4)
- [Folkapp](#folkapp)
  * [Introduction](#introduction-7)
  * [Code](#code-6)
  * [Workflow](#workflow-5)
- [Money2020](#money2020)
  * [Introduction](#introduction-8)
  * [Code](#code-7)
  * [Workflow](#workflow-6)
- [Growjo](#growjo)
  * [Introduction](#introduction-9)
  * [Code](#code-8)
  * [Workflow](#workflow-7)
- [50Pros.Com](#50proscom)
  * [Introduction](#introduction-10)
  * [Code](#code-9)
  * [Workflows](#workflows-2)
- [Datamation](#datamation)
  * [Introduction](#introduction-11)
  * [Code](#code-10)
  * [Workflow](#workflow-8)

<!-- tocstop -->

# Introduction

- We automated the process of running cold outreach campaign using some of our
  KaizenFlow components
- We have built a master Jupyter notebook with the entire flow that we can use
  to go from LinkedIn / Sales Navigator query to a Google Sheet with the
  information for an outreach (names, emails, positions)
  - `ck_marketing/process_automation/Master.cold_outreach.ipynb`

- For specific tasks, there is a single notebook with only what's needed for
  that task, which is a particular version of the master notebook
- We stitched several services E.g., LinkedIn scraping, PhantomBuster, a little
  of ML, hunter.io, dropcontact, YAMM At some point we should also add a CRM to
  the flow

# Abbreviations

- **SN** = SalesNavigator
- **PB** = PhantomBuster

# Workflow

- Come up with a list of sectors to target and decision makers
  - E.g., David's
    [TO DELETE Kaizen ICP](https://docs.google.com/document/d/1IFrrUiA7vciZzkQU9-mhMM0-PfTdTxRCeIkw1yYLl4g/edit?tab=t.0#heading=h.i63h21soi3hx)
- Come up with lists of target companies for each sector
  - E.g.,
    [!Company lists](https://docs.google.com/spreadsheets/d/10_znRzH4jV54bCeTWYqwTkt9fLJIgpfw/edit?gid=40678431#gid=40678431)
- Create a SalesNavigator (SN) query for the company with the decision makers
  - [https://www.linkedin.com/sales/home](https://www.linkedin.com/sales/home)
  - We have templates of SN queries that we can customize
    - E.g., "decision makers for a VC firm", "decision makers for a consulting
      firm"
- We can analyze a SN query to the list of query to process
  - E.g., Cold outreach - LIN searches
  - Use PhantomBuster to extract the candidates (manually at first and then
    using API)
    - [https://phantombuster.com/8472730339660855/phantoms](https://phantombuster.com/8472730339660855/phantoms)
    - E.g., [VC leads - Shaunak]()
    - E.g., Flutter_decision_makers
- The structure of the notebook pipeline is
  - Given a sector and a company
  - Generate the SN query automatically
  - The output is in VC leads - Shaunak
  - Run PB (only export profiles) -> linked in gsheet
    - E.g.,
  - Read Gsheet "export_search"
  - Filter by certain criteria (e.g., "remove lawyers from the list")
    - Goal is to keep only the decision makers
    - We have a set of functions in the lib that help doing filtering
    - Every company is different and so we pick the functions that are best and
      we customize it
  - Save in Gsheet tab "export_search.filtered"
  - Extract emails
    - Use hunter.io
    - Use Dropcontact (already implemented)
  - Save in Gsheet tab "email"
  - Filter/remove dead emails
    - It's totally ok to use hunter.io
    - Neverbounce
  - Save Gsheet as "email.cleaned" tab
    - We want to get to 20-50 people per company
  - Create customized email
  - Run Yamm campaign

# Main Flow

- Load Contact data
  - Read all the scraped Gsheet (e.g., FolkApp, VCSheet, ...)
  - Read LIn connections from people LIn accounts
  - Read mixed data sources
    - HedgeFundList
    - Super networking spreadsheet
  - Each data loader
    - Reads data from a different format
    - Maps data from original schema to Contact schema
    - Normalizes data into the Contact schema
  - Concat all data
    - Merge all the data
    - Clean up
    - Compute stats
    - Serialize it as a Gsheet
- Process Contact data
  - Clean up first / last names
  - Enrich with Hunters.io data
    - Query data from Hunters.io
    - Merge the data back
    - We should do the emails too
  - Validate emails
    - Use Hunters.io to check that all emails are valid
  - Assign a category to leads
    - E.g., investor, VC, customer
- YAMM pipeline
  - We read the data from previous YAMM campaigns Update the state of each
    contact Extract YAMM / LIn campaign

# Problems / Guidelines:

The Contact schema is often changing

- E.g., we find out that we want to track some new information that we
  originally ignored
- Solutions
  - We need to be able to re-run everything from the original data

Some fields are separated in some cases, e.g.,

- "series type = {series_seed, series_A, ...}"
- "geography"
- Solutions
  - Have multiple tables (not sure it's worth it)
  - Use key-value db
  - Make it simple to recreate the dataset once we change something (this seems
    the best)

Not all the original data sets have all the info

- Solutions
  - We can encode multiple values in a single cell
  - Just make the schema large and have easy ways to slice the data (best)

Sometimes one wants to open a pipeline stage and look into it, other times you
want to run it as an atomic block

- Solution:
  - Have multiple notebooks with different level of details
  - Serialize data to exchange data
  - Have multiple functions back-to-back
  - Put all the functions in a single function once it's debugged
  - Have switches to run in verbose mode or not

The notebook is a pipeline of pipelines

- The main pipeline has several stages
  - E.g., Master_process_contacts
- Each pipeline stage has several stages
  - Some notebooks are used to analyze a pipeline, e.g.,
    - Process_hedge_fund_list
    - GP_LIn_contacts

Add sanity checks to make sure the data is well-formed or abort

Each transform can add debug information

- E.g., stats
- Mark the changed rows as `is_changed`
- Have a function to debug the data

There is a config controlling all the stages

There is a stage to serialize / deserialize if serialize:

- Save
- Assert 0 else:
- Load

Each function should be idempotent

- Make a copy, modify, and return the data
- It's ok to keep assigning stages in sequence
```bash
  >  Contact_df = f1(contact_df)
  >  Contact_df = f2(contact_df)
 ```
- Once in a while we want to assign to a different var to split the computation
```bash
  > Contact_df = f1(contact_df)
  > Contact_df2 = f1(contact_df)
```
  - It's better in this case to use a meaningful name `cleaned_contact_df`,
    rather than `contact_df2`

The expensive / slow phases are cached, either as Gsheet or through the caching
code

# Conventions

- Each SN search corresponds to a single Gsheet with multiple tabs for each step
  of the process
- Once the tab is complete we copy into a Gsheet corresponding to each vertical,
  e.g., "Cold outreach - VC"
  - The format/schema of each tab should be always the same so we can append
    data
  - We also add extra columns to the gsheet to represent the fact that a lead
    was acted upon, etc
  - In other words, the tab for VCs is called "VC - DB"
- Every time we do a YAMM campaign we
  - Add another tab tagged with the date
  - Copy-paste a set of rows from the "DB" tab

# Extracting Marketing Data

- The goal is to extract detailed "marketing" information (e.g., about
  investors, employees, customers, etc) from some public/easy to collect
  databases

- The services we use are:
  - LinkedIn/SalesNavigator
    - Search for people according to certain criteria (e.g., job description,
      working at a certain company)
    - Search for groups
  - Tracxn
    - Get information about a company
  - Dropcontact
    - Find / verify emails for people
  - Hunter.io
    - Find / verify emails for people
  - Signal NFX
    - Find information for investors
  - PhantomBuster
    - Extract information from LinkedIn/SalesNavigator
    - Send messages on LinkedIn
    - Autoconnect to people on LinkedIn
  - Yamm
    - GoogleSheet plugin to automate sending and tracking emails
  - Docsend
    - Share and track documentation
  - FolkApp
    - Scrape VC profile data from Folk.app
    - Exports results to CSV for further processing
  - Money2020
    - Extract attendee data from the Money2020 event API
    - Handle pagination with retry logic to avoid rate limits
    - Save data to CSV and enriches it with contact details
  - 50pros.com
    - Scrape Fortune 500 company data from 50pros.com
    - Extract company name, industry, location, revenue, CEO, and more
    - Saves extracted data to Google Sheets
  - Growjo
    - Scrape AI company growth data from Growjo.com
    - Extract rank, funding, employee count, revenue, and key personnel
    - Save data to Google Sheets
  - Datamation
    - Scrape AI company details from Datamation.com
    - Extract company name, headquarters, annual revenue, and Glassdoor scores
    - Save data to Google Sheets
  - VC Google Sheets
    - Manually curated and validated lists of venture capitalists
    - Maintained internally and integrated with other data pipelines

# Tracxn

## Introduction

- Tracxn website is at [https://tracxn.com](https://tracxn.com)
- E.g., searching for VC firms that invested in Series seed and A of AI
  companies
  [https://tracxn.com/a/s/query/t/investors/t/activeinestorsvc/table?h=f7aa3582c404433be03c12f1df4f0e463c78bc6398c81a45a403ac8703e0ba0a&s=sort%3DinvestmentCount%7Corder%3DDESC](https://tracxn.com/a/s/query/t/investors/t/activeinestorsvc/table?h=f7aa3582c404433be03c12f1df4f0e463c78bc6398c81a45a403ac8703e0ba0a&s=sort%3DinvestmentCount%7Corder%3DDESC)
- The result is a set of links to company pages like
  [https://tracxn.com/a/companies/srAiTt8Aevx0dkPbmrFdUVl21azd7Gx7AOT8J4fO1Zs/ycombinator.com/people/currentteam](https://tracxn.com/a/companies/srAiTt8Aevx0dkPbmrFdUVl21azd7Gx7AOT8J4fO1Zs/ycombinator.com/people/currentteam)
  - This page contains information about people working at that company with
    information about LinkedIn and emails

## Code

- The module is located at `ck_marketing/tracxn`
- Example notebooks are at:
  - `ck_marketing/tracxn/notebooks/SorrTask601_Extract_VCs_from_Tra_search_mhtml.ipynb`
  - `ck_marketing/tracxn/notebooks/SorrTask601_Extract_people_from_Tra_company_html.ipynb`

## Workflow

### Company Flow

- Go to a Tracxn VCs search result page
- Use the browser's `Save As` button to download the webpage as a
  `Web page, single file`.
- If you see the downloaded file format is `.mht` or `.mhtml`, you can process
  forward. Otherwise, you won't be able to bypass the check layer from the
  website.
  - The MIME HTML file containing a table of VC company names
- Call `get_VCs_from_mhtml()` method with the `.mhtml` file path to extract the
  result as a Pandas dataframe containing the VC names and its information:
  ```txt
  Investor Name                                              Jiangmen Ventures
  Score                                                                      2
  #Rounds                                                                   10
  Portfolio Companies                    DMAI;Bito Robotics;DEEP INFORMATICS++
  Investor Location                                                   Chaoyang
  Stages of Entry                                    Series A (8);Seed (6)[+2]
  Sectors of Investment        Enterprise Applications (10);High Tech (9)[+16]
  Locations of Investment                     China (27);United States (4)[+3]
  Company URL                https://tracxn.com/a/companies/3pfRjux26cdu4Aq...
  ```
- Save the returned dataframe to whatever format preferred

An example of this flow is
`ck_marketing/tracxn/notebooks/SorrTask601_Extract_VCs_from_Tra_search_mhtml.ipynb`

The inputs are in
[https://drive.google.com/drive/u/2/folders/1nT5CYuFWLOxb10ONw7yjfzyobc9VM90-](https://drive.google.com/drive/u/2/folders/1nT5CYuFWLOxb10ONw7yjfzyobc9VM90-)
The outputs are in
[https://drive.google.com/drive/u/2/folders/1MfTeNHR7sxex_rSpyp54HeJsxtLjKqy3](https://drive.google.com/drive/u/2/folders/1MfTeNHR7sxex_rSpyp54HeJsxtLjKqy3)

### People Flow

- Same flow as above but it converts a page like
  [https://tracxn.com/a/d/investor/srAiTt8Aevx0dkPbmrFdUVl21azd7Gx7AOT8J4fO1Zs/ycombinator.com/people/currentteam](https://tracxn.com/a/d/investor/srAiTt8Aevx0dkPbmrFdUVl21azd7Gx7AOT8J4fO1Zs/ycombinator.com/people/currentteam)
  into a dataframe like:
  ```txt
  Name                                                 Matanya Horowitz
  LinkedIn Profile    https://linkedin.com/in/matanya-horowitz-87805519
  ```

# Phantombuster

## Introduction

- PhantomBuster website is at
  [https://phantombuster.com/](https://phantombuster.com/)
- PhantomBuster is an automation tool for extracting and processing web data The
  script provided at `ck_marketing/linkedin/phantombuster_api.py` demonstrates
  how to interact with the PhantomBuster API using Python, enabling you to
  manage and retrieve data from your PhantomBuster agents.

## Code

- The module is located at `ck_marketing/linkedin/phantombuster_api.py`
- Example notebook is at:
  - `ck_marketing/process_automation/Master.cold_outreach.ipynb`

## Workflow

1. Initialization

- Phantom Class: Initialize the class with the provided API key to set up
  necessary headers for API requests.

2. Agent Management

- Get All Agents: Retrieve a list of all agents associated with the account.
- Get Agent Name: Fetch the name of a specific agent by its ID.
- Launch Agent: Start a specific agent using its ID.
- Fetch Agent Results: Continuously poll the API until the agent finishes
  running and fetch the results.

3. Data Handling

- Launch and Get DataFrame: Launch an agent, wait for it to run, fetch results,
  and load the data into a pandas DataFrame.
- Get CSV URL: Extract the CSV URL from the agent's output text.
- Download CSV: Download a CSV file from a given URL and load it into a pandas
  DataFrame.

4. Phantom Data Retrieval

- Get All Phantoms: Retrieve all names and IDs of Phantoms and return as a
  DataFrame.
- Download Result CSV by Phantom ID: Download the result CSV file for a specific
  Phantom by its ID.

5. Private Functions

- `_get_result_csv_by_phantom_id`: Fetch the result CSV URL for a given Phantom
  ID.
- `_get_all_containers_id_by_phantom_id`: Retrieve all container IDs for a given
  Phantom ID.
- `_get_result_csv_by_container_id`: Fetch the result CSV URL for a given
  container ID.
- `_get_phantom_data`: Get all Phantom information.
- `_get_api_response`: Make an API request and return the response.

# Hunterio

## Introduction

- HunterIO is a service for finding and verifying email addresses using names
  and company information. This guide provides an overview of the `HunterIO`
  class and its associated methods for interacting with the Hunter.io API and
  Google Sheets.

## Code

- The module is located at `ck_marketing/hunterio/hunter_api.py`
- Example notebook is at:
  - `ck_marketing/process_automation/Master.cold_outreach.ipynb`

## Workflow

1. Initialization:

- Create an instance of the HunterIO class with an API key.

2. Email Finding:

- By Company: Use `find_email` to find an email address using the first name,
  last name, and company name.
- By Domain: Use `find_email_by_domain` to find an email address using the first
  name, last name, and company domain.

3. Bulk Email Extraction:

- By Company: Use `find_bulk_emails` to find email addresses for each row in a
  DataFrame using the company name.
- By Domain: Use `find_bulk_emails_by_domain` to find email addresses for each
  row in a DataFrame using the company domain.

4. Single Email Extraction:

- By Company: Use `find_single_email` to find an email address for a single
  person using the company name.
- By Domain: Use `find_single_email_by_domain` to find an email address for a
  single person using the company domain.

5. Email Verification:

- Use `verify_email` to verify the validity of an email address and
  `verify_emails` to verify emails in bulk.

6. Google Sheets Interaction:

- Read Data: Use `read_sheet` to read data from a Google Sheets file.
- Write Data: Use `write_results` to write data to a Google Sheets file.
- Create New Sheet: Use `create_new_sheet_from_df` to create a new Google Sheets
  file from a DataFrame.

7. Email Statistics:

- Use `compute_email_statistics` to compute statistics about the email
  extraction results.

8. Record Processing:

- Single Record: Use `process_records` to process a single record to find an
  email address.
- Bulk Records: Use `process_records` to process bulk records from Google Sheets
  to find and append emails.

9. Combined Email Extraction:

- Use `hunter_drop_emails` to extract emails using both HunterIO and
  DropContact, and write the results to Google Sheets.

# Dropcontact

## Introduction

- DropContact [https://www.dropcontact.com/](https://www.dropcontact.com/) is a
  service to find people's emails from their first and last name

## Code

- The code is located at `ck_marketing/dropcontact/dropcontact_api.py`
- An example notebook is at
  `ck_marketing/process_automation/Master.cold_outreach.ipynb`
- It contains a full process for extracting data using `DropContact` API and
  adding into an existing Google sheet

## Workflows

1. Preprocess Data

- The `_preprocess_dropcontact_data` function formats input lists of first
  names, last names, and company names into a list of dictionaries for the
  DropContact API.

2. Send API Request

- The `_request_dropcontact` function sends a POST request to DropContact with
  the formatted batch data and returns the API response.

3. Generate DataFrame

- The `_generate_result_df` function converts the API query results into a
  pandas DataFrame with columns like first name, last name, full name, email,
  phone, pronoun, and job title.

4. Batch Request Handling

- The `_send_batch_request` function divides the data into batches, sends
  requests for each batch, checks for completion, and compiles the results. It
  handles timeouts and errors, retrying the request up to 12 times with a
  10-second interval.

5. Main Function

- The `get_email_from_dropcontact` function integrates the preprocessing, batch
  requesting, and result generation to return a final DataFrame with the desired
  information.

# Signal NFX

## Introduction

- Signal NFX contains many lists of investors for different stage (e.g.,
  pre-seed, seed, series A) and verticals (e.g., AI), e.g.,
  `https://signal.nfx.com/investor-lists/`

## Code

- The module is located at `ck_marketing/signal_nfx`
- An example notebook is at
  `ck_marketing/signal_nfx/notebooks/SorrTask612_Get_information_from_Signal.ipynb`

## Workflows

- Import the module using `import ck_marketing.signal as mrksign`
- Select a list in
  [https://signal.nfx.com/investor-lists/](https://signal.nfx.com/investor-lists/)
  and open its page
- The url for the list will work as a input data, for e.g.:
  `baseurl = [https://signal.nfx.com/investor-lists/top-fintech-seed-investor](https://signal.nfx.com/investor-lists/top-fintech-seed-investor)s`
- Determine the range of data to be extracted in a particular run by specifying
  the start index and the length of the data
  - This is because the page is only loading a few items for one click on the
    loading button and the total length of data is unknown. We don't want the
    code to run forever
- A Pandas dataframe with investors' `First Name`, `Last Name` and
  `Company Name`

# Process Automation

## Introduction

- This process automation extracts and validates profiles with emails using APIs
  from PhantomBuster, DropContact, Google Sheets, and HunterIO.

## Code

- The module is located at
  `ck_marketing/process_automation/Master.cold_outreach.py`

## Workflow

- Setup and configuration
  - Import necessary modules and initialize logging
  - Set up API keys from environment variables
  - Initialize the Phantom instance

- PhantomBuster to extract profiles
  - Fetch and display all PhantomBuster agents
  - Select and launch a specific agent to extract profiles into a DataFrame
  - Upload the extracted DataFrame to a Google Sheet

- Clean profiles
  - Filter profiles based on specific criteria
  - Save the cleaned profiles to a new tab in the Google Sheet

- HunterIO & DropContact to extract/verify emails
  - Use HunterIO and DropContact APIs to find and append emails to the profiles
  - Verify the extracted emails using HunterIO

- Final Dataframe
  - Create a final DataFrame with verified profiles and emails
  - Filter out rows with empty email fields
  - Save the final DataFrame to the Google Sheet

# Folkapp

## Introduction

- This process automation scrapes VC profile data from a shared FolkApp link
  using Playwright. It scrolls through dynamically loaded rows and columns to
  extract structured profile data, which is then cleaned and saved as a CSV for
  further enrichment or outreach.

## Code

- The module is located at `ck_marketing/folkapp/notebooks/Folkapp.ipynb`

## Workflow

- Use Playwright to launch a Chromium browser in non-headless mode and open the
  target FolkApp shared URL
  `https://app.folk.app/shared/US-VCs-oc71Oi94yB9vwbfh1XWIQPHTAGQE7FQ1`

- Extract the table headers from the second row of the virtualized table and
  store them as column titles

- Start scrolling through the table in a loop:
  - Click the first visible name row to trigger rendering of the remaining
    columns
  - Track and compare `aria-rowindex` attributes to determine if new rows have
    loaded
  - If no new rows are found, break the loop

- For each visible batch of rows:
  - Extract the last line of each name cell
  - Extract and flatten the visible columns using asynchronous `inner_text()`
    calls

- Scroll horizontally if needed by pressing `"ArrowLeft"` and jumping back to
  the latest loaded row

- Once all rows are collected:
  - Build a `pandas.DataFrame` using the collected data
  - Clean the `"Companies"` column and replace newlines with semicolons

- Save the final result to a local CSV file `folkapp1.csv`

# Money2020

## Introduction

- This process extracts and enriches attendee data from the
  [Money20/20](https://money2020.com/) conference platform using authenticated
  API requests.
- The system logs in using credentials, paginates through public attendee data,
  and further enriches the dataset with email and phone details via secondary
  API calls.

## Code

- The module is located at
  `ck_marketing/notebooks/CmTask10499_Scrape_the_money_20-20_attendees.ipynb`

## Workflow

- Setup and import `helpers` functions.
- Authenticate using a username/password combo and an `x-authorization` token
  via a session login POST request.
- Define the base API URL (`https://api-prod.grip.events/...`) and iterate over
  1000 pages to fetch paginated attendee data.
- Retry failed requests (including rate-limited ones) up to 3 times using
  exponential backoff.
- Parse each response to extract attendee fields: `firstName`, `lastName`,
  `jobTitle`, `companyName`, `location`, and `id`.
- Store results in a structured `DataFrame` and save them as
  `money20-20_Attandees.csv_Requests`.
- Load a filtered attendee dataset (`money2020_data.csv`) for enrichment.
- For each attendee `id`, make a secondary GET request to `/contact_details` to
  retrieve:
  - `email`
  - `phone_number`
  - `is_connection`
  - `contact_sharing`
- Append enriched fields to the existing DataFrame and save as
  `money20-20_Attandees_Contacts.csv`.
- Categorize email availability status and compute availability statistics:
  - `email available as connected`
  - `email available if connected`
  - `email not available as private`

# Growjo

## Introduction

- Growjo maintains ranked lists of the fastest-growing companies in various
  industries, including AI. This scraper targets the
  [AI companies list on Growjo](https://growjo.com/industry/AI), extracting
  structured data like revenue, funding, employees, and key personnel for each
  company across multiple pages.

## Code

- The module is located at `ck_marketing/misc/CmampTask11363_Growjo_data.py`
- Output is saved to a **Google Sheet** for easy access and tracking.
- Requires authentication using a **Google service account key file**.

## Workflow

- Run the script directly as a Python module.
- The script visits paginated URLs such as: `https://growjo.com/industry/AI/1`,
  `.../AI/2`, etc.
- For each page:
  - It uses Selenium to wait for the table to load.
  - Extracts rows using BeautifulSoup.
- The following fields are extracted:
  - `Rank`, `Name`, `City`, `State`, `Country`, `Funding`, `Employees`,
    `Revenue`, `Predictive Score`, `Person Name`, `Title`
- All data is stored in a Pandas dataframe.
- The resulting dataframe is written to Google Sheets.

# 50Pros.Com

## Introduction

- This script scrapes detailed data on Fortune 500 companies from
  [50pros.com](https://www.50pros.com/fortune500). The extracted information
  includes company name, industry, city, website, employees, revenue, CEO, and
  other relevant fields.

## Code

- The script is located at:
  `ck_marketing/misc/CmampTask11363_Fortune500_data.py`

## Workflows

- Run the script as a Python module.
- The script loads the URL:
  `https://www.50pros.com/fortune500`
- Uses Selenium to navigate the page and switch into the iframe containing the
  data table.
- Waits for the iframe and table elements to load.
- Switches to the iframe that contains the company table.
- Extracts rows from the table, retrieving fields such as:
  `Name`, `Industry`, `City`, `Website`, `Employees`, `Revenue (Millions)`,
  `CEO`
- Compiles the data into a Pandas dataframe.
- Writes the dataframe to Google Sheets.

# Datamation

## Introduction

- Focuses on AI companies to enrich sector-specific targeting and research.

## Code

- Located at:
  `ck_marketing/misc/CmampTask11363_Target_companies_list.py`
- Uses `requests` and `BeautifulSoup` to scrape and parse company information.

## Workflow

- Setup and configuration

  - Go to the [Google Cloud Console](https://console.cloud.google.com/).
  - Create a new project or select an existing one.
  - Navigate to `APIs & Services` > `Enabled APIs & services`.
  - Enable the `Google Sheets API` and `Google Drive API`.
  - Go to `APIs & Services` > `Credentials`.
  - Click `Credentials` > `Create Credentials` > `Service Account`.
  - Follow the steps to create the service account.
  - Once created, click the service account email, then go to the `Keys` tab.
  - Click `Add Key` > `Create new key` > choose `JSON`.
  - **Download the JSON key file** when prompted — this file contains your credentials.
      - **Important**: Keep this file secure and **do not** share it publicly.

  - In your script, replace `<path_to_your_personal_keyfile_here>` with the actual path to this downloaded `.json` file.

- Data scraping
  - Send a request to Datamation AI companies page
  - Parse HTML with BeautifulSoup
  - Extract company details (name, headquarters, revenue, Glassdoor score) from
    headers and paragraphs

- Data processing
  - Collect extracted data into a Pandas DataFrame

- Data upload
  - Authenticate with Google Sheets API using helper functions
  - Upload the DataFrame to a specified Google Sheet
  - Skip upload if no data is found
