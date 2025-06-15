# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.7
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# CONTENTS:
# - [Description](#description)
#   - [Analyzing EIA Time Series Metadata](#analyzing-eia-time-series-metadata)
#     - [Introduction](#introduction)
#     - [Potential Applications](#potential-applications)
#   - [Setup](#setup)
#     - [Imports](#imports)
#     - [Set Up API Key](#set-up-api-key)
#     - [Define Config](#define-config)
#   - [Load Metadata](#load-metadata)
#   - [Visualize Metadata](#visualize-metadata)
#   - [Wrap-up and Insights](#wrap-up-and-insights)
#     - [Key Takeaways](#key-takeaways)

# %% [markdown]
# <a name='description'></a>
# # Description
#
# This notebook demonstrates how to extract and visualize structured metadata from the U.S. Energy Information Administration (EIA) v2 API using the `EiaMetadataDownloader`. It covers how to preview available time series, explore supported frequencies and metrics.

# %% [markdown]
# <a name='analyzing-eia-time-series-metadata'></a>
# ## Analyzing EIA Time Series Metadata

# %% [markdown]
# <a name='introduction'></a>
# ### Introduction
#
# This notebook demonstrates how to use the `EiaMetadataDownloader` class to analyze and construct valid queries from the U.S. Energy Information Administration (EIA) v2 API.
# It enables data scientists, analysts, and engineers to extract structured metadata, explore available datasets, and build full queryable URLs for accessing time series data.
#
# The EIA v2 API provides metadata about datasets such as electricity consumption, pricing, and production across various regions and time frequencies.
# By programmatically accessing this metadata, you can:
# - Discover all frequency-metric combinations available for a dataset
# - Retrieve the list of required facet types (e.g., `stateid`, `sectorid`) for each dataset
# - Construct full API requests to query time series data
# - Automate ingestion by generating API URLs using metadata, even though data availability must still be verified after making the request
#
# This notebook walks through a real-world use case to demonstrate the utility of the metadata downloader.

# %% [markdown]
# <a name='potential-applications'></a>
# ### Potential Applications
#
# The EIA metadata downloader enables a wide range of analytical and operational tasks by making time series metadata programmatically accessible.
#
# Practical use cases include:
# - Creating dashboards that track the availability of new metrics or datasets over time
# - Automatically generating full EIA API URLs to feed into a data pipeline or fetcher script
# - Supporting reproducible energy-related research with clear, programmatically obtained dataset references

# %% [markdown]
# <a name='setup'></a>
# ## Setup

# %% [markdown]
# <a name='imports'></a>
# ### Imports

# %%
# %load_ext autoreload
# %autoreload 2
import logging
import os

import helpers.hdbg as hdbg

import causal_automl.TutorTask401_EIA_metadata_downloader_pipeline.eia_utils as catemdpeu

# Enable logging.
hdbg.init_logger(verbosity=logging.INFO)
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
# Set your EIA api key here.
os.environ["EIA_API_KEY"] = ""

# %%
# Ensure the api key is set correctly.
hdbg.dassert_in(
    "EIA_API_KEY", os.environ, msg="Missing environment variable EIA_API_KEY."
)

# Retrieve it when needed.
api_key = os.getenv("EIA_API_KEY")

# %% [markdown]
# <a name='define-config'></a>
# ### Define Config
#
# This section defines the key parameters that drive the metadata extraction:
#
# - `category`: The root category of interest from the EIA v2 API. Example: `"electricity"`, `"natural-gas"`, `"petroleum"`
# - `version_num`: A version label used to tag output files or datasets

# %%
# Define category and output version.
category = "electricity"
version_num = "1.0"

# %% [markdown]
# <a name='load-metadata'></a>
# ## Load Metadata
#
# We instantiate the `EiaMetadataDownloader` with a specified category, API key, and version number.
#
# Then, we extract:
# - A metadata table containing dataset routes, metrics, and frequencies
# - A list of facet values required to construct API queries

# %% vscode={"languageId": "plaintext"}
# Initialize metadata downloader.
downloader = catemdpeu.EiaMetadataDownloader(
    category=category,
    api_key=api_key,
    version_num=version_num,
)

# %% vscode={"languageId": "plaintext"}
# Extract metadata.
df_metadata, param_entries = downloader.run_metadata_extraction()

# %% [markdown]
# <a name='visualize-metadata'></a>
# ## Visualize Metadata
#
# In this section, we explore and visualize the structure of the EIA metadata extracted from the API.
#
# We use the flattened metadata table to gain insights into:
# - The distribution of time series across different frequencies (e.g., monthly, annual)
# - The variety of units used to measure energy-related data (e.g., MWh, USD)
# - The number of time series available per dataset ID
#
# These visualizations help assess the coverage, granularity, and diversity of the available EIA datasets before constructing any time series queries.

# %%
# Preview metadata.
df_metadata.head()

# %%
# Frequency distribution plot.
catemdpeu.plot_distribution(
    df_metadata, column="frequency_id", title="Distribution of Frequencies"
)

# Units distribution plot.
catemdpeu.plot_distribution(
    df_metadata, column="data_units", title="Distribution of Data Units"
)

# Number of time serires per dataset plot.
catemdpeu.plot_distribution(
    df_metadata, column="dataset_id", title="Number of Time Series per Dataset"
)

# %% [markdown]
# <a name='wrap-up-and-insights'></a>
# ## Wrap-up and Insights
#
# In this section, we explored the structure of the EIA metadata to understand the coverage and richness of available datasets.

# %% [markdown]
# <a name='key-takeaways'></a>
# ### Key Takeaways
#
# - The flattened metadata table (`df_metadata`) reveals the number of time series per dataset, each defined by a unique combination of frequency and metric
# - Distributions of `frequency_id` and `data_units` give insight into the granularity (e.g., monthly, annual) and measurement types (e.g., MWh, USD) used across EIA datasets
# - Grouping by `dataset_id` showed how some datasets expose more metric-frequency combinations than others, which is useful when prioritizing which datasets to ingest or analyze further
#
# By analyzing just the metadata, we can assess the overall shape and availability of EIA time series without needing to fetch any actual data. This is especially useful for exploratory analysis, schema understanding, and preparing batch download logic.
