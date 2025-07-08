# How To Guide: `project_description.py`

<!-- toc -->

- [What It Does](#what-it-does)
- [Assumptions / Requirements](#assumptions--requirements)
- [Instructions](#instructions)
  * [Step 1: Fetch Input](#step-1-fetch-input)
  * [Step 2: Script Execution](#step-2-script-execution)
  * [Step 3: Review Output](#step-3-review-output)
- [Troubleshooting](#troubleshooting)

<!-- tocstop -->

## What It Does

- Automates the process of generating academic project descriptions by:
  - Reading project data from a Google Sheet.
  - Using OpenAI's API to auto-generate detailed project descriptions.
  - Saving the final output in a formatted Markdown file for distribution.

## Assumptions / Requirements

- Google Cloud service key file ready to use
- Docker running
- Valid OpenAI API key for model access
- Project-specific helper modules must be available:
  - Helpers.hgoogle_file_api
  - Helpers.hio
  - Helpers.hopenai

## Instructions

### Step 1: Fetch Input

Ensure the Google Sheet is publicly accessible or shared with the configured
service account.

For instructions on how to configure google sheets API, follow this link:
[https://github.com/causify-ai/helpers/blob/c50fddfdffccdccb1b2d963b729ab9674d8fda8f/docs/tools/notebooks/all.gsheet_into_pandas.how_to_guide.md](https://github.com/causify-ai/helpers/blob/c50fddfdffccdccb1b2d963b729ab9674d8fda8f/docs/tools/notebooks/all.gsheet_into_pandas.how_to_guide.md)

The Google Sheet should contain:

- Project name

- Difficulty

## Step 2: Script Execution

- Run the script directly using Python
- This will:

  Authenticate and read the Google Sheet

  Generate a project description using OpenAI for each row

  Save the top N (or all if MAX_PROJECTS=None) projects in a file called
  `./projects/DATA605_Projects.md`

Code to run script:

```bash
python <file_path>/project_description.py   --sheet_url <file_path>   --secret_path <file_path>  --openai_key key   --markdown_path <file_path>  -v INFO
```

Edit Google Sheet URL inside the script or pass a new one through CLI

### Step 3: Review Output

- Markdown stored at DATA605/projects/MSML610_Projects.md.

## Troubleshooting

Issue: google.auth.exceptions.DefaultCredentialsError Cause: Google service key
not found at the expected path. Fix: Place the correct google_secret.json file
in /app/DATA605/.

Issue: Empty or incomplete output file Cause: API failure or invalid sheet
format. Fix: Check logs, verify if the OpenAI and Google API calls are working,
and ensure data in the Google Sheet is structured correctly.
