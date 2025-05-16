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
# - [Exploratory Data Analysis: EIA Metadata](#exploratory-data-analysis:-eia-metadata)
#   - [Introduction](#introduction)
#   - [Imports](#imports)
#   - [Helper Functions](#helper-functions)
#   - [Load and Preprocess Data](#load-and-preprocess-data)
#   - [Introductory Analytics](#introductory-analytics)
#     - [Preview Data](#preview-data)
#       - [EIA Metadata Index Column information](#eia-metadata-index-column-information)
#       - [EIA Parameters Column information](#eia-parameters-column-information)
#     - [Missing Data](#missing-data)
#   - [Exploratory Analysis](#exploratory-analysis)
#     - [Distribution Analyses](#distribution-analyses)
#       - [Distribution by Dataset](#distribution-by-dataset)
#       - [Distribution by Frequency](#distribution-by-frequency)
#       - [Distribution by Unit](#distribution-by-unit)
#     - [Coverage Analysis](#coverage-analysis)
#       - [Distribution by Timespan (Years)](#distribution-by-timespan-(years))
#       - [Distribution by Time Series Start Period](#distribution-by-time-series-start-period)
#       - [Distribution by Time Series End Period](#distribution-by-time-series-end-period)
#     - [Facet Analysis](#facet-analysis)
#       - [Top Facets](#top-facets)
#       - [Facet Usage Across Dataset](#facet-usage-across-dataset)
#       - [Facet Cardinalities](#facet-cardinalities)
#       - [Temporal Resolution Coverage by Dataset](#temporal-resolution-coverage-by-dataset)

# %% [markdown]
# Contents:
#

# %% [markdown]
# <a name='exploratory-data-analysis:-eia-metadata'></a>
# # Exploratory Data Analysis: EIA Metadata

# %% [markdown]
# <a name='introduction'></a>
# ## Introduction
#
# This notebook analyzes the U.S. Energy Information Administration (EIA) electricity metadata retrieved from the v2 API. The goal is to understand how time series are structured across datasets, frequencies, and facet dimensions to support downstream data exploration and analysis.

# %% [markdown]
# <a name='imports'></a>
# ## Imports

# %%
# %load_ext autoreload
# %autoreload 2
import logging
import os
import io
import ast
from typing import Tuple, Dict, List

import helpers.hdbg as hdbg
import helpers.henv as henv
import helpers.hprint as hprint
import helpers.hs3 as hs3
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

import causal_automl.eda_utils as caueduti

# %%
# Configure logger.
hdbg.init_logger(verbosity=logging.INFO)
_LOG = logging.getLogger(__name__)

# Configure the notebook style.
hprint.config_notebook()

# Configure S3.
s3_dir = "s3://causify-data-collaborators/causal_automl/metadata/"
aws_profile = "ck"


# %% [markdown]
# <a name='helper-functions'></a>
# ## Helper Functions

# %%
def _get_missing_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns a summary of missing value count and percentage per column.

    :param df: data to inspect
    :return: data with count and percentage of missing values
    """
    count = df.isna().sum()
    percent = df.isna().mean() * 100
    missing_count = pd.DataFrame({'Missing Count': count, 'Missing %': percent}).sort_values(by="Missing %", ascending=False)
    missing_columns_df = missing_count[
        missing_count["Missing Count"] > 0
    ]
    return missing_columns_df

def _plot_distribution(df_metadata: pd.DataFrame, column: str, title: str) -> None:
    """
    Plot a distribution count for a specified metadata column.

    :param df_metadata: metadata table containing time series fields
    :param column: column to group and count values by (e.g.,
        'frequency_id', 'data_units')
    :param title: title for the plot
    """
    if column not in df_metadata.columns:
        raise ValueError(f"Column '{column}' not found in df_metadata.")
    counts = df_metadata[column].value_counts()
    caueduti.plot_top_n_annotated_bar(
        counts=counts,
        total=len(df_metadata),
        top_n=len(counts),
        title=title,
        xlabel=column.replace("_", " ").title(),
        ylabel="Count",
        wrap_width=35,
        rotation=30,
    )


# %% [markdown]
# <a name='load-and-preprocess-data'></a>
# ## Load and Preprocess Data

# %%
def _load_data(file_path: str, aws_profile:str) -> pd.DataFrame:
    """
    Load data from file path to a DataFrame.

    :param file_path: path of the data to load from
    :param aws_profile: AWS CLI profile used for access
    :return: DataFrame of the loaded data
    """
    file = hs3.from_file(file_path, aws_profile=aws_profile)
    df = pd.read_csv(io.StringIO(file))
    return df

def _load_eia_metadata_and_parameters(
    s3_dir: str,
    metadata_file_path: str,
    parameter_subdir: str,
    aws_profile: str,
) -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
    """
    Load EIA metadata and parameter files from S3.

    :param s3_dir: base S3 directory (e.g., "s3://mybucket/data/")
    :param metadata_file: metadata CSV filename (e.g., "eia_metadata.csv")
    :param parameter_subdir: subdirectory in `s3_dir` containing parameter files
    :param aws_profile: AWS CLI profile used for access
    :return: metadata and parameter DataFrames
    """
    # Load metadata CSV.
    metadata_path = os.path.join(s3_dir, metadata_file_path)
    df_metadata = _load_data(metadata_path, aws_profile)
    # Load all parameter CSVs.
    parameter_dir = os.path.join(s3_dir, parameter_subdir)
    s3fs_ = hs3.get_s3fs(aws_profile)
    param_paths = s3fs_.ls(parameter_dir)
    param_dfs = {}
    for path in param_paths:
        if path.endswith(".csv"):
            key = os.path.basename(path).replace("_parameters.csv", "")
            full_path = f"s3://{path}"
            param_dfs[key] = _load_data(full_path, aws_profile)
    return df_metadata, param_dfs

def _normalize_facets(facets: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Normalize similar facet values.

    :param facets: facets to process
    :return: normalized facets
    """
    for facet in facets:
        if facet["id"].lower() in {"state", "stateid", "stateID"}:
            facet["id"] = "stateid"
    return facets

def _preprocess_eia(
    df_metadata: pd.DataFrame,
    param_dfs: Dict[str, pd.DataFrame],
) -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
    """
    Preprocess metadata and parameter DataFrames for analysis.

    :param df_metadata: metadata index DataFrame
    :param param_dfs: parameter DataFrames
    :return: cleaned metadata and parameter DataFrames
    """
    # Preprocess metadata.
    df_metadata["frequency_id"] = df_metadata["frequency_id"].str.lower().str.strip()
    # Parse facets column if stored as string.
    df_metadata["facets"] = df_metadata["facets"].apply(ast.literal_eval)
    # Normalize similar variables.
    df_metadata["facets"] = df_metadata["facets"].map(_normalize_facets)
    # Preprocess parameters.
    param_dfs_cleaned = {}
    for file_name, df_param in param_dfs.items():
        df_param_cleaned = df_param.copy()
        # Standardized field with normalized variables.
        df_param_cleaned["facet_id"] = (
            df_param_cleaned["facet_id"]
            .astype(str)
            .str.strip()
            .str.lower()
            .replace({"state": "stateid", "stateid": "stateid", "stateid": "stateid"})
        )
        # Strip and clean id field in known affected file.
        df_param_cleaned["id"] = df_param_cleaned["id"].astype(str).str.strip()
        param_dfs_cleaned[file_name] = df_param_cleaned
    return df_metadata, param_dfs_cleaned


# %%
# Load EIA metadata index and parameters.
metadata_s3_path = f"eia_electricity_metadata_original_v1.0.csv"
param_s3_dir = f"eia_parameters_v1.0"
df_metadata, param_dfs = _load_eia_metadata_and_parameters(s3_dir, metadata_s3_path, param_s3_dir, aws_profile)
# Preprocess EIA metadata index and parameters.
df_metadata, param_dfs = _preprocess_eia(df_metadata, param_dfs)

# %% [markdown]
# <a name='introductory-analytics'></a>
# ## Introductory Analytics

# %% [markdown]
# <a name='preview-data'></a>
# ### Preview Data

# %%
# Preview metadata.
print(f"Number of time series: {len(df_metadata)}")
print(f"Number of columns: {df_metadata.shape[1]}")
print(f"Number of unique datasets: {df_metadata['dataset_id'].nunique()}")
df_metadata.head()

# %% [markdown]
# <a name='eia-metadata-index-column-information'></a>
# #### EIA Metadata Index Column information
#
# | **Column**              | **Description**                                                                 |
# |-------------------------|---------------------------------------------------------------------------------|
# | `url`                   | Full API URL to access the time series.                                         |
# | `id`                    | Unique identifier for the time series.                                          |
# | `dataset_id`            | Dataset group this series belongs to.                                           |
# | `name`                  | Human-readable title of the time series.                                        |
# | `description`           | Full description of what the time series measures.                              |
# | `frequency_id`          | Frequency label (e.g. `monthly`, `quarterly`, `hourly`).                        |
# | `frequency_alias`       | Alternative frequency name (often missing).                                     |
# | `frequency_description` | Sentence-style explanation of frequency (e.g. "One data point for each month"). |
# | `frequency_query`       | Query shorthand for frequency (e.g. `M` for monthly).                           |
# | `frequency_format`      | Formatting string used in time index.                                           |
# | `facets`                | JSON-style list of dimension fields used for the series.                        |
# | `data`                  | Short name of the measured value (e.g. `revenue`, `sales`).                     |
# | `data_alias`            | Human-readable version of the data name.                                        |
# | `data_units`            | Units of measurement (e.g. `million dollars`, `cents per kWh`).                 |
# | `start_period`          | Start date of available data (YYYY-MM format).                                  |
# | `end_period`            | End date of available data (YYYY-MM format).                                    |
# | `parameter_values_file` | S3 path to facet value mappings for this dataset.                               |
#

# %%
# Available parameter datasets.
print("Available parameter datasets:")
for name in sorted(param_dfs.keys()):
    print(f"- {name}")
# Preview one parameter file.
param_dfs["retail_sales"].head()

# %% [markdown]
# <a name='eia-parameters-column-information'></a>
# #### EIA Parameters Column information
#
# | **Column**         | **Description**                                                                 |
# |--------------------|---------------------------------------------------------------------------------|
# | `dataset_id`       | Name of the parent dataset this parameter file belongs to (e.g. `retail_sales`). |
# | `facet_id`         | The dimension or facet described (e.g. `stateid`, `sectorid`).                   |
# | `id`               | The unique code or shorthand for the facet value (e.g. `CA`, `RES`).             |
# | `name`             | Plain name of the facet value (e.g. `California`, `residential`).                |
# | `alias`            | Display-friendly name or formatted version of the value.                |
#

# %% [markdown]
# <a name='missing-data'></a>
# ### Missing Data

# %%
# Calculate missing counts and percentages.
missing_count = _get_missing_summary(df_metadata)
display(missing_count)
# Plot percentage of missing value.
caueduti.plot_top_n_annotated_bar(
    counts=missing_count["Missing Count"],
    total=len(df_metadata),
    top_n=len(missing_count),
    title="Missing Values per Column",
    xlabel="Column",
    ylabel="Missing Count",
    wrap_width=None,
    rotation=0,
)

# %% [markdown]
# Only three columns contain missing values: `frequency_alias`, `data_units`, and `data_alias`, with 95.3%, 36.0% and 0.6% missing values respectively. The missing `frequency_alias` and `data_alias` are not essential, as they serve only as display-friendly labels. While `data_units` is more relevant for interpreting values (e.g., whether a series is in MW or MWh), it is often redundant with dataset context and not required for structural analysis.

# %% [markdown]
# <a name='exploratory-analysis'></a>
# ## Exploratory Analysis

# %% [markdown]
# <a name='distribution-analyses'></a>
# ### Distribution Analyses

# %% [markdown]
# <a name='distribution-by-dataset'></a>
# #### Distribution by Dataset
#
# The time series in the EIA electricity metadata originate from 19 distinct datasets, with the majority concentrated in a few categories. Notably, `electric_power_operational_data` and `summary` together account for nearly half of all parameter entries, suggesting they are the most comprehensive or widely used sources. In contrast, many other datasets contribute only a small number of entries, suggesting they are more specialized or narrowly scoped. This skewed distribution highlights key datasets likely to dominate downstream analysis.

# %%
_plot_distribution(df_metadata, "dataset_id", "Distribution of Categories")

# %% [markdown]
# <a name='distribution-by-frequency'></a>
# #### Distribution by Frequency
#
# The dataset predominantly consists of annual (55.8%), monthly (22.1%), and quarterly (15.1%) time series, which together account for over 93% of the metadata. High-frequency data such as hourly and daily are rare, indicating the EIA primarily publishes coarse-grained electricity statistics rather than fine-grained real-time series.

# %%
_plot_distribution(df_metadata, "frequency_id", "Distribution of Frequency")

# %% [markdown]
# <a name='distribution-by-unit'></a>
# #### Distribution by Unit
#
# The EIA electricity metadata is dominated by energy-related units, with `megawatthours` alone accounting for 26.7% of all time series. The top 16 units cover 64% of the data, indicating a moderate concentration across physical, economic, and environmental metrics. This suggests the dataset primarily captures electricity usage and generation, but also includes financial and emissions indicators. Analysts should be mindful of unit differences when comparing or aggregating series.

# %%
_plot_distribution(df_metadata, "data_units", "Distribution of Data Units")

# %% [markdown]
# <a name='coverage-analysis'></a>
# ### Coverage Analysis

# %% [markdown]
# <a name='distribution-by-timespan-(years)'></a>
# #### Distribution by Timespan (Years)
#
# Most time series in the dataset span around 25 years, indicating strong long-term data coverage. There are smaller peaks at approximately 15 and 33 years, suggesting that some datasets began earlier or were added more recently. Very few time series have less than 10 years of data, making this collection well-suited for historical trend analysis. The consistency in duration enhances its utility for longitudinal studies and forecasting tasks.

# %%
# Compute time span.
df_metadata["start_period_year"] = df_metadata["start_period"].str.extract(r"(\d{4})").astype(float)
df_metadata["end_period_year"] = df_metadata["end_period"].str.extract(r"(\d{4})").astype(float)
df_metadata["timespan_years"] = df_metadata["end_period_year"] - df_metadata["start_period_year"]
# Plot histogram of time spans.
caueduti.plot_histograms(
    data_series=[df_metadata["timespan_years"]],
    labels=["All Series"],
    colors=["C0"],
    bins=10,
    xlabel="Years of Coverage",
    title="Distribution of Timespan (Years)",
    figsize=(12, 6)
)

# %% [markdown]
# <a name='distribution-by-time-series-start-period'></a>
# #### Distribution by Time Series Start Period
#
# The distribution shows that most time series began around 2000–2001, suggesting a major expansion or standardization effort during that period. A smaller spike appears in 2008, possibly tied to policy or market shifts. After 2010, new series became increasingly rare, indicating a stabilization in data collection. Very few series started before 1995, likely due to limited historical digitization.

# %%
caueduti.plot_histograms(
    data_series=[df_metadata["start_period_year"]],
    labels=["Start Year"],
    colors=["C0"],
    bins=10,
    kde=True,
    xlabel="Year",
    title="Distribution of Time Series Start Year",
    figsize=(12, 6)
)

# %% [markdown]
# <a name='distribution-by-time-series-end-period'></a>
# #### Distribution by Time Series End Period
#
# The distribution of time series end years is highly concentrated in just two years: 2023 and 2025. This sharp clustering suggests that these values are likely system-generated or administrative placeholders rather than natural discontinuation points. Unlike the more varied start year distribution, the end year pattern indicates a bulk update or scheduled metadata cutoff. This means that not all of the series are necessarily discontinued, as 2023 may still be too recent to make that assumption. Therefore, we assume that all time series are still active and not discontinued.

# %%
caueduti.plot_histograms(
    data_series=[df_metadata["end_period_year"]],
    labels=["End Year"],
    colors=["C0"],
    bins=10,
    kde=True,
    xlabel="Year",
    title="Distribution of Time Series Start Year",
    figsize=(12, 6)
)

# %% [markdown]
# <a name='facet-analysis'></a>
# ### Facet Analysis

# %% [markdown]
# <a name='top-facets'></a>
# #### Top Facets
#
# The distribution of facets used across EIA time series reveals that `stateid` is by far the most common, appearing in nearly 67% of series, indicating strong geographic granularity. Other frequently used facets include `sectorid`, `fueltypeid`, and `location`, suggesting that categorization by usage sector and fuel classification is also central to the dataset structure. The presence of technical identifiers like `plantCode`, `generatorid`, and `primeMover` highlights the detailed operational scope of certain datasets. Overall, the top 15 facets cover over 250% of the time series, confirming that most series are tagged with multiple dimensions for richer filtering and analysis.

# %%
# Calculate facets count.
df_facet = df_metadata[["facets"]].explode("facets").copy()
df_facet["facet_id"] = df_facet["facets"].map(lambda f: f["id"])
facet_counts = df_facet.groupby("facet_id").size().sort_values(ascending=False)
# Plot bar chart of top facets.
caueduti.plot_top_n_annotated_bar(
    counts=facet_counts,
    total=len(df_metadata),
    top_n=15,
    title="Top Facets Used in EIA Time Series",
    xlabel="Facet ID",
    ylabel="Count",
    rotation=45,
    wrap_width=30,
)

# %% [markdown]
# <a name='facet-usage-across-dataset'></a>
# #### Facet Usage Across Dataset
#
# The heatmap visualizes the presence or absence of each facet ID across EIA datasets. Some facets like `stateid`, `sectorid`, and `plantCode` appear across multiple datasets, highlighting their importance in disaggregating and analyzing energy data. Conversely, many datasets use a small, distinct subset of facets—suggesting that different datasets are specialized for particular use cases. For example, retail_sales is richly annotated, while others like summary or facility_fuel are more minimalistic. This heterogeneity underscores the need for dataset-specific handling when performing cross-dataset analysis.

# %%
# Create data pairing dataset and facets.
df_dataset_facet = (
    df_metadata[["dataset_id", "facets"]]
    .explode("facets")
    .assign(facet_id=lambda d: d["facets"].map(lambda f: f["id"]))
    .drop(columns="facets")
    .drop_duplicates()
)
# Create crosstab of facet presence per dataset.
facet_crosstab = pd.crosstab(df_dataset_facet["dataset_id"], df_dataset_facet["facet_id"])
# Plot heatmap of dataset and facet pair.
caueduti.plot_heatmap(
    matrix=facet_crosstab,
    annot=False,
    cmap="Blues",
    title="Facet Usage Across Datasets",
    xlabel="Facet ID",
    ylabel="Dataset ID",
    figsize=(16, 8)
)

# %% [markdown]
# <a name='facet-cardinalities'></a>
# #### Facet Cardinalities
#
# The graph shows the number of unique values each facet contributes across EIA datasets. It reveals that two facets, `operating_generator_capacity` and `facility_fuel`, dominate the total unique value count, indicating they hold highly granular or identifier-like data. This suggests most facets are used for grouping or filtering, while a few may require special handling due to their cardinality.
#
# - **Heavy Skew in Cardinality**: The `operating_generator_capacity` facet alone accounts for about 64% of all unique values, indicating extreme cardinality.
# - **Interpretability Gap**: High-cardinality facets likely represent opaque identifiers, whereas low-cardinality facets are more interpretable and suitable for grouping.
# - **Storage Implications**: The disproportionate cardinality in a few facets can strain indexing and querying performance.
# - **Modeling Caution**: These high-cardinality fields should be handled carefully in data modeling to avoid overfitting or inefficient joins. Facets like `operating_generator_capacity` may lead to row explosion in joins if not normalized or managed properly.

# %%
# Compute number of unique values for each facet.
facet_cardinalities = {}
for facet_id, df_param in param_dfs.items():
    unique_count = df_param["id"].nunique()
    facet_cardinalities[facet_id] = unique_count
facet_card_series = pd.Series(facet_cardinalities).sort_values(ascending=False)
# Plot bar chart of unique values.
caueduti.plot_top_n_annotated_bar(
    counts=facet_card_series,
    total=facet_card_series.sum(),
    top_n=len(facet_card_series),
    title="Number of Unique Values per Facet (EIA)",
    xlabel="Facet ID",
    ylabel="Unique Value Count",
    rotation=30,
    wrap_width=30,
    figsize=(12, 6),
)

# %% [markdown]
# <a name='temporal-resolution-coverage-by-dataset'></a>
# #### Temporal Resolution Coverage by Dataset
#
# This heatmap shows the distribution of time series across combinations of `dataset_id` and `frequency_id`.
#
# - Most datasets report data at `monthly` frequency.
#
# - A few datasets, `like daily_region_data` or `daily_fuel_type_data`, are specifically tailored for daily reporting.
#
# - Some datasets support multiple frequencies, indicating they may be used across short-term and long-term analyses.
#
# - Datasets such as capability, summary, and net_metering have limited frequency options, typically annual or yearly, suggesting a more strategic rather than operational nature.

# %%
# Generate dataset and frequency crosstab.
dataset_frequency_crosstab = pd.crosstab(df_metadata["dataset_id"], df_metadata["frequency_id"])
# Plot heatmap of dataset against frequency.
caueduti.plot_heatmap(
    crosstab,
    title="Heatmap of Dataset vs Frequency",
    xlabel="Frequency ID",
    ylabel="Dataset ID",
    fmt="d",
    cmap="Blues",
    figsize=(12, 6)
)
