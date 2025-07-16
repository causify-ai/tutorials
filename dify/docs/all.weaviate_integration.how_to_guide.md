<!-- toc -->

- [How to Integrate Weaviate with Dify External Knowledge API](#how-to-integrate-weaviate-with-dify-external-knowledge-api)
  * [What You'll Build](#what-youll-build)
  * [Prerequisites](#prerequisites)
  * [Step 1: Environment Setup](#step-1-environment-setup)
  * [Step 2: Start Required Services](#step-2-start-required-services)
  * [Step 3: Process Your Documents](#step-3-process-your-documents)
  * [Step 4: Start the Retrieval API](#step-4-start-the-retrieval-api)
  * [Step 5: Configure Dify External Knowledge](#step-5-configure-dify-external-knowledge)
  * [Step 6: Test the Integration](#step-6-test-the-integration)
  * [Troubleshooting Quick Fixes](#troubleshooting-quick-fixes)

<!-- tocstop -->

# How to Integrate Weaviate with Dify External Knowledge API

This tutorial walks you through setting up Weaviate as an external knowledge
source for Dify applications.

## What You'll Build

You'll create a system where:

1. Documents are automatically processed and stored in Weaviate
2. Dify can query this knowledge base through a REST API
3. Search results are returned with relevant context and metadata

## Prerequisites

Before starting, ensure you have the following services running:

- Weaviate running on `localhost:8080`
  - Follow the official setup guide: [Weaviate Installation Documentation](https://weaviate.io/developers/weaviate/installation)
  - Quick start with Docker: [Weaviate Docker Guide](https://weaviate.io/developers/weaviate/installation/docker-compose)
  - Verify it's running: `curl http://localhost:8080/v1/meta`

- Ollama running on `localhost:11434` with `nomic-embed-text` model
  - Download and install: [Ollama Official Website](https://ollama.ai/)
  - Installation guide: [Ollama GitHub Documentation](https://github.com/ollama/ollama#quickstart)
  - Ensure you have the embedding model: `ollama pull nomic-embed-text`
  - Verify it's running: `curl http://localhost:11434/api/tags`

- Python 3.8+ with required packages installed
  ```bash
  pip install weaviate-client langchain requests fastapi uvicorn
  ```

## Step 1: Environment Setup

Create a `.env` file with the required configuration:

```bash
# .env file
PWD=/path/to/your/project
OLLAMA_EMBED_URL=http://localhost:11434/api/embed
OLLAMA_MODEL=nomic-embed-text
API_KEY=your-secure-api-key-here
APP_HOST=0.0.0.0
APP_PORT=2001
```

## Step 2: Start Required Services

Start Weaviate:

If you followed the [Weaviate Docker setup](https://weaviate.io/developers/weaviate/installation/docker-compose), start with:

```bash
# Navigate to your weaviate directory
cd /path/to/weaviate
docker compose up -d

# Verify it's running
curl http://localhost:8080/v1/meta
```

Start Ollama:

If you installed from [ollama.ai](https://ollama.ai/), start with:

```bash
# Start Ollama service
ollama serve

# Pull the embedding model (if not already done)
ollama pull nomic-embed-text

# Verify it's running
curl http://localhost:11434/api/tags
```

## Step 3: Process Your Documents

Use the document processing module to upload your markdown files:

```python
import logging
import dify.weaviate_docs as dweadocs

# Configure logging
dweadocs.configure_logging(level=logging.INFO)

# Process documents
result = dweadocs.upload_markdown_docs_to_weaviate(
    docs_dir='./your-docs-directory',
    collection_name='Documents'
)

print(f"Successfully processed {result['successful_files']} files")
```

## Step 4: Start the Retrieval API

Run the FastAPI service that Dify will connect to:

```bash
> python3  dify.weaviate_retrieval
```

The API will start on `http://localhost:2001` with these endpoints:

- `POST /retrieval` - Main search endpoint for Dify
- `GET /health` - Health check

## Step 5: Configure Dify External Knowledge

In your Dify application:

1. Go to Knowledge → External Knowledge
2. Add a new external knowledge source:
   - API Endpoint: `http://localhost:2001/retrieval`
   - API Key: The value from your `API_KEY` environment variable
   - Knowledge ID: `Documents` (the collection name you used)

## Step 6: Test the Integration

Test that everything works:
Healthcheck:
```bash
> curl http://localhost:2001/health
```

Test the API directly
```bash
> curl -X POST http://localhost:2001/retrieval \
  -H "Authorization: " \
  -H "Content-Type: application/json" \
  -d '{
    "knowledge_id": "Documents",
    "query": "your search query",
    "retrieval_setting": {
      "top_k": 5,
      "score_threshold": 0.5
    }
  }'
```

## Troubleshooting Quick Fixes

Connection Issues:

- Verify Weaviate:
  ```bash
   > curl http://localhost:8080/v1/meta 
   ```
- Verify Ollama:
  ```bash
  > curl http://localhost:11434/api/tags
  ```
  If this fails, see [Ollama GitHub Issues](https://github.com/ollama/ollama/issues) or [Ollama Documentation](https://github.com/ollama/ollama/blob/main/docs/troubleshooting.md).

For detailed troubleshooting:
- [Weaviate Documentation](https://weaviate.io/developers/weaviate)
- [Ollama Documentation](https://github.com/ollama/ollama)
- [Weaviate Python Client](https://weaviate.io/developers/weaviate/client-libraries/python)
