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
# # Description
#
# This notebook demonstrates how to use the `EiaMetadataDownloader` to extract and understand
# the metadata available via the EIA v2 API. It shows how to instantiate the downloader, run
# extraction, and preview the resulting metadata and facet structure.

# %% [markdown]
# ## Contents
# - [EIA Metadata API Tutorial](#eia-metadata-api-tutorial)
#   - [Overview](#overview)
#   - [Why Use This Notebook?](#why-use-this-notebook)
#   - [Requirements](#requirements)
# - [Setup](#setup)
#   - [Import Required Modules](#import-required-modules)
#   - [Set Up API Key](#set-up-api-key)
# - [Define Config](#define-config)
# - [Initialize Metadata Downloader](#initialize-metadata-downloader)
# - [Run Metadata Extraction](#run-metadata-extraction)
# - [Preview Flattened Metadata](#preview-flattened-metadata)
# - [Preview Facet Values](#preview-facet-values)
# - [Group and Preview Facet Values by Facet Type](#group-and-preview-facet-values-by-facet-type)
# - [Construct Sample EIA URL](#construct-sample-eia-url)

# %% [markdown]
# ## EIA Metadata API Tutorial
#
# ### Overview
#
# In this notebook, you'll learn how to:
#
# - Connect to the [EIA v2 API](https://www.eia.gov/opendata/) using a Python client.
# - Traverse API categories to find available datasets.
# - Retrieve and flatten metadata including frequency, available metrics, and facet dimensions.
# - Access parameter values for facets such as state, sector, or energy type.
#
# ### Why Use This Notebook?
#
# - Automate the discovery of available EIA datasets without browsing the web interface.
# - Generate all valid combinations of time series from EIA metadata.
# - Understand how to construct API requests for specific metrics and filters.
#
# ### Requirements
#
# To authenticate and interact with the EIA API, you'll need an API key. Follow these steps:
#
# 1. Visit the [EIA registration page](https://www.eia.gov/opendata/register.php).
# 2. Enter your email address and submit the form.
# 3. You'll receive a key via email—this key is used as a query parameter in all API requests.
# 4. Set the key as an environment variable:

# %% [markdown]
# ## Setup

# %% [markdown]
# ### Import Required Modules

# %% vscode={"languageId": "plaintext"}
# %load_ext autoreload
# %autoreload 2
import logging
import os

import eia_utils as eiu

# Enable logging.
logging.basicConfig(level=logging.INFO)
_LOG = logging.getLogger(__name__)

# %% [markdown]
# ### Set Up API Key
#
# Store your **EIA API Key** as an environment variable for security. You can do this in your terminal:
#
# ```sh
# export EIA_API_KEY="your_personal_api_key"
# ```
#
# Alternatively, you can set it within the notebook:

# %% vscode={"languageId": "plaintext"}
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
# ## Define Config
#
# In this section, we define the configuration used by the downloader:
#
# - `category`: The root category path under the EIA v2 API. Examples include `electricity`, `petroleum`, `natural-gas`, etc.
# - `version_num`: A version string to tag outputs. This is used in filenames and S3 paths.
#
# These inputs help parameterize the metadata extraction process and keep output files versioned.

# %% vscode={"languageId": "plaintext"}
# Define category and output version.
category = "electricity"
version_num = "1.0"

# %% [markdown]
# ## Initialize Metadata Downloader

# %% vscode={"languageId": "plaintext"}
downloader = eiu.EiaMetadataDownloader(
    category=category,
    api_key=api_key,
    version_num=version_num,
)

# %% [markdown]
# ## Run Metadata Extraction

# %% vscode={"languageId": "plaintext"}
df_metadata, param_entries = downloader.run_metadata_extraction()

# %% [markdown]
# ## Preview Metadata

# %% vscode={"languageId": "plaintext"}
df_metadata.head()

# %% [markdown]
# ## Preview Facet Values

# %% vscode={"languageId": "plaintext"}
df_facet = param_entries[0][0]
df_facet.head()

# %% [markdown]
# ## Group and Preview Facet Values by Facet Type

# %%
# Show unique facet types and sample values for each.
df_facet.groupby("facet_id").head(1)

# %% [markdown]
# ## Construct Full URL from One Value per Facet

# %%
# Select sample route.
meta = df_metadata.iloc[0]

# Select facet values.
facet_input = {"stateid": "IN", "sectorid": "OTH"}

# Build URL.
full_url = eiu.build_full_url(
    base_url=meta["url"],
    df_facets=df_facet,
    api_key=api_key,
    facet_input=facet_input,
)
