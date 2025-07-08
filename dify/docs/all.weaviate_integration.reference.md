<!-- toc -->

- [Weaviate Integration Reference](#weaviate-integration-reference)
  * [Module API Reference](#module-api-reference)
    + [dify.weaviate_docs](#difyweaviate_docs)
    + [dify.weaviate_retrieval](#difyweaviate_retrieval)
  * [API Specifications](#api-specifications)
    + [Request Format (POST /retrieval)](#request-format-post-retrieval)
    + [Response Format](#response-format)
    + [Error Codes](#error-codes)
  * [Environment Variables](#environment-variables)
    + [Required](#required)
    + [Optional](#optional)
  * [Weaviate Collection Schema](#weaviate-collection-schema)
  * [Common Issues & Solutions](#common-issues--solutions)
    + [Connection Problems](#connection-problems)
    + [Poor Search Results](#poor-search-results)
    + [Performance Issues](#performance-issues)
  * [Version Compatibility](#version-compatibility)

<!-- tocstop -->

# Weaviate Integration Reference

Technical specifications for the Weaviate-Dify External Knowledge API
integration.

## Module API Reference

### dify.weaviate_docs

`upload_markdown_docs_to_weaviate(docs_dir, collection_name, **kwargs)`

- Processes markdown files and uploads to Weaviate
- Returns: `{"successful_files": int, "failed_files": int}`

Key Parameters:

- `chunk_size`: 500 (characters)
- `chunk_overlap`: 50 (characters)
- `batch_size`: 100 (objects)
- `allowed_extensions`: `[".md"]`

### dify.weaviate_retrieval

FastAPI Endpoints:

- `POST /retrieval` - Search documents (Dify External Knowledge API compatible)
- `GET /health` - Service health check

Authentication: Bearer token via `Authorization` header

## API Specifications

### Request Format (POST /retrieval)

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
  `curl [http://localhost:11434/api/tag](http://localhost:11434/api/tag)s`

### Poor Search Results

- Lower `score_threshold` (try 0.3 instead of 0.5)
- Verify same embedding model for index and search
- Check collection exists:
  `curl [http://localhost:8080/v1/object](http://localhost:8080/v1/object)s`

### Performance Issues

- Reduce `chunk_size` to 300 for faster processing
- Increase `batch_size` to 200 for bulk operations
- Monitor memory usage during large document processing

## Version Compatibility

| Component | Minimum | Tested  |
| --------- | ------- | ------- |
| Weaviate  | 1.20.0  | 1.25.0  |
| Python    | 3.8     | 3.11    |
| FastAPI   | 0.100.0 | 0.104.0 |
