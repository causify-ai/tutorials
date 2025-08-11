<!-- toc -->

- [Dify Chatflow with External Knowledge API](#dify-chatflow-with-external-knowledge-api)
  * [Summary](#summary)
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
  * [Resources](#resources)
  * [Last Review](#last-review)

<!-- tocstop -->

# Dify Chatflow with External Knowledge API

## Summary

- This document explains how to import a pre-built Dify chatflow using the provided DSL (YAML) file
- You only need to import the DSL and configure the External Knowledge and Knowledge Retrieval nodes
- No manual chatflow construction is required

## Prerequisites

- Dify instance running (local or cloud)
- Complete setup from
  [Weaviate Integration Guide](/all.weaviate_integration.how_to_guide.md) using
  the automated `csk_chat_setup.py` script
- All services running and verified:
  - Weaviate on `localhost:8080`
  - Ollama on `localhost:11434`
  - Retrieval API on `localhost:2001`


## Prerequisites

- Dify instance running (local or cloud)
- Complete setup from [Weaviate Integration Guide](/all.weaviate_integration.how_to_guide.md) using the automated `csk_chat_setup.py` script
- All services running and verified:
  - Weaviate on `localhost:8080`
  - Ollama on `localhost:11434`
  - Retrieval API on `localhost:2001`
- The chatflow DSL YAML file (e.g., `csk-chat.yml`) ready for import

## Step 1: Import the DSL (YAML) Chatflow

1. In the Dify web UI, go to "Applications".
2. Click "Import DSL" or "Import YAML" (depending on your Dify version).
3. Select the provided `csk-chat.yml` file and import it.
4. The chatflow will be created automatically with all nodes and connections.

## Step 2: Configure External Knowledge

1. In the imported chatflow, go to the "Knowledge" section.
2. Click "Connect External Knowledge API".
3. Configure:
   - Name: `Documents`
   - API Endpoint: `http://172.17.0.1:2001/retrieval` (Docker bridge IP)
   - API Key: from your `.env` file
   - Knowledge ID: `Documents`
   - Top K: `5`
   - Score Threshold: `0.5`
4. Test the connection to verify setup.

## Step 3: Knowledge Retrieval Node

1. The imported DSL already includes a Knowledge Retrieval node.
2. You can review or adjust its configuration if needed (e.g., dataset, top_k, score_threshold).

## Troubleshooting

- If the chatflow import fails, check the YAML file for syntax errors.
- If Dify cannot reach the API, verify the API endpoint and Docker bridge IP.
- Test the retrieval API directly:
  ```bash
  curl -X POST http://localhost:2001/retrieval \
    -H "Authorization: Bearer " \
    -H "Content-Type: application/json" \
    -d '{"knowledge_id": "Documents", "query": "test", "retrieval_setting": {"top_k": 3, "score_threshold": 0.5}}'
  ```

## Resources

- [Dify Official Documentation](https://docs.dify.ai/)
- [Dify External Knowledge API Documentation](https://docs.dify.ai/en/guides/knowledge-base/external-knowledge-api)
- [Weaviate Integration Guide](/all.weaviate_integration.how_to_guide.md)
- [Docker Bridge Networking](https://docs.docker.com/network/bridge/)

