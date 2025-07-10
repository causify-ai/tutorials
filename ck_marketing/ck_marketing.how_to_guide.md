

<!-- toc -->

- [Extracting marketing data](#extracting-marketing-data)
- [Tracxn](#tracxn)
  * [Introduction](#introduction)
  * [Code](#code)
  * [Workflow](#workflow)
    + [Company flow](#company-flow)
    + [People flow](#people-flow)
- [PhantomBuster](#phantombuster)
  * [Introduction](#introduction-1)
  * [Code](#code-1)
  * [Workflow](#workflow-1)
- [HunterIO](#hunterio)
  * [Introduction](#introduction-2)
  * [Code](#code-2)
  * [Workflow](#workflow-2)
- [Dropcontact](#dropcontact)
  * [Introduction](#introduction-3)
  * [Code](#code-3)
  * [Workflows](#workflows)
- [Signal NFX](#signal-nfx)
  * [Introduction](#introduction-4)
  * [Code](#code-4)
  * [Workflows](#workflows-1)
- [Process Automation](#process-automation)
  * [Introduction](#introduction-5)
  * [Code](#code-5)
  * [Workflow](#workflow-3)

<!-- tocstop -->

# Extracting marketing data

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

# Tracxn

## Introduction

- Tracxn website is at https://tracxn.com
- E.g., searching for VC firms that invested in Series seed and A of AI
  companies
  https://tracxn.com/a/s/query/t/investors/t/activeinestorsvc/table?h=f7aa3582c404433be03c12f1df4f0e463c78bc6398c81a45a403ac8703e0ba0a&s=sort%3DinvestmentCount%7Corder%3DDESC
- The result is a set of links to company pages like
  https://tracxn.com/a/companies/srAiTt8Aevx0dkPbmrFdUVl21azd7Gx7AOT8J4fO1Zs/ycombinator.com/people/currentteam
  - This page contains information about people working at that company with
    information about LinkedIn and emails

## Code

- The module is located at `ck_marketing/tracxn`
- Example notebooks are at:
  - `ck_marketing/tracxn/notebooks/SorrTask601_Extract_VCs_from_Tra_search_mhtml.ipynb`
  - `ck_marketing/tracxn/notebooks/SorrTask601_Extract_people_from_Tra_company_html.ipynb`

## Workflow

### Company flow

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
https://drive.google.com/drive/u/2/folders/1nT5CYuFWLOxb10ONw7yjfzyobc9VM90- The
outputs are in
https://drive.google.com/drive/u/2/folders/1MfTeNHR7sxex_rSpyp54HeJsxtLjKqy3

### People flow

- Same flow as above but it converts a page like
  https://tracxn.com/a/d/investor/srAiTt8Aevx0dkPbmrFdUVl21azd7Gx7AOT8J4fO1Zs/ycombinator.com/people/currentteam
  into a dataframe like:
  ```txt
  Name                                                 Matanya Horowitz
  LinkedIn Profile    https://linkedin.com/in/matanya-horowitz-87805519
  ```

# PhantomBuster

## Introduction

- PhantomBuster website is at https://phantombuster.com/
- PhantomBuster is an automation tool for extracting and processing web data
  The script provided at `ck_marketing/linkedin/phantombuster_api.py`
  demonstrates how to interact with the PhantomBuster API using Python, enabling
  you to manage and retrieve data from your PhantomBuster agents.

## Code

- The module is located at
  `ck_marketing/linkedin/phantombuster_api.py`
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

# HunterIO

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

# DropContact

## Introduction

- DropContact https://www.dropcontact.com/ is a service to find people's emails
  from their first and last name

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
- Select a list in https://signal.nfx.com/investor-lists/ and open its page
- The url for the list will work as a input data, for e.g.:
  `baseurl = https://signal.nfx.com/investor-lists/top-fintech-seed-investors`
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
