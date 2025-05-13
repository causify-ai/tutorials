# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# CONTENTS:
# - [Description](#description)
#   - [Contents](#contents)
#   - [Analyzing EIA Time Series Metadata](#analyzing-eia-time-series-metadata)
#     - [Introduction](#introduction)
#   - [Potential Applications](#potential-applications)
#   - [Setup](#setup)
#     - [Import Required Modules](#import-required-modules)
#     - [Set Up API Key](#set-up-api-key)
#   - [Define Config](#define-config)
#   - [Initialize Metadata Downloader](#initialize-metadata-downloader)
#   - [Extract Metadata](#extract-metadata)
#   - [Scenario 1: Visualize Metadata](#scenario-1:-visualize-metadata)
#     - [Preview Metadata](#preview-metadata)
#     - [Visualizations](#visualizations)
#   - [Wrap-up and Insights](#wrap-up-and-insights)
#     - [Key Takeaways:](#key-takeaways:)

# %% [markdown]
# <a name='description'></a>
# # Description
#
# This notebook demonstrates a real-world use of the `EiaMetadataDownloader` to extract metadata
# from the EIA v2 API, explore facet values, construct valid time series URLs, and preview data.
# It follows the KaizenFlow notebook style guide and showcases best practices for configuration,
# reproducibility, and insight generation.

# %% [markdown]
# <a name='contents'></a>
# ## Contents
# - [Introduction](#introduction)
# - [Potential Applications](#potential-applications)
# - [Setup](#setup)
#   - [Import Required Modules](#import-required-modules)
#   - [Set Up API Key](#set-up-api-key)
# - [Define Config](#define-config)
# - [Initialize Metadata Downloader](#initialize-metadata-downloader)
# - [Scenario 1: Metadata Insight](#scenario-1-metadata-insight)
# - [Wrap-up and Insights](#wrap-up-and-insights)

# %% [markdown]
# <a name='introduction'></a>
# <a name='analyzing-eia-time-series-metadata'></a>
# ## Analyzing EIA Time Series Metadata
#
# ### Introduction
#
# This notebook demonstrates how to use the `EiaMetadataDownloader` class to analyze and construct valid queries from the U.S. Energy Information Administration (EIA) v2 API.
# It enables data scientists, analysts, and engineers to extract structured metadata, explore available datasets, and build full queryable URLs for accessing time series data.
#
# The EIA v2 API provides metadata about datasets such as electricity consumption, pricing, and production across various regions and time frequencies.
# By programmatically accessing this metadata, you can:
# - Discover all frequency-metric combinations available for a dataset.
# - Retrieve valid facet (parameter) values like `state`, `sector`, or `provider`.
# - Construct full API requests to query time series data.
# - Automate ingestion and validation workflows for large-scale energy datasets.
#
# This notebook walks through a real scenario to demonstrate the utility of the metadata downloader.

# %% [markdown]
# <a name='potential-applications'></a>
# ## Potential Applications
#
# The EIA metadata downloader enables a wide range of analytical and operational tasks by making time series metadata programmatically accessible.
#
# Practical use cases include:
# - Creating dashboards that track the availability of new metrics or datasets over time.
# - Pre-validating which combinations of frequency, metric, and facets are supported before making data queries.
# - Automatically generating full EIA API URLs to feed into a data pipeline or fetcher script.
# - Supporting reproducible energy-related research with clear, programmatically obtained dataset references.

# %% [markdown]
# <a name='setup'></a>
# ## Setup
#
# In this section, we import all required Python libraries and ensure the system is ready to authenticate and run API calls.
#
# We rely on:
# - `pandas` for data manipulation.
# - `requests` for HTTP communication with the EIA API.### Import Required Modules
# - `eia_utils` as part of the project module tree.

# %% [markdown]
# <a name='import-required-modules'></a>
# ### Import Required Modules

# %%
# %load_ext autoreload
# %autoreload 2
import logging
import os

import helpers.hdbg as hdbg
import pandas as pd

import causal_automl.notebooks.TutorTask401_EIA_metadata_downloader_pipeline.eia_utils as cantemdpeu

# Enable logging.
logging.basicConfig(level=logging.INFO)
_LOG = logging.getLogger(__name__)

# %% [markdown]
# <a name='set-up-api-key'></a>
# ### Set Up API Key
#
# Store your **EIA API Key** as an environment variable for security. You can do this in your terminal:
#
# ```sh
# export EIA_API_KEY="your_personal_api_key"
# ```
#
# Alternatively, you can set it within the notebook:

# %%
# Set your GitHub access token here.
os.environ["EIA_API_KEY"] = ""

# Retrieve it when needed.
api_key = os.getenv("EIA_API_KEY")

# Ensure the token is set correctly.
if not api_key:
    raise ValueError(
        "EIA API key is not set. Please configure it before proceeding."
    )

# %% [markdown]
# <a name='define-config'></a>
# ## Define Config
#
# This section defines the key parameters that drive the metadata extraction:
#
# - `category`: The root category of interest from the EIA v2 API. Example: `"electricity"`, `"natural-gas"`, `"petroleum"`.
# - `version_num`: A version label used to tag output files or datasets.

# %%
# Define category and output version.
category = "electricity"
version_num = "1.0"

# %% [markdown]
# <a name='initialize-metadata-downloader'></a>
# ## Initialize Metadata Downloader
#
# We instantiate the `EiaMetadataDownloader` class using the configuration provided above.
#
# This object encapsulates all the logic needed to:
# - Traverse the EIA API tree
# - Extract relevant time series metadata
# - Retrieve valid facet values for downstream filtering

# %%
downloader = cantemdpeu.EiaMetadataDownloader(
    category=category,
    api_key=api_key,
    version_num=version_num,
)

# %% [markdown]
# <a name='extract-metadata'></a>
# ## Extract Metadata

# %%
df_metadata, param_entries = downloader.run_metadata_extraction()

# %% [markdown]
# <a name='scenario-1:-visualize-metadata'></a>
# ## Scenario 1: Visualize Metadata
#
# In this scenario, we explore and visualize the structure of the EIA metadata extracted from the API.
#
# We use the flattened metadata table to gain insights into:
# - The distribution of time series across different frequencies (e.g., monthly, annual)
# - The variety of units used to measure energy-related data (e.g., MWh, USD)
# - The number of time series available per dataset ID
#
# These visualizations help assess the coverage, granularity, and diversity of the available EIA datasets before constructing any time series queries.

# %% [markdown]
# <a name='preview-metadata'></a>
# ### Preview Metadata

# %%
df_metadata.head()

# %% [markdown]
# <a name='visualizations'></a>
# ### Visualizations

# %%
# Frequency distribution plot.
cantemdpeu.plot_distribution(
    df_metadata, column="frequency_id", title="Distribution of Frequencies"
)

# Units distribution plot.
cantemdpeu.plot_distribution(
    df_metadata, column="data_units", title="Distribution of Data Units"
)

# Number of time serires per dataset plot.
cantemdpeu.plot_distribution(
    df_metadata, column="dataset_id", title="Number of Time Series per Dataset"
)

# %% [markdown]
# <a name='key-takeaways:'></a>
# <a name='wrap-up-and-insights'></a>
# ## Wrap-up and Insights
#
# In this scenario, we explored the structure of the EIA metadata to understand the coverage and richness of available datasets.
#
# ### Key Takeaways:
#
# - The flattened metadata table (`df_metadata`) reveals the number of time series per dataset, each defined by a unique combination of frequency and metric.
# - Distributions of `frequency_id` and `data_units` give insight into the granularity (e.g., monthly, annual) and measurement types (e.g., MWh, USD) used across EIA datasets.
# - Grouping by `dataset_id` showed how some datasets expose more metric-frequency combinations than others, which is useful when prioritizing which datasets to ingest or analyze further.
#
# By analyzing just the metadata, we can assess the overall shape and availability of EIA time series without needing to fetch any actual data. This is especially useful for exploratory analysis, schema understanding, and preparing batch download logic.
#
