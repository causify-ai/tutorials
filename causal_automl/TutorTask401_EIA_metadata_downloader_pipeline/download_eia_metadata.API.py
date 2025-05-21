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
#   - [EIA Metadata API Tutorial](#eia-metadata-api-tutorial)
#     - [Overview](#overview)
#     - [Why Use This Notebook](#why-use-this-notebook)
#     - [Requirements](#requirements)
#   - [Setup](#setup)
#     - [Imports](#imports)
#     - [Set Up API Key](#set-up-api-key)
#     - [Define Config](#define-config)
#   - [Load Metadata](#load-metadata)
#   - [Preview Metadata](#preview-metadata)
#   - [Construct Full URL from One Value per Facet](#construct-full-url-from-one-value-per-facet)

# %% [markdown]
# <a name='description'></a>
# # Description
#
# This notebook demonstrates how to use the `EiaMetadataDownloader` to extract and understand
# the metadata available via the EIA v2 API. It shows how to instantiate the downloader, run
# extraction, and preview the resulting metadata and facet structure.

# %% [markdown]
# <a name='requirements'></a>
# <a name='why-use-this-notebook'></a>
# <a name='overview'></a>
# <a name='eia-metadata-api-tutorial'></a>
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
# ### Why Use This Notebook
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
# 4. Set the key as an environment variable (see [Set Up API Key](#set-up-api-key)).

# %% [markdown]
# <a name='setup'></a>
# ## Setup

# %% [markdown]
# <a name='imports'></a>
# ### Imports

# %% vscode={"languageId": "plaintext"}
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

# %% vscode={"languageId": "plaintext"}
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
# <a name='load-metadata'></a>
# ## Load Metadata
#
# We instantiate the `EiaMetadataDownloader` with a specified category, API key, and version number.
#
# Then, we extract:
# - A metadata table containing dataset routes, metrics, and frequencies
# - A list of facet values required to construct valid API queries

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
# <a name='preview-metadata'></a>
# ## Preview Metadata
#
# Each dataset defines one or more facets, which are categorical dimensions used to filter time series data. A valid query must specify one value per required facet (e.g., `stateid=CA`, `sectorid=COM`).

# %% vscode={"languageId": "plaintext"}
# Preview metadata index.
df_metadata.head()

# %% vscode={"languageId": "plaintext"}
# Preview facet values.
df_facet = param_entries[0][0]
df_facet.head()

# %%
# Show unique facet types and sample values for each.
df_facet.groupby("facet_id").head(1)

# %% [markdown]
# <a name='construct-full-url-from-one-value-per-facet'></a>
# ## Construct Full URL from One Value per Facet

# %%
# Since the URL would expose the actual API key, we overwrite it with a placeholder for safe display.
api_key = "API_KEY"

# Select sample route.
meta = df_metadata.iloc[0]

# Select facet values.
facet_input = {"stateid": "IN", "sectorid": "OTH"}

# Build a query URL to retrieve actual time series values from the EIA API.
full_url = catemdpeu.build_full_url(
    base_url=meta["url"],
    api_key=api_key,
    facet_input=facet_input,
)
print(full_url)
