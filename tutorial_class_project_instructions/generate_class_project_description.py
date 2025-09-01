#!/usr/bin/env python
"""
Generate project descriptions from a Google Sheet and save them to a Markdown
file.

>   python tutorial_class_project_instructions/generate_class_project_description.py  
    --OPENAI_API_KEY ""  
    -v INFO

Import as:

import DATA605.project_description as dprodesc
"""

import argparse
import logging
import pathlib
import time
from typing import Any, Optional

import pandas as pd

import helpers_root.helpers.hdbg as hdbg
import helpers_root.helpers.hgoogle_drive_api as hgofiapi
import helpers_root.helpers.hio as hio
import helpers_root.helpers.hopenai as hopenai
import helpers_root.helpers.hparser as hparser

_LOG = logging.getLogger(__name__)

# Set Constants.
if True:
    DEFAULT_SHEET_URL = (
        # "https://docs.google.com/"
        # "spreadsheets/d/"
        # "1Ez5uRvOgvDMkFc9c6mI21kscTKnpiCSh4UkUh_ifLIw/"
        # "edit?gid=0#gid=0"
        "https://docs.google.com/"
        "spreadsheets/d/"
        "1Ez5uRvOgvDMkFc9c6mI21kscTKnpiCSh4UkUh_ifLIw/"
        "edit?pli=1&gid=934932850#gid=934932850"
    )
    
    # Set to True to use the actual spreadsheet link
else:
    # Set to False for testing purposes
    fake_url = "https://docs.google.com/fake-sheet-url"
    DEFAULT_SHEET_URL = fake_url
GLOBAL_PROMPT = """Act as a data science professor.
I will give you a tool (XYZ).
Write a short bullet-point project brief on how XYZ can be
used for real-time Bitcoin data ingestion in Python.
Include:

- Title
- Difficulty - 1/2/3 (1 means easy, should take around 7 days to develop, 2 is medium difficulty, should take around 10 days to complete, 3 is hard,should take 14 days to complete)
- Tech Description
- Project Idea
- Python libs
- Is it Free?
- Relevant tool(XYZ) related Resource Links

Avoid long texts or steps
"""
EXAMPLE = """Example:
Title: Ingest bitcoin prices using AWS Glue (AWS Glue is technology XYZ)
Difficulty: 1
Description
AWS Glue is a fully managed extract, transform, and load (ETL) service...
Useful resources: AWS Glue Docs
Is it free?: Free tier available with limits
Python libraries: boto3, PySpark
"""
DEFAULT_MARKDOWN_PATH = "./class_project_instructions/Projects"
# The maximum number of projects.
# Set the value to None to disable the limit.
DEFAULT_MAX_PROJECTS = None


def _read_google_sheet(url: str,tab_name: str, secret_path: str) -> pd.DataFrame:
    """
    Read the Google Sheet and return the data as a pandas DataFrame.

    :param url: the URL of the Google Sheet to read
    :param secret_path: path to google_secret.json
    :return: the data
    """
    _LOG.info("Reading Google Sheet %s: ", url)
    _LOG.info("Using credentials from: %s", secret_path)
    credentials = hgofiapi.get_credentials(service_key_path=secret_path)
    df = hgofiapi.read_google_file(url,tab_name, credentials=credentials)
    return df


def _generate_project_description(project_name: str) -> Any:
    """
    Generate a project description.

    :param project_name: the name of the project
    :param difficulty: the difficulty level of the project
    :return: the project description
    """
    if False:
        # Potential (v3) prompt if needed to use.
        # Change False to True to use it.
        prompt = (
            f"Write a professional and detailed project description"
            f"for a data project titled '{project_name}'. "
            f"Indicate the difficulty level as '{difficulty}', and include objectives, "
            f"technologies used, and expected outcomes."
        )
        # Will use more tokens, but might help produce a better result.
    elif False:
        # v1 (Original) prompt.
        # Change False to True to use it.
        prompt = (
            f"Generate a project description for '{project_name}',"
            f"with difficulty level '{difficulty}'."
        )
    else:
        # v2: Added by Aayush as an improvement to optimize tokens
        # while conveying the same information.
        prompt = f"Technology: {project_name}"
        # Short, to the point and concise. Saves the most tokens while achieving similar results.
    project_desc = hopenai.get_completion(
        prompt,
        system_prompt=GLOBAL_PROMPT,
        model="gpt-4o-mini",
        cache_mode="FALLBACK",
        temperature=0.3,
        max_tokens=400,
        print_cost=True,
    )
    return project_desc


def create_markdown_file(
    df: pd.DataFrame,
    markdown_folder_path: str,
    max_projects: Optional[int],
    *,
    sleep_sec: float = 1.5,
) -> None:
    """
    Create a markdown file with the project descriptions using helpers.hio.

    :param df: the dataframe containing the project descriptions
    :param markdown_path: the path to the markdown file
    :param max_projects: limit to the rows processed
    :param sleep_sec: amount of time to sleep between rows
    """
    # Generate the project descriptions.
    # Limit the number of projects.
    rows = df.head(max_projects) if max_projects is not None else df
    pathlib.Path(markdown_folder_path).mkdir(parents=True, exist_ok=True)
    for _, row in rows.iterrows():
        content = ""
        project_name = row["Tool"]
        # difficulty = row["Difficulty"]
        description = _generate_project_description(project_name)
        # Add the project description to the markdown file.
        difficulty = "Failed"  # Default difficulty level if extraction fails
        if "difficulty" in description.lower():
            # Extract the difficulty level from the response (assuming it follows 'difficulty: X')
            try:
                difficulty = next(
                    word.split(":")[1].strip() 
                    for word in description.splitlines() 
                    if "difficulty" in word.lower()
                )
            except IndexError:
                _LOG.warning(f"Difficulty level extraction failed for {project_name}, defaulting to 1.")
        # content += f"## {project_name}\n"
        # content += f"{description}\n\n"
        # content = f"# {project_name} Project Description\n\n"
        # content += f"## Difficulty Level: {difficulty}\n\n"
        # content += f"## Project Description\n"
        content += f"{description}\n\n"
        file_name = f"{project_name}_Project_Description.md"
        markdown_path = pathlib.Path(markdown_folder_path) / file_name
        if markdown_path.exists():
            _LOG.info("File already exists, skipping: %s", markdown_path)
            continue
        _LOG.info("Generating Markdown → %s", markdown_path)
        hio.to_file(str(markdown_path), content)
        # Letting it wait for a while before triggering another request
        time.sleep(sleep_sec)


def _parse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--sheet_url", default=DEFAULT_SHEET_URL, help="Google Sheet URL"
    )
    parser.add_argument(
        "--tab_name", type=str, default='MSML610 - Fall 2025', help="Tab to read data from within Google Sheet"
    )
    parser.add_argument(
        "--secret_path",
        # default="/app/DATA605/google_secret.json",
        default='~/.config/gspread_pandas/google_secret.json',
        help="Path to Google service‑account JSON.",
    )
    parser.add_argument(
        "--markdown_folder_path",
        default=DEFAULT_MARKDOWN_PATH,
        help="Output Projects folder",
    )
    parser.add_argument(
        "--max_projects",
        type=int,
        default=DEFAULT_MAX_PROJECTS,
        help="Limit rows processed (None = all).",
    )
    parser.add_argument(
        "--OPENAI_API_KEY",
        type=str,
        default=None,
        help="OpenAI API key (will override env var)",
    )
    
    hparser.add_verbosity_arg(parser)
    return parser


def _main(parser: argparse.ArgumentParser) -> None:
    args = parser.parse_args()
    hdbg.init_logger(verbosity=args.log_level, use_exec_path=True)
    # Expand user/relative paths to absolute ones early to avoid surprises.
    secret_path = str(pathlib.Path(args.secret_path).expanduser().resolve())
    markdown_folder_path = str(pathlib.Path(args.markdown_folder_path).expanduser().resolve())
    _LOG.info("Reading sheet %s", args.sheet_url)
    _LOG.info("TAB NAME IS %s", args.tab_name)
    sheet_df = _read_google_sheet(args.sheet_url, args.tab_name,secret_path)
    create_markdown_file(
        sheet_df,
        markdown_folder_path,
        args.max_projects,
    )
    _LOG.info("Done: %s", markdown_folder_path)


if __name__ == "__main__":
    _main(_parse())
