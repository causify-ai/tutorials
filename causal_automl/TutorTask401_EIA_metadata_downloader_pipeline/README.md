# EIA Metadata Tutorial

<!-- toc -->

- [EIA Tutorial Overview](#eia-tutorial-overview)
- [Files](#files)

<!-- tocstop -->

## EIA Tutorial Overview

This tutorial demonstrates how to extract and analyze electricity metadata from
the U.S. EIA v2 API. It provides a modular metadata-only pipeline for exploring
dataset coverage, metrics, frequencies, and facet structures without pulling
actual time series values.

## Files

- `eia_utils.py`: Wrapper for the EIA v2 API
- `download_eia_metadata.py`: Script to extract metadata and upload it to S3
- `download_eia_metadata.API.ipynb`: Notebook showing how to use the API wrapper
- `download_eia_metadata.API.md`: Markdown explaining the API design and wrapper
- `download_eia_metadata.example.ipynb`: Notebook exploring the output metadata
- `download_eia_metadata.example.md`: Markdown explaining the analysis and
  insights
- `README.md`: This file
