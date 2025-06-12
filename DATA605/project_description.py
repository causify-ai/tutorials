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
DEFAULT_SHEET_URL = "https://docs.google.com/spreadsheets/d/1Ez5uRvOgvDMkFc9c6mI21kscTKnpiCSh4UkUh_ifLIw/edit?gid=0#gid=0"
GLOBAL_PROMPT = """
You are a college professor of Data science.
In the next prompt I will give you a topic XYZ for a class project and you will write a description using bullet points for a college class project about implementing an example big data system in Python.

The project should be related to ingesting and processing real-time data about bitcoin. The focus should be on the technology XYZ, using basic Python packages for anything else.

The assignment requires to describe the basic functionalities of the package using examples and then a concrete project related to implementing something related to time series analysis.
The complexity of the project is 1, where 1 is easy (it should take around 7 days) to develop, 2 is medium difficulty (it should take around 10 days to complete), 3 is hard (it should take 14 days to complete).

The output should follow the template below
Title:
Difficulty: (1=easy, 3=difficult)
Description
Describe technology
Describe the project
Useful resources
Is it free?
Python libraries / bindings
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


def read_google_sheet(url: str, secret_path: str) -> pd.DataFrame:
    """
    Read the Google Sheet and return the data as a pandas DataFrame.

    :param url: the URL of the Google Sheet to read
    :param secret_path: path to google_secret.json
    :return: the data
    """
    _LOG.info(f"Reading Google Sheet: {url}")
    _LOG.info(f"Using credentials from: {secret_path}")
    credentials = hgofiapi.get_credentials(service_key_path=secret_path)
    df = hgofiapi.read_google_file(url, credentials=credentials)
    return df


def generate_project_description(project_name: str, difficulty: str) -> Any:
    """
    Generate a project description.

    :param project_name: the name of the project
    :param difficulty: the difficulty level of the project
    :return: the project description
    """
    # Generate the project description.
    # prompt = f"Generate a project description for '{project_name}' with difficulty level '{difficulty}'."
    # prompt = PROMPT_DOC_URL.strip()+ "\n\n"+ EXAMPLE.strip()+ f"\n\nTechnology: {project_name}\nDifficulty: {difficulty}"
    # description = hopenai.get_completion(prompt, model="gpt-4o-mini")
    # return description
    prompt = f"Technology: {project_name}\nDifficulty: {difficulty}"
    project_desc = hopenai.get_completion(
        prompt,
        system_prompt=GLOBAL_PROMPT,
        model="gpt-4o-mini",
        cache_mode="FALLBACK",
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
        description = generate_project_description(project_name, difficulty)
        # Add the project description to the markdown file.
        content += f"## {project_name}\n"
        content += f"{description}\n\n"
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
    hparser.add_verbosity_arg(parser)  # adds -v / --log_level
    return parser


def _main(parser: argparse.ArgumentParser) -> None:
    args = parser.parse_args()
    hdbg.init_logger(verbosity=args.log_level, use_exec_path=True)
    # Expand user/relative paths to absolute ones early to avoid surprises.
    secret_path = str(pathlib.Path(args.secret_path).expanduser().resolve())
    markdown_path = str(pathlib.Path(args.markdown_path).expanduser().resolve())
    _LOG.info("Reading sheet %s", args.sheet_url)
    sheet_df = read_google_sheet(args.sheet_url, secret_path)
    _LOG.info("Generating Markdown → %s", markdown_path)
    create_markdown_file(
        sheet_df,
        markdown_path,
        args.max_projects,
    )
    _LOG.info("Done: %s", markdown_path)


if __name__ == "__main__":
    _main(_parse())
