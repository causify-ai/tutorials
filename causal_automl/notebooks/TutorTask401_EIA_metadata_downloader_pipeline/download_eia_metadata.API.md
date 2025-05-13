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

- Discover available dataset routes and metrics.
- Flatten nested metadata into a tabular format.
- Preview available frequency, units, and facets.
- Construct valid (but unvalidated) query URLs for EIA time series access.

## Problem it solves

- The EIA API exposes thousands of datasets in a nested category tree.
- Each dataset has a mix of:
  - Metric IDs (e.g., revenue, sales)
  - Frequencies (e.g., annual, monthly)
  - Required facet combinations (e.g., `stateid`, `sectorid`)
- Users often need to understand the full dimensionality of what's available
  before downloading actual data.

This API layer lets you:

- Extract all leaf datasets under any category.
- Generate flat metadata describing valid time series combinations.
- Preview allowed values for required facets.
- Construct query URLs to test manually — but not guarantee availability.

## Design goals

- Separate metadata logic from time series fetching.
- Make all outputs easy to inspect as `pd.DataFrame`s.
- Allow notebook users to generate parameterized URLs, even if some URLs may not
  yield data.

## Challenges

One key challenge in working with the EIA v2 API is its **tree-structured
hierarchy**. Datasets are nested across multiple category levels (e.g.,
`electricity/sales/retail`) and cannot be retrieved in bulk through a single
endpoint.

To build a valid time series request, users must:

* Traverse to each **leaf dataset** in the API.
* Identify all combinations of **frequency** and **metric** that define a
  time series.
* Parse and separate **facet types** (e.g., `stateid`, `sectorid`) and their
  allowed values.
* Provide **exactly one value per facet** to construct a valid query.

The EIA API does not provide availability flags for facet combinations. This
means:

* A syntactically valid URL might return no data.
* Users must flatten all metadata and facet dimensions in advance.
* Availability checks must be done after URL construction (not within this
  layer).

This module resolves the traversal and flattening steps but deliberately leaves
data availability validation to downstream layers or notebooks that choose to
fetch actual responses.

## Limitations

* Does not download or validate numeric time series.
* Assumes one facet value per type (e.g., `stateid=CA`, not all states).
* Does not handle errors in downstream API calls.

## Conclusion

This module simplifies metadata exploration across the EIA dataset catalog. It
does not replace a full ingestion pipeline but provides a reliable way to
understand the structure and parameters of available time series.
