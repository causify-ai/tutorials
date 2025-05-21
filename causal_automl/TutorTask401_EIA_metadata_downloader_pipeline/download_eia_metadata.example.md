# EIA Metadata Example Notebook

<!-- toc -->

- [Overview](#overview)
- [Scenario](#scenario)
- [Applications](#applications)
- [Design highlights](#design-highlights)
- [Wrap-up and insights](#wrap-up-and-insights)

<!-- tocstop -->

## Overview

This notebook demonstrates a real-world application of the
`EiaMetadataDownloader` class to extract and analyze metadata from the EIA v2
API. It focuses on using the flattened metadata to understand dataset coverage,
preview facet dimensions, and support query planning—all without making live API
calls to fetch time series.

The goal is to help users perform structured, reproducible metadata analysis as
a precursor to building ingestion logic or validating dataset structure.

## Scenario

The example walks through metadata visualization. Using metadata extracted from
the `electricity` category, the notebook generates distribution plots of:

- Frequency types (e.g., monthly, annual)
- Unit types (e.g., million dollars, MWh)
- Number of time series per dataset

These visualizations reveal the breadth and depth of available datasets and help
identify high-coverage routes for further inspection.

## Applications

This metadata-first approach supports multiple use cases:

- Exploring which metrics, frequencies, and facet types are exposed for each
  dataset
- Building dashboards that track schema coverage or the availability of new
  datasets
- Generating documentation for ingestible datasets based on real API structure
- Supporting ingestion pipelines that use metadata to construct API queries
  before fetching data

## Design highlights

- Uses the `EiaMetadataDownloader` class to abstract away tree traversal
- All plots are generated using helper functions from `eia_utils`, improving
  reusability
- URL construction and actual data fetching are deliberately omitted to preserve
  clarity and purpose

## Wrap-up and insights

This example demonstrates how to extract and visualize structural metadata from
the EIA v2 API, enabling users to:

- Understand the dimensionality of available datasets
- Preview the frequency and unit types across all metrics
- Prioritize dataset routes based on their time series count

This helps avoid unnecessary API calls by validating the structure before
building ingestion logic. It also supports a clean separation between discovery
(metadata) and execution (data retrieval).
