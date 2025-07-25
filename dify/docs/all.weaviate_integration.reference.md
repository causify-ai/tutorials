<!-- toc -->

- [Weaviate Integration Reference](#weaviate-integration-reference)
  * [Summary](#summary)
  * [Module API Reference](#module-api-reference)
    + [Dify.Weaviate_Docs](#difyweaviate_docs)
    + [Dify.Weaviate_Retrieval](#difyweaviate_retrieval)
  * [API Specifications](#api-specifications)
    + [Request Format (POST /Retrieval)](#request-format-post-retrieval)
    + [Response Format](#response-format)
    + [Error Codes](#error-codes)
  * [Environment Variables](#environment-variables)
    + [Required](#required)
    + [Optional](#optional)
  * [Weaviate Collection Schema](#weaviate-collection-schema)
  * [Common Issues & Solutions](#common-issues--solutions)
    + [Connection Problems](#connection-problems)
    + [Poor Search Results](#poor-search-results)
  * [Resources](#resources)
  * [Last Review](#last-review)

<!-- tocstop -->

# Weaviate Integration Reference

## Summary

- Technical specifications for the Weaviate-Dify External Knowledge API
  integration
- API documentation for modules and endpoints
- Environment variables and configuration options
- Troubleshooting guide for common issues

## Module API Reference

### Dify.Weaviate_Docs

`upload_markdown_docs_to_weaviate(docs_dir, collection_name, **kwargs)`

- Processes markdown files and uploads to Weaviate
- Returns: `{"successful_files": int, "failed_files": int}`

Key Parameters:

- `chunk_size`: 500 (characters)
- `chunk_overlap`: 50 (characters)
- `batch_size`: 100 (objects)
- `allowed_extensions`: `[".md"]`

### Dify.Weaviate_Retrieval

FastAPI Endpoints:

- `POST /retrieval` - Search documents (Dify External Knowledge API compatible)
- `GET /health` - Service health check

Authentication: Bearer token via `Authorization` header

## API Specifications

### Request Format (POST /Retrieval)

```json
{
  "knowledge_id": "string",
  "query": "string",
  "retrieval_setting": {
    "top_k": 5,
    "score_threshold": 0.5
  }
}
```

### Response Format

```json
{
  "records": [
    {
      "metadata": { "filepath": "string" },
      "score": 0.95,
      "title": "string",
      "content": "string"
    }
  ]
}
```

### Error Codes

| Code | Status | Description                  |
| ---- | ------ | ---------------------------- |
| 1001 | 403    | Invalid Authorization header |
| 1002 | 403    | Invalid API key              |
| 2001 | 400    | Collection not found         |
| 5000 | 500    | Embedding generation failed  |
| 5001 | 500    | Weaviate query failed        |

## Environment Variables

### Required

- `PWD` - Project root directory
- `API_KEY` - Authentication key for API access

### Optional

- `OLLAMA_EMBED_URL` - Default: `http://localhost:11434/api/embed`
- `OLLAMA_MODEL` - Default: `nomic-embed-text`
- `APP_HOST` - Default: `0.0.0.0`
- `APP_PORT` - Default: `2001`

## Weaviate Collection Schema

```json
{
  "class": "Documents",
  "vectorizer": "none",
  "properties": [
    { "name": "text", "dataType": ["text"] },
    { "name": "filename", "dataType": ["text"] },
    { "name": "filepath", "dataType": ["text"] }
  ]
}
```

## Common Issues & Solutions

### Connection Problems

- Weaviate down: `docker ps | grep weaviate`
- Ollama unavailable:
  ```bash
  > curl http://localhost:11434/api/tags
  ```

### Poor Search Results

- Lower `score_threshold` (try 0.3 instead of 0.5)
- Verify same embedding model for index and search
- Check collection exists:
  ```bash
  > curl http://localhost:8080/v1/objects
  ```

## Resources

- [Weaviate API Documentation](https://weaviate.io/developers/weaviate/api)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Dify External Knowledge API Specification](https://docs.dify.ai/en/guides/knowledge-base/external-knowledge-api)

