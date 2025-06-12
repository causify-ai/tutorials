<!-- toc -->

  * [What It Does](#what-it-does)
  * [Assumptions / Requirements](#assumptions--requirements)
  * [Instructions](#instructions)
    + [Step 1: Fetch Input](#step-1-fetch-input)
- [Edit GOOGLE_SHEET_URL inside the script or pass a new one to read_google_sheet()](#edit-google_sheet_url-inside-the-script-or-pass-a-new-one-to-read_google_sheet)
  * [Step 2: Describe Action](#step-2-describe-action)
    + [Step 3: Review Output](#step-3-review-output)
  * [Troubleshooting](#troubleshooting)

<!-- tocstop -->

# What It Does

- Automates the process of generating academic project descriptions by:
  - Reading project data from a Google Sheet.
  - Using OpenAI's API to auto-generate detailed project descriptions.
  - Saving the final output in a formatted Markdown file for distribution.

## Assumptions / Requirements

- Google Cloud service key file at `/app/DATA605/google_secret.json`
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

The Google Sheet should contain:

- Project name

- Difficulty

# Edit GOOGLE_SHEET_URL inside the script or pass a new one to read_google_sheet()

URL="https://docs.google.com/spreadsheets/d/<sheet_id>/edit"

## Step 2: Describe Action

- Run the script directly using Python
- This will:

  Authenticate and read the Google Sheet

  Generate a project description using OpenAI for each row

  Save the top 5 (or all if MAX_PROJECTS=None) projects in a file called
  `./projects/DATA605_Projects.md`

### Step 3: Review Output

- Navigate to the projects/ folder and open DATA605_Projects.md.

## Troubleshooting

Issue: google.auth.exceptions.DefaultCredentialsError Cause: Google service key
not found at the expected path. Fix: Place the correct google_secret.json file
in /app/DATA605/.

Issue: ModuleNotFoundError: No module named 'helpers' Cause: Missing local
helper modules. Fix: Ensure helpers/ directory is in your PYTHONPATH or the same
directory as the script.

Issue: Empty or incomplete output file Cause: API failure or invalid sheet
format. Fix: Check logs, verify if the OpenAI and Google API calls are working,
and ensure data in the Google Sheet is structured correctly.
