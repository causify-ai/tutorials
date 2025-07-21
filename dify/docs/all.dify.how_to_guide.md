<!-- toc -->

- [Dify Chatflow with External Knowledge API](#dify-chatflow-with-external-knowledge-api)
  * [Prerequisites](#prerequisites)
  * [Step 1: Create Dify Application](#step-1-create-dify-application)
  * [Step 2: Configure Basic Chatflow](#step-2-configure-basic-chatflow)
    + [Start Node Configuration](#start-node-configuration)
    + [Add LLM Node](#add-llm-node)
    + [Connect and Test](#connect-and-test)
  * [Step 3: Configure External Knowledge](#step-3-configure-external-knowledge)
  * [Step 4: Add Knowledge to Chatflow](#step-4-add-knowledge-to-chatflow)
    + [Add Knowledge Retrieval Node](#add-knowledge-retrieval-node)
    + [Update LLM System Prompt](#update-llm-system-prompt)
    + [Update User](#update-user)
    + [Final Flow](#final-flow)
  * [Step 5: Test and Optimize](#step-5-test-and-optimize)
    + [Test Knowledge Integration](#test-knowledge-integration)
    + [Optimization Options](#optimization-options)
  * [Troubleshooting](#troubleshooting)
    + [API Connection Issues](#api-connection-issues)


<!-- tocstop -->

# Dify Chatflow with External Knowledge API

Step-by-step guide to create a Dify chatflow that uses your Weaviate knowledge
base for intelligent document retrieval.

## Prerequisites

- Dify instance running (local or cloud)
- Weaviate running on `localhost:8080`
  - Follow the official setup guide: [Weaviate Installation Documentation](https://weaviate.io/developers/weaviate/installation)
  - Quick start with Docker: [Weaviate Docker Guide](https://weaviate.io/developers/weaviate/installation/docker-compose)
  - Verify it's running: `curl http://localhost:8080/v1/meta`

- Ollama running on `localhost:11434` with `nomic-embed-text` model
  - Download and install: [Ollama Official Website](https://ollama.ai/)
  - Installation guide: [Ollama GitHub Documentation](https://github.com/ollama/ollama#quickstart)
  - Ensure you have the embedding model: `ollama pull nomic-embed-text`
  - Verify it's running: `curl http://localhost:11434/api/tags`

- Documents processed into Weaviate collection - see [Weaviate Integration Guide](all.weaviate_integration.how_to_guide.md)
- API service running on `http://localhost:2001`

## Step 1: Create Dify Application

1. Navigate to your Dify instance (`http://localhost/` for local)
2. Click "Create Application" → "Chatflow"
3. Name: `Knowledge Assistant`
4. Click "Create"

## Step 2: Configure Basic Chatflow

### Start Node Configuration

- User Input Variable: `user_question`
- Input Type: Text
- Required: Yes

### Add LLM Node

1. Add LLM node between Start and Answer
2. Configure:
   - Model: Your preferred model (GPT-4, Claude, etc.)
   - System Prompt: `You are a helpful AI assistant.`
   - User Message: `{{#sys.query#}}`

### Connect and Test

1. Connect: Start → LLM → Answer
2. Set Answer node: `{{#llm.text#}}`
3. Publish and test basic functionality

## Step 3: Configure External Knowledge

1. Go to "Knowledge" → "Connect External Knowledge API"
2. Configure:
   - Name: `Documents`
   - API Endpoint: `http://localhost:2001/retrieval`
     - Sometimes the api endpoint is pointed to bridge gateway for the docker
       service
     - For cloud setup deploy weaviate on weaviate cloud or make a S3 instance
       with the retrieval api
   - API Key: Your API key from `.env` file
   - Knowledge ID: `Documents`
   - Top K: `5`
   - Score Threshold: `0.5`
3. Test connection to verify setup

## Step 4: Add Knowledge to Chatflow

### Add Knowledge Retrieval Node

1. Insert "Knowledge Retrieval" node between Start and LLM
2. Configure:
   - Knowledge Source: Select `Documents`
   - Query: `{{#sys.query#}}`

### Update LLM System Prompt

```text
You are a knowledgeable AI assistant with access to a document knowledge base.

Instructions:
1. Use the provided context from retrieved documents to answer questions
2. If the context contains relevant information, use it in your response
3. If the context doesn't contain relevant information, say so and provide a general answer
4. Always be helpful and cite when you're using information from the knowledge base
5. Keep responses clear and concise

Context from knowledge base:
main prompt: {{#sys.query#}}
context: {{#context#}}
```

### Update User

```text

User Question: {{#sys.query#}}

Please provide a helpful answer using the context provided above when relevant.
```

### Final Flow

Start → Knowledge Retrieval → LLM → Answer

## Step 5: Test and Optimize

### Test Knowledge Integration

1. Publish your chatflow
2. Test with document-specific questions:
   - "How do I configure the environment?"
   - "What are the setup prerequisites?"
3. Verify responses include document information

## Troubleshooting

### API Connection Issues

Check API is running:
`curl http://localhost:2001/health` Verify API
key matches between Dify and `.env` file Test direct API call:

```bash
> curl -X POST http://localhost:2001/retrieval \
  -H "Authorization: " \
  -H "Content-Type: application/json" \
  -d '{"knowledge_id": "Documents", "query": "test", "retrieval_setting": {"top_k": 3, "score_threshold": 0.5}}'
```

