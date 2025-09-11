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
GLOBAL_PROMPT_OLD = """Act as a graduate data science professor.
I will give you a tool (XYZ).
Write **three distinct and realistic graduate-level data science project briefs** using the given tool XYZ.
Each project should be distinct, creative, and feasible for a graduate student to build over a semester.
Include:
- Title
- Difficulty: 1/2/3 (1 = easy, 2 = medium, 3 = hard; use each level **exactly once**)
- Project Idea: 5-6 lines explaining the goal and approach.
- Python libs - 4–6 packages used in the implementation
- Is it Free? - Yes/No with explanation.
- Relevant tool(XYZ) related Resource Links

**Strict Constraints**:
- Use **different data sources**, **problem domains**, or **ML tasks** across the 3 projects.- DO NOT reuse the same Bitcoin price API data or ML algorithm.
- Keep each project unique and useful.
- Do NOT repeat the same dataset or algorithm across projects.
- Use realistic, popular Python packages—no toy examples.
- Do not propose projects that require physical sensors or IoT devices or non-public data.
- All data used must be from current, active, **public APIs or open datasets** that are **free to use without paid plans or authentication tokens**.
- Do NOT use APIs that have been discontinued or are no longer free (e.g., Twitter API, Yahoo Finance API, Google News RSS, COVID19API).
- Prefer datasets available on Kaggle (active ones only), HuggingFace Datasets, open government APIs, or GitHub repositories.
- Mention the dataset name or source clearly.
- Do NOT mention surveys, forms for custom user data source collection.
- **Do NOT use A/B testing in ANY project**.
- Use **pre-trained models** for NLP or vision tasks — do not require training from scratch.
- If describing "real-time" detection or streaming scenarios, clarify whether the data is truly streamed or simulated using static datasets. Avoid vague claims like "as new data streams in" unless you're using actual real-time APIs or streaming platforms.
- You may simulate streaming by feeding one row at a time from a static dataset in a loop — but you must clearly state this and explain how it mimics real-time inference.
- Avoid projects that require **GPUs, multi-node clusters, or expensive cloud compute**.
- Do NOT propose large-scale deep learning training unless using transfer learning on a small dataset.
- Avoid real-time claims unless tool supports it.
- Do **not propose large-scale training of transformer models or deep learning systems** unless pre-trained models are used for lightweight inference or fine-tuning on small datasets.
- Avoid long texts or steps. Use concise, clear language.
- Every project MUST involve at least one clear machine learning task (e.g., classification, regression, clustering, anomaly detection, forecasting, topic modeling, summarization, etc.).  
- Tools that focus on EDA, data cleaning, feature engineering, or visualization MUST still include ML — even if basic.
- Projects must go beyond just model acceleration or deployment; they must include an actual ML task, with data, training/fine-tuning (if needed), evaluation, and analysis.

**Avoid overuse of common topics**:
You may use common domains like housing prices, movie sentiment, traffic data. But, do not repeat these aggressively domains/toolkits across tools.

**Examples of overused combinations to avoid repeating**:
- Housing price prediction (e.g., Ames, Boston)
- Sentiment analysis on movie or product reviews
- Accident detection using traffic APIs
- Titanic or Iris EDA/classification
- Spam detection or SMS classification
- Cryptocurrency price alerts

Examples of variation:
- Different data sources: GraphQL, WebSockets, news APIs, order books
- Different ML tasks: Forecasting, anomaly detection, clustering, classification, transfer learning
Look at the example to get an idea of how it needs to look. 
"""


GLOBAL_PROMPT = """
Act as a graduate-level data science professor.
I will give you the name of a tool (XYZ).
Write a Description in 4-6 lines about what the tool is and its features in bullet points. Mention this only once in the output generated.
You must then generate a **project blueprint** that helps students build three realistic data science projects over a semester.
You must write the brief assuming the student only knows the name of the tool — you will decide everything else (domain, dataset type, ML task, etc.) in a technically feasible and pedagogically valuable way.

Your response must include:

1. **Difficulty** : 1/2/3 (1 is easy, 2 is medium, 3 is hard; use each level **exactly once**)
2. **Project Objective**: Clearly state the goal of the project and what is being optimized, predicted, or detected.

3. **Dataset Suggestions**: Suggest where to find datasets (e.g., Kaggle, HuggingFace, government portals, simulated data). But DO NOT provide the exact specific dataset name.

4. **Tasks**: Outline the key tasks of the project, each tailored to the tool. Describe each task in 1-2 lines high-level description in brief bullet point formats.

5. **Bonus Ideas (Optional)**: Extensions, baseline comparisons, or challenges students might attempt if they want to go further.

**Constraints**:
- Project should run on standard laptops or Google Colab.
- Do not propose projects that require physical sensors or IoT devices or non-public data.
- All data used must be from current, active, **public APIs or open datasets** that are **free to use without paid plans or authentication tokens**.
- Do NOT use APIs that have been discontinued (e.g., Yahoo Finance API).
- Prefer datasets available on Kaggle (active ones only), HuggingFace Datasets, open government APIs, or GitHub repositories or APIs with a free tier.
- Do NOT mention surveys, forms for custom user data source collection.
- Use pre-trained models if deep learning is involved.
- Avoid overused examples like Titanic or Iris.
- Avoid vague real-time claims unless well-justified.
- Every project MUST involve at least one clear machine learning task (e.g., classification, regression, clustering, anomaly detection, forecasting, topic modeling, summarization, etc.).  
- Tools that focus on EDA, data cleaning, feature engineering, or visualization MUST still include ML — even if basic.
- Projects must go beyond just model acceleration or deployment; they must include an actual ML task, with data, training/fine-tuning (if needed), evaluation, and analysis.
- Avoid vague statements like "scrape social media" — be specific and realistic.


Write in a way that is **student-friendly**, technically clear, and encourages learning and creativity.
Refer to the example below for some ideas.


EXAMPLE = Description

In this project, students will leverage TextBlob, a Python library for processing textual data, to perform real-time sentiment analysis on news articles related to Bitcoin. By integrating NewsAPI, students can access a wide range of news sources to gather relevant articles. The objective is to understand market sentiments and trends associated with Bitcoin prices and explore how this sentiment data can be utilized in time-series analysis for predictive modeling.
Technologies Used
TextBlob

    Simplifies text processing tasks with intuitive functions and methods.
    Utilizes NLTK and Pattern libraries for comprehensive NLP capabilities.
    Provides sentiment analysis returning:
        Polarity (from -1.0 to 1.0)
        Subjectivity (from 0.0 to 1.0)
    Supports multiple languages for global data processing.

NewsAPI

    Access to news articles from over 30,000 worldwide sources via HTTP REST API.
    Filters articles based on keywords, sources, language, and dates.
    Offers a free tier suitable for educational, non-commercial projects.

Project Objective

Create a pipeline to:

    Ingest real-time Bitcoin news using NewsAPI.
    Analyze sentiment with TextBlob.
    Integrate sentiment scores with Bitcoin price data for predictive time-series analysis.

Tasks

    Set Up NewsAPI Client:
        Register for API key at [NewsAPI.org].
        Use the newsapi-python client library.

    Ingest News Data:
        Fetch Bitcoin-related articles.
        Store articles and metadata (date, source) in a Pandas DataFrame.

    Perform Sentiment Analysis:
        Calculate polarity and subjectivity scores for each article.
        Aggregate sentiment scores (daily/hourly) to identify trends.

    Integrate with Bitcoin Price Data:
        Obtain Bitcoin price data via public APIs (e.g., CoinGecko).
        Align sentiment scores with price data based on timestamps.

    Time-Series Analysis:
        Implement forecasting models (ARIMA, LSTM) using sentiment scores.

    Visualization:
        Visualize correlations between sentiment trends and Bitcoin prices using Matplotlib or Seaborn.

Useful Resources

    [TextBlob Documentation]
    [NewsAPI Python Client Library]

Cost

    TextBlob: Open-source, free.
    NewsAPI: Free tier available for educational purposes (usage limits apply).

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
            f"Each project must have a unique difficulty level (1-easy, 2-medium, 3-hard)."
            f"Do NOT use A/B testing anywhere in the projects."
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
        max_tokens=1200,
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
    # rows = rows[rows['Tool'].isin(['BoTorch','Polars','Apache Arrow (PyArrow)','apache-tvm','Keras Tuner','tsfresh','Whisper Large V3','CausalInference','CausalML'])]
    # rows = rows[rows['Tool'].isin(['Caffe'])]
    for _, row in rows.iterrows():
        content = ""
        project_name = row["Tool"]
        description = _generate_project_description(
                project_name)
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
