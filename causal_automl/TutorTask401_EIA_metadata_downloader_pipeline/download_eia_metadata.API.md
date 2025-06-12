# EIA Metadata API Layer

<!-- toc -->

- [Overview](#overview)
  * [Understanding facets](#understanding-facets)
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

- **Discover dataset routes.** Retrieve the full category tree exposed by the
  EIA API and identify dataset leaf paths (e.g., `electricity/retail-sales`)
  that define related time series

- **Identify available metrics.** Extract the measurable variables (referred to
  as metrics in the EIA API) for each dataset, such as total revenue, number of
  customers, or electricity consumption

- **Preview supported frequencies, units, and facets.** Understand the temporal
  resolution (e.g., monthly, annual), the measurement units (e.g., kilowatthours
  or dollars), and the filtering dimensions (facets) required by each dataset
  (e.g., `stateid=CA`, `sectorid=RES`)

- **Flatten nested metadata into a tabular format.** Generate a `pd.DataFrame`
  where each row corresponds to a unique combination of dataset route,
  frequency, and metric, along with the list of required facet types (e.g.,
  `stateid`, `sectorid`)

- **Construct time series query URLs.** Build syntactically correct EIA API URLs
  to retrieve specific time series, without checking whether those URLs actually
  return data

### Understanding facets

Each dataset defines one or more facets, which are categorical filters used to
construct time series API queries. A facet includes:

- A facet type, such as `stateid` or `sectorid`
- A list of allowed values, like `CA`, `TX`, or `OTH`
- Aliases (user-friendly labels for display)

To retrieve data for a given dataset, you must supply exactly one value for each
required facet. The required facet types vary across datasets.

Note: The EIA API does not indicate which combinations of facet values will
return data. While you can construct syntactically correct URLs using this
metadata, actual data availability must be tested independently.

## Problem it solves

The EIA API exposes thousands of datasets organized in a nested category tree.

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
- Make all outputs easy to inspect as `pd.DataFrame`s
- Allow notebook users to generate parameterized URLs based on metadata, even if
  some URLs do not yield data

## Challenges

One key challenge in working with the EIA v2 API is its tree-structured
hierarchy. Datasets are nested across multiple category levels (e.g.,
`electricity/retail-sales`) and cannot be retrieved in bulk through a single
endpoint.

To construct a time series query, users must:

- Traverse to each leaf dataset in the API
- Identify all combinations of frequency and metric values available under that
  dataset
- Parse the list of required facets and retrieve their allowed values from the
  metadata
- Provide one value per required facet to construct a syntactically query URL
  (see [Understanding facets](#understanding-facets) for details)

The EIA API does not provide availability flags for facet combinations. This
means:

- A syntactically correct URL might return no data
- Users must flatten all metadata and facet dimensions in advance
- Availability checks must be done after URL construction (not within this
  module)

This module resolves the traversal and flattening steps but leaves data
availability validation to downstream systems or notebooks.

## Limitations

- Does not download or validate numeric time series
- Requires exactly one facet value per required type (e.g., `stateid=CA`, not
  all states). This requirement applies only when retrieving numeric time series
  data, not during metadata extraction.
- Does not handle errors in downstream API calls

## Conclusion

This module simplifies metadata exploration across the EIA dataset catalog. It
does not replace a full ingestion pipeline but provides a lightweight interface
to understand the structure and constraints of time series metadata available
through the EIA API.
