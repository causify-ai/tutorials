#!/usr/bin/env python
"""
Generate project descriptions from a Google Sheet and save them to a Markdown
file.

> project_description.py \
    --sheet_url "https://docs.google.com/spreadsheets/d/1abc...gid=0" \
    --markdown_path ./projects/MSML610_Projects.md \
    --max_projects 3 \
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
        "https://docs.google.com/"
        "spreadsheets/d/"
        "1Ez5uRvOgvDMkFc9c6mI21kscTKnpiCSh4UkUh_ifLIw/"
        "edit?gid=0#gid=0"
    )
    # Set to True to use the actual spreadsheet link
else:
    # Set to False for testing purposes
    fake_url = "https://docs.google.com/fake-sheet-url"
    DEFAULT_SHEET_URL = fake_url
GLOBAL_PROMPT = """Act as a data science professor.
I will give you a tool (XYZ) and difficulty level (1–3).
Write a short bullet-point project brief on how XYZ can be
used for real-time Bitcoin data ingestion in Python.
Include:

- Title
- Difficulty (1 means easy, should take around 7 days to develop, 2 is medium difficulty, should take around 10 days to complete, 3 is hard,should take 14 days to complete)
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
DEFAULT_MARKDOWN_PATH = "./projects/MSML610_Projects.md"
# The maximum number of projects.
# Set the value to None to disable the limit.
DEFAULT_MAX_PROJECTS = None


def _read_google_sheet(url: str, secret_path: str) -> pd.DataFrame:
    """
    Read the Google Sheet and return the data as a pandas DataFrame.

    :param url: the URL of the Google Sheet to read
    :param secret_path: path to google_secret.json
    :return: the data
    """
    _LOG.info("Reading Google Sheet %s: ", url)
    _LOG.info("Using credentials from: %s", secret_path)
    credentials = hgofiapi.get_credentials(service_key_path=secret_path)
    df = hgofiapi.read_google_file(url, credentials=credentials)
    return df


def _generate_project_description(project_name: str, difficulty: str) -> Any:
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
        prompt = f"Technology: {project_name}\nDifficulty: {difficulty}"
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
    markdown_path: str,
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
    content = "# MSML610 Projects\n\n"
    # Generate the project descriptions.
    # Limit the number of projects.
    rows = df.head(max_projects) if max_projects is not None else df
    for _, row in rows.iterrows():
        project_name = row["Tool"]
        difficulty = row["Difficulty"]
        description = _generate_project_description(project_name, difficulty)
        # Add the project description to the markdown file.
        content += f"## {project_name}\n"
        content += f"{description}\n\n"
        # Letting it wait for a while before triggering another request
        time.sleep(sleep_sec)
    # Write the markdown file.
    hio.to_file(markdown_path, content)


def _parse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--sheet_url", default=DEFAULT_SHEET_URL, help="Google Sheet URL"
    )
    parser.add_argument(
        "--secret_path",
        default="/app/DATA605/google_secret.json",
        help="Path to Google service‑account JSON.",
    )
    parser.add_argument(
        "--markdown_path",
        default=DEFAULT_MARKDOWN_PATH,
        help="Output Markdown file",
    )
    parser.add_argument(
        "--max_projects",
        type=int,
        default=DEFAULT_MAX_PROJECTS,
        help="Limit rows processed (None = all).",
    )
    parser.add_argument(
        "--openai_key",
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
    markdown_path = str(pathlib.Path(args.markdown_path).expanduser().resolve())
    _LOG.info("Reading sheet %s", args.sheet_url)
    sheet_df = _read_google_sheet(args.sheet_url, secret_path)
    _LOG.info("Generating Markdown → %s", markdown_path)
    create_markdown_file(
        sheet_df,
        markdown_path,
        args.max_projects,
    )
    _LOG.info("Done: %s", markdown_path)


if __name__ == "__main__":
    _main(_parse())
