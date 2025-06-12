# AWS X-Ray API and Custom Wrapper Layer

## 📡 Native API: `boto3.client("xray")`

This is Amazon's official SDK for interacting with AWS X-Ray.
It includes methods like:
- `get_trace_summaries()`
- `batch_get_traces()`

Our Wrapper Layer is in `utils/xray_data_fetcher.py`

To simplify usage, we created:

### `fetch_today_trace_data()`

- Fetches and consolidates traces for the current UTC day
- Parses JSON documents, extracts subsegments with annotations
- Converts them into a flat DataFrame for downstream ML/analysis

**Key Outputs:**
- `trace_id`
- `timestamp`
- `flag`
- `processing_time_ms`
- `shard_id`
- `hour_str` (rounded timestamp to nearest hour)

### `extract_annotated_subsegments()`

- Recursively pulls all annotated subsegments from a segment
- Allows analysis of deeply nested traces

---

## 📌 Design Decisions

- Flattening traces into a Pandas-friendly format
- Extracts annotations like `processing_time_ms`, `flag`, and `error`
- Modular approach allows the fetcher function to be reused in dashboards, forecasting, or notebooks
---
