#!/usr/bin/env python
"""
Generate project descriptions from a Google Sheet and save them to a Markdown
file. This script also creates Github links for the project files and adds them
back to the Google Sheet. Set the OPENAI_API_KEY using export before running script.

>   python tutorial_class_project_instructions/generate_class_project_description.py
    
    --tab_name ""
    -v INFO

Import as:

import DATA605.project_description as dprodesc
"""

import argparse
import logging
import pathlib
import time
import re
from collections import defaultdict
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
DEFAULT_FILE_GITHUB_LINK = (
    "https://github.com/causify-ai/tutorials/"
    "blob/TutorTask640_Generating_Markdowns_for_MSML610_Projects/"
    "class_project_instructions/Projects/"
)
tool_description_cache = defaultdict(list)
# Write a short bullet-point project brief on how XYZ can be
# used for real-time Bitcoin data ingestion in Python.

# - Prefer solutions that can run on a **standard laptop or cloud notebooks with limited resources (e.g., Colab free tier)**.
GLOBAL_PROMPT = """Act as a graduate data science professor.
I will give you a tool (XYZ). 
Write **three distinct and realistic graduate-level data science project briefs** using the given tool XYZ.
Each project should be distinct, creative, and feasible for a graduate student to build over a semester.
Include:
- Title
- Difficulty: 1/2/3 (1 = easy, 2 = medium, 3 = hard; use each level **exactly once**)
- Tech Description: 1–2 lines about how the tool is used in this project
- Project Idea: 6-8 lines explaining the goal and approach.
- Python libs - 4–6 packages used in the implementation
- Is it Free? - Yes/No with explanation.
- Relevant tool(XYZ) related Resource Links

**Constraints**:
- Use **different data sources**, **problem domains**, or **ML tasks** across the 3 projects.- DO NOT reuse the same Bitcoin price API data or ML algorithm.
- Keep each project unique and useful.
- Do NOT repeat the same dataset or algorithm across projects.
- Use realistic, popular Python packages—no toy examples.
- Do not propose projects that require physical sensors or IoT devices or non-public data.
- Only use **freely available public data** via free APIs (no limited usage), web streams, or downloadable datasets.
- Mention the dataset name or source clearly.
- Do NOT mention surveys, forms, or custom user data collection.
- Use **pre-trained models** for NLP or vision tasks — do not require training from scratch.
- Avoid projects that require **GPUs, multi-node clusters, or expensive cloud compute**.
- Do NOT propose large-scale deep learning training unless using transfer learning on a small dataset.
- Avoid real-time claims unless tool supports it.
- Do **not propose large-scale training of transformer models or deep learning systems** unless pre-trained models are used for lightweight inference or fine-tuning on small datasets.
- Avoid long texts or steps. Use concise, clear language.

Examples of variation:
- Different data sources: GraphQL, WebSockets, news APIs, order books
- Different ML tasks: Forecasting, anomaly detection, clustering
- Different environments: cloud services, edge computing, streaming pipelines
Look at the example to get an idea of how it needs to look. 
"""
EXAMPLE = """Example using Streamlit (technology XYZ):

### Project 1  
**Title**: Interactive EDA Dashboard for Global Earthquake Data  
**Difficulty**: 1  
**Tech Description**: Use Streamlit to build an interactive web app for visualizing and filtering earthquake data.  
**Project Idea**: Create a simple Streamlit dashboard that loads real-time global earthquake data from the USGS API. Allow users to filter earthquakes by magnitude, date, and region. Add dynamic maps using `pydeck` and graphs with `plotly`. Ideal for learning basic dashboard interactivity and data visualization.  
**Python libs**: streamlit, pandas, plotly, requests, pydeck  
**Is it Free?**: Yes, Streamlit is open-source and completely free  
**Resource Links**: [Streamlit Docs](https://docs.streamlit.io), [USGS API](https://earthquake.usgs.gov/fdsnws/event/1/)

---

### Project 2  
**Title**: Job Salary Estimator App Using Streamlit and NLP  
**Difficulty**: 2  
**Tech Description**: Use Streamlit to deploy a trained NLP model that predicts job salaries from descriptions.  
**Project Idea**: Train an NLP model on the Kaggle “Salary Prediction” dataset that predicts salary based on job descriptions. Deploy the model as an interactive app using Streamlit, where users can input job text and see predicted salaries, confidence intervals, and key phrase highlights.  
**Python libs**: streamlit, scikit-learn, nltk, pandas, shap  
**Is it Free?**: Yes  
**Resource Links**: [Streamlit Docs](https://docs.streamlit.io), [Kaggle Dataset](https://www.kaggle.com/c/job-salary-prediction)

---

### Project 3  
**Title**: Real-Time Traffic Accident Alert System  
**Difficulty**: 3  
**Tech Description**: Use Streamlit to display live alerts and analytics using a streaming API of traffic incidents.  
**Project Idea**: Build a real-time dashboard that pulls traffic accident data from a live API like the MapQuest Traffic Feed or Open511. Use asynchronous requests and queueing to process alerts, show severity-based maps, and send browser notifications. Add clustering of hot zones using unsupervised learning.  
**Python libs**: streamlit, aiohttp, folium, scikit-learn, pandas, altair  
**Is it Free?**: Streamlit is free; some APIs may require free tokens or rate limits  
**Resource Links**: [Streamlit Docs](https://docs.streamlit.io), [Open511 API](https://open511.org/), [MapQuest](https://developer.mapquest.com)

"""

DEFAULT_MARKDOWN_PATH = "./class_project_instructions/Projects"
# The maximum number of projects.
# Set the value to None to disable the limit.
DEFAULT_MAX_PROJECTS = None


def _read_google_sheet(url: str, tab_name: str, secret_path: str) -> pd.DataFrame:
    """
    Read the Google Sheet and return the data as a pandas DataFrame.

    :param url: the URL of the Google Sheet to read
    :param secret_path: path to google_secret.json
    :return: the data
    """
    _LOG.info("Reading Google Sheet %s: ", url)
    _LOG.info("Using credentials from: %s", secret_path)
    credentials = hgofiapi.get_credentials(service_key_path=secret_path)
    df = hgofiapi.read_google_file(url, tab_name, credentials=credentials)
    return df


def _write_google_sheet(
    df, url: str, tab_name: str, secret_path: str
) -> pd.DataFrame:
    """
    Write the paths to project description files back to Google Sheet.

    :param url: the URL of the Google Sheet to read
    :param secret_path: path to google_secret.json
    :return: the data
    """
    _LOG.info("Writing to Google Sheet %s: ", url)
    _LOG.info("Using credentials from: %s", secret_path)
    credentials = hgofiapi.get_credentials(service_key_path=secret_path)
    try:
        hgofiapi.write_to_google_sheet(
            df, url, tab_name, append=True, credentials=credentials
        )
    except ValueError as e:
        _LOG.info("ERROR while writing to Google Sheet %s", str(e))
    return df


def _build_prompt(project_name: str) -> str:
    if False:
        # Potential (v3) prompt if needed to use.
        # Change False to True to use it.
        if not previous_descriptions:
            return (
                f"Write a professional and detailed project description"
                f"for a data project titled '{project_name}'. "
                f"Indicate the difficulty level: '1/2/3, and include objectives, "
                f"technologies used, and expected outcomes."
                f"Make sure it is different from the following:\n{previous_descriptions}\n"
                f"Only focus on the new idea."
            )
        else:
            previous_descriptions = "\n- " + "\n- ".join(previous_descriptions)
            return (
                f"Write a professional and detailed project description"
                f"for a data project titled '{project_name}'. "
                f"Indicate the difficulty level: '1/2/3, and include objectives, "
                f"technologies used, and expected outcomes."
                f"Make sure it is different from the following:\n{previous_descriptions}\n"
                f"Only focus on the new idea."
            )
        # Will use more tokens, but might help produce a better result.
    elif False:
        # v1 (Original) prompt.
        # Change False to True to use it.
        if not previous_descriptions:
            return f"Generate a project description for '{project_name}',"
            f"with difficulty level: 1/2/3."
        else:
            previous_descriptions = "\n- " + "\n- ".join(previous_descriptions)
            return (
                f"Generate a project description for '{project_name}',"
                f"with difficulty level: 1/2/3."
                f"Make sure it is completely different from the following:\n{previous_descriptions}\n"
                f"Only focus on the new idea."
            )
    else:
        # v2: Added by Aayush as an improvement to optimize tokens
        # while conveying the same information.
        # Short, to the point and concise. Saves the most tokens while achieving similar results.
        # if not previous_descriptions:
        #     return f"Technology: {project_name}."
        # else:
        #     previous_descriptions = "\n- " + "\n- ".join(previous_descriptions)
            # return (
            #     f"Technology: {project_name}."
            #     f"Do NOT repeat the following idea:"
            #     f"{previous_descriptions}\n"
            #     f"Only focus on the new idea."
            #     f"Create a **completely new project** that differs clearly in all three aspects:\n"
            #     f"1. the domain or application (e.g., use a different target problem),"
            #     f"2. the data source (e.g., webscraping, APIs,ready datasets),"
            #     f"3. the ML task (e.g., clustering, regression, classification, forecasting, anomaly detection, etc.)."
            #     f"Also change the difficulty by 1 from the previous project (i.e., make it one level easier or harder).\n"
            #     f"Match the style and format of the GLOBAL PROMPT strictly."
                
            # )
        return (
            f"Tool: {project_name}.\n"
            f"Generate three new and distinct graduate-level data science project ideas using this tool.\n"
            f"Each project must have a unique difficulty level (1, 2, 3)."
        )


def _generate_project_description(
    project_name: str
) -> Any:
    """
    Generate a project description. Depending on the value in No of Projects
    columns, this will generate N number of projects for each tool, each
    different from the other.

    :param project_name: the name of the project
    :param difficulty: the difficulty level of the project
    :return: the project description
    """
    prompt = _build_prompt(project_name)
    project_desc = hopenai.get_completion(
        prompt,
        system_prompt=GLOBAL_PROMPT,
        model="gpt-4o-mini",
        cache_mode="FALLBACK",
        temperature=0.5,
        max_tokens=1000,
        print_cost=True,
    )
    return project_desc


def create_markdown_file(
    df: pd.DataFrame,
    markdown_folder_path: str,
    max_projects: Optional[int],
    *,
    sleep_sec: float = 1.5,
) -> pd.DataFrame:
    """
    Create a markdown file with the project descriptions using helpers.hio.

    :param df: the dataframe containing the project descriptions
    :param markdown_path: the path to the markdown file
    :param max_projects: limit to the rows processed
    :param sleep_sec: amount of time to sleep between rows
    """
    file_githublinks_df = pd.DataFrame(columns=["Tool","URL"])
    rows = df.head(max_projects) if max_projects is not None else df
    # temps = [0.3,0.45,0.6]
    pathlib.Path(markdown_folder_path).mkdir(parents=True, exist_ok=True)
    for _, row in rows.iterrows():
        content = ""
        project_name = row["Tool"]
        # n_projects = int(row.get("No of Projects", 1))
        # for i in range(n_projects):
            # prev_descs = tool_description_cache[project_name][-2:]
        description = _generate_project_description(
                project_name)
        # tool_description_cache[project_name].append(description)
            # Add the project description to the markdown file.
            # difficulty_match = re.search(r"[Dd]ifficulty\s*[:\-–=]\s*(\d)", description)
            # if not difficulty_match:
            #     # Try to find "### Difficulty" followed by a number on the next line
            #     match_lines = re.findall(r"#+\s*Difficulty\s*\n\s*(\d)", description)
            #     if match_lines:
            #         difficulty = match_lines[0]
            #     else:
            #         difficulty = "N/A"
            #         _LOG.warning("Could not extract difficulty from description for tool:\n%s", project_name)
            # else:
            #     difficulty = difficulty_match.group(1)
    
        
            # content += f"## {project_name}\n"
            # content += f"{description}\n\n"
            # content = f"# {project_name} Project Description\n\n"
            # content += f"## Difficulty Level: {difficulty}\n\n"
            # content += f"## Project Description\n"
        content = f"{description}\n\n"
        # content += f"######################## END ###############################\n\n"
        file_name = f"{project_name}_Project_Description.md"
        markdown_path = pathlib.Path(markdown_folder_path) / file_name
            # if markdown_path.exists():
            #     _LOG.info(
            #         "File already exists, skipping generation: %s", markdown_path
            #     )
                
            # else:
        hio.to_file(str(markdown_path), content)
        _LOG.info("Generated Markdown File: %s", file_name)
        github_url = f"{DEFAULT_FILE_GITHUB_LINK}{file_name}"
        file_githublinks_df.loc[len(file_githublinks_df)] = [project_name,github_url]
            # Letting it wait for a while before triggering another request
        time.sleep(sleep_sec)
    return file_githublinks_df


def _parse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--sheet_url", default=DEFAULT_SHEET_URL, help="Google Sheet URL"
    )
    parser.add_argument(
        "--tab_name",
        type=str,
        default="MSML610 - Fall 2025",
        help="Tab to read data from within Google Sheet",
    )
    parser.add_argument(
        "--secret_path",
        # default="/app/DATA605/google_secret.json",
        default="~/.config/gspread_pandas/google_secret.json",
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
    markdown_folder_path = str(
        pathlib.Path(args.markdown_folder_path).expanduser().resolve()
    )
    _LOG.info("Reading sheet %s", args.sheet_url)
    sheet_df = _read_google_sheet(args.sheet_url, args.tab_name, secret_path)
    file_githublinks_df = create_markdown_file(
        sheet_df,
        markdown_folder_path,
        args.max_projects,
    )
    _LOG.info("Done: %s", markdown_folder_path)
    _LOG.info("Adding GitHub links to Project files to Google sheet")
    # _write_google_sheet(
        # file_githublinks_df, args.sheet_url, 'MSML610 Project Github Links', secret_path
    # )


if __name__ == "__main__":
    _main(_parse())
