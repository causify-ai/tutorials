# EIA Metadata API Layer

<!-- toc -->

- [Overview](#overview)
- [Problem it solves](#problem-it-solves)
- [Design goals](#design-goals)
- [Challenges](#challenges)
- [Limitations](#limitations)
- [Conclusion](#conclusion)

<!-- tocstop -->

## Overview

This module provides a minimal, class-based API to extract and structure
metadata from the [EIA v2 API](https://www.eia.gov/opendata/). It is designed to
support exploration and validation of time series metadata without fetching
actual numeric data.

This allows users to:

- **Discover dataset routes**
  Retrieve the full category tree exposed by the EIA API and identify dataset
  leaf paths (for example, `electricity/sales/retail`) that define related time
  series

- **Identify available metrics**
  Extract the measurable variables (referred to as metrics in the EIA API) for
  each dataset, such as total revenue, number of customers, or electricity
  consumption

- **Preview supported frequencies, units, and facets**
  Understand the temporal resolution (e.g., monthly, annual), the measurement
  units (e.g., kilowatthours or dollars), and the filtering dimensions (facets)
  required by each dataset (for example, `stateid=CA`, `sectorid=RES`)

- **Flatten nested metadata into a tabular format**
  Generate a `pd.DataFrame` where each row represents a unique time series
  defined by a valid combination of metric, frequency, and facet values

- **Construct time series query URLs**
  Build syntactically valid EIA API URLs to retrieve specific time series,
  without checking whether those URLs return data

## Problem it solves

The EIA API exposes thousands of datasets organized in a nested category tree

Each dataset is defined by:

- A set of metrics such as revenue or sales
- One or more supported frequencies such as annual or monthly
- A set of required facets such as `stateid` or `sectorid`, each of which is
  required by the EIA API and must be included in the query URL

Users often need to explore the structure of available time series before
downloading data. This module helps by:

- Extracting all leaf-level datasets under a given category
- Listing all available metrics, frequencies, and facet values extracted from
  each dataset's metadata
- Constructing query URLs based on metadata structure, which may not return data
  and must be validated downstream

## Design goals

- Separate metadata logic from time series fetching
- Make all outputs easy to inspect as pandas dataframes
- Allow notebook users to generate parameterized URLs, even if some URLs may not
  yield data

## Challenges

One key challenge in working with the EIA v2 API is its **tree-structured
hierarchy**. Datasets are nested across multiple category levels (e.g.,
`electricity/sales/retail`) and cannot be retrieved in bulk through a single
endpoint.

To build a valid time series request, users must:

- Traverse to each **leaf dataset** in the API
- Identify all combinations of **frequency** and **metric** that define a time
  series
- Parse and separate **facet types** (e.g., `stateid`, `sectorid`) and their
  allowed values
- Provide **exactly one value per facet** to construct a valid query

The EIA API does not provide availability flags for facet combinations. This
means:

- A syntactically valid URL might return no data
- Users must flatten all metadata and facet dimensions in advance
- Availability checks must be done after URL construction (not within this
  layer)

This module resolves the traversal and flattening steps but deliberately leaves
data availability validation to downstream layers or notebooks that choose to
fetch actual responses.

## Limitations

- Does not download or validate numeric time series
- Assumes one facet value per type (e.g., `stateid=CA`, not all states)
- Does not handle errors in downstream API calls

## Conclusion

This module simplifies metadata exploration across the EIA dataset catalog. It
does not replace a full ingestion pipeline but provides a reliable way to
understand the structure and parameters of available time series.
