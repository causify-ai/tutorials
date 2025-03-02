"""
Import as:

import DATA605.project_description as dprodesc
"""

import logging
import os

import helpers.hgoogle_file_api as hgofiapi
import helpers.hio as hio
import helpers.hopenai as hopenai
import pandas as pd

_LOG = logging.getLogger(__name__)

# Constants.
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1Ez5uRvOgvDMkFc9c6mI21kscTKnpiCSh4UkUh_ifLIw/edit?gid=0#gid=0"
PROMPT_DOC_URL = """
You are a college professor of Data science. In the next prompt I will give you a topic XYZ for a class project and you will write a description using bullet points for a college class project about implementing an example big data system in Python.

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

An example of a project where XYZ is “AWS Glue” is the following

Title: Ingest bitcoin prices using AWS Glue
Description
AWS Glue is a fully managed extract, transform, and load (ETL) service provided by Amazon Web Services (AWS). It helps you prepare and transform data for analytics, machine learning, and other data processing tasks. Understand AWS Glue's core concepts, including data catalogs, crawlers, and jobs
An easy project that can be completed in one week involves using AWS Glue to ingest Bitcoin price data from a public API, such as CoinGecko, and store it in an S3 bucket for further analysis. The first step of the project is to set up an AWS Glue crawler to automatically discover and catalog the incoming JSON data. Students will configure the crawler to run on a schedule to continuously fetch new Bitcoin price data from the API every few minutes. They will store the data in an S3 bucket and create a Glue Data Catalog to manage the dataset’s schema. Then, a simple AWS Glue job can be written using Python (with PySpark) to process and transform the raw data, such as filtering the data for specific time intervals or adding new fields, like the price change over time. Finally, the processed data can be stored back in S3 in a more structured format (e.g., Parquet) for easy querying. This project gives students hands-on experience with AWS Glue and basic ETL processes while learning how to handle real-time data ingestion.
Difficulty: easy (it should take around one week)
Useful links
Is it free?
You need to create an AWS account. AWS Glue offers a free tier, but it comes with some limitations.
Python libraries / bindings
To use AWS Glue with Python, the primary resource you'll need is boto3, the official AWS SDK for Python, which allows you to interact programmatically with AWS Glue services, such as creating and managing Glue jobs, crawlers, and data catalogs. You can install boto3 using pip install boto3. For processing and transforming data within AWS Glue jobs, you'll use PySpark, which is the Python API for Apache Spark. AWS Glue automatically provides a managed Spark environment, so you don't need to install PySpark locally; you simply write your ETL scripts using PySpark within Glue's job editor. Additionally, AWS Glue provides its own Python library, AWS Glue Python Library, which includes utilities for managing Glue jobs, handling data transformations, and interacting with the Glue Data Catalog. These resources together enable you to build, schedule, and execute ETL jobs for large-scale data processing in a serverless environment.
boto3 (AWS SDK for Python): The official Python SDK for interacting with AWS services, including AWS Glue. It provides tools to create, manage, and monitor Glue jobs, crawlers, and data catalogs.  AWS boto3 Documentation
PySpark: A Python API for Apache Spark, used for writing distributed data processing scripts in AWS Glue. PySpark is key for data transformation within Glue jobs.  PySpark Documentation
AWS Glue Python Library: A specialized library in AWS Glue for managing and transforming data, including utilities for Glue-specific tasks such as working with the Glue Data Catalog and executing ETL jobs. AWS Glue Python API Reference
"""
MARKDOWN_FILE_PATH = "./projects/DATA605_Projects.md"
# The maximum number of projects.
# Set the value to None to disable the limit.
MAX_PROJECTS = 5


def read_google_sheet(url: str) -> pd.DataFrame:
    """
    Read the Google Sheet and return the data as a pandas DataFrame.

    :param url: the URL of the Google Sheet to read
    :return: df containing the data
    """
    credentials = hgofiapi.get_credentials(
        service_key_path="/app/DATA605/google_secret.json"
    )
    df = hgofiapi.read_google_file(url, credentials=credentials)
    return df


def generate_project_description(project_name: str, difficulty: str) -> str:
    """
    Generate a project description.

    :param project_name: the name of the project
    :param difficulty: the difficulty level of the project
    :return: the project description
    """
    # Generate the project description.
    prompt = f"Generate a project description for '{project_name}' with difficulty level '{difficulty}'."
    description = hopenai.get_completion(prompt, model="gpt-4o-mini")
    return description


def create_markdown_file(df: pd.DataFrame, markdown_file_path: str) -> None:
    """
    Create a markdown file with the project descriptions using helpers.hio.

    :param df: the dataframe containing the project descriptions
    :param markdown_file_path: the path to the markdown file
    """
    content = "# DATA605 Projects\n\n"
    # Generate the project descriptions.
    # Limit the number of projects.
    for _, row in df.head(
        MAX_PROJECTS if MAX_PROJECTS is not None else len(df)
    ).iterrows():
        project_name = row["Project name"]
        difficulty = row["Difficulty"]
        description = generate_project_description(project_name, difficulty)
        # Add the project description to the markdown file.
        content += f"## {project_name}\n"
        content += f"**Difficulty:** {difficulty}\n\n"
        content += f"{description}\n\n"
    # Write the markdown file.
    hio.to_file(markdown_file_path, content)


def main():
    # Read the Google Sheet.
    df = read_google_sheet(GOOGLE_SHEET_URL)
    # Create the markdown file.
    create_markdown_file(df, MARKDOWN_FILE_PATH)
    _LOG.info(f"Markdown file created at {MARKDOWN_FILE_PATH}")


if __name__ == "__main__":
    main()