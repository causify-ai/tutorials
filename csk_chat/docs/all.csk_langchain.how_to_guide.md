<!-- toc -->

- [CSK LangChain Chat CLI](#csk-langchain-chat-cli)
  * [Summary](#summary)
  * [Prerequisites](#prerequisites)
  * [Installation and Setup](#installation-and-setup)
  * [Configuration](#configuration)
  * [Usage Modes](#usage-modes)
    + [Interactive Mode](#interactive-mode)
    + [Single Query Mode](#single-query-mode)
    + [Connection Testing](#connection-testing)
  * [Command Line Options](#command-line-options)
  * [Understanding the Output](#understanding-the-output)
  * [Troubleshooting](#troubleshooting)
  * [Advanced Usage](#advanced-usage)
  * [Resources](#resources)
  * [Last review](#last-review)

<!-- tocstop -->

# CSK LangChain Chat CLI

## Summary

- This document explains how to use the CSK LangChain Chat CLI system
- The system integrates Weaviate document retrieval with Anthropic Claude for intelligent document-based Q&A
- Supports both interactive chat sessions and single query execution
- Automatically includes GitHub links to source documentation in responses
- Provides metadata about retrieved documents and relevance scores

## Prerequisites

Before using the CSK LangChain Chat CLI, ensure you have:

- Python 3.8 or higher installed
- Access to Anthropic's Claude API
- API keys configured (see Configuration section below)

## Installation and Setup

Run the automated setup process:

```bash
python3 csk_chat/csk_chat_setup.py --install-all
```

This will:
- Install all required Python dependencies
- Set up Weaviate and Ollama services
- Process and upload documentation
- Configure the retrieval API

For individual setup steps, use:
```bash
# Install dependencies only
python3 csk_chat/csk_chat_setup.py --install-deps

# Start services only  
python3 csk_chat/csk_chat_setup.py --start-services

# Process documents only
python3 csk_chat/csk_chat_setup.py --process-docs
```

## Configuration

Set up your environment variables by creating a `.env` file or setting system environment variables:

```bash
# .env file
ANTHROPIC_API_KEY=your_anthropic_api_key_here
API_KEY=your_weaviate_api_key_here
```

The system searches for `.env` files in:
- Current directory (`./.env`)
- Parent directory (`../.env`)
- System environment variables (if no `.env` file found)

Verify your setup:
```bash
python3 csk_chat/csk_langchain.py --test
```

Expected output:
```
Testing connections...
[OK] Weaviate API connection
[OK] Anthropic API connection
```

## Usage Modes

### Interactive Mode

Start an interactive chat session:

```bash
python3 csk_langchain.py --interactive
```

What you'll see:
```
CSK LangChain Chat CLI
========================================
Type 'quit', 'exit', or 'q' to end the session
Type 'help' for available commands
========================================

Your question: 
```

Available commands in interactive mode:
- Type any question about your documentation
- `help` - Show available commands
- `quit`, `exit`, or `q` - Exit the session

Example interaction:
```
Your question: How do I write good documentation?

============================================================
RESPONSE:
============================================================
According to [all.writing_docs.how_to_guide.md](https://github.com/causify-ai/helpers/tree/74f3d1ad9b5b453b2babbe9c870adf381b35ce45/docs/documentation_meta/all.writing_docs.how_to_guide.md), here are key principles for writing good documentation:

- Use active voice most of the time
- Format for easy reading with headings and bullet points
- Keep it visual with diagrams and tables
- Be efficient and avoid fluff

References:
- [all.writing_docs.how_to_guide.md](https://github.com/causify-ai/helpers/tree/74f3d1ad9b5b453b2babbe9c870adf381b35ce45/docs/documentation_meta/all.writing_docs.how_to_guide.md)

METADATA:
   Documents used: 1
   Source files: all.writing_docs.how_to_guide.md
============================================================
```

### Single Query Mode

Execute a single query and exit:

```bash
python3 csk_langchain.py --query "What are the coding style guidelines?"
```

When to use:
- Quick one-off questions
- Scripting or automation
- Testing specific queries

Hide metadata (for cleaner output):
```bash
python3 csk_langchain.py --query "What is DRY principle?" --no-metadata
```

### Connection Testing

Test your system setup:

```bash
python3 csk_langchain.py --test
```

This verifies Weaviate API and Anthropic API connectivity.

## Command Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `-i, --interactive` | Start interactive chat mode | `--interactive` |
| `-q, --query` | Single query mode | `--query "How to write tests?"` |
| `--test` | Test service connections | `--test` |
| `--no-metadata` | Hide metadata in output | `--no-metadata` |
| `-v, --verbose` | Enable debug logging | `--verbose` |

Combining options:
```bash
# Verbose single query without metadata
python3 csk_langchain.py --query "What is CI/CD?" --no-metadata --verbose
```

## Understanding the Output

The system provides structured responses with three main sections:

### 1. Response Content
The main answer to your question, with inline citations to source documents.

### 2. GitHub Links
Clickable links to the exact source files in the repository:
```
According to [filename.md](https://github.com/causify-ai/helpers/tree/74f3d1ad9b5b453b2babbe9c870adf381b35ce45/docs/path/filename.md)...
```

### 3. Metadata Section
```
METADATA:
   Documents used: 3
   Source files: file1.md, file2.md, file3.md
```

Understanding relevance:
- The system retrieves up to 5 most relevant documents
- Relevance scores help determine document quality
- Higher scores (closer to 1.0) indicate better matches

## Troubleshooting

### Common Issues

Issue: `ANTHROPIC_API_KEY environment variable is required`
- Solution: Set your API key in `.env` file or environment variables

Issue: `[ERROR] Weaviate API connection failed`  
- Solution: Ensure Weaviate is running via the setup script
- Check: Run `python3 csk_chat/csk_chat_setup.py --test`

Issue: `No relevant documents found`
- Solution: Verify documents were processed successfully
- Re-run: `python3 csk_chat/csk_chat_setup.py --process-docs`

Issue: Import errors for packages
- Solution: Re-run setup: `python3 csk_chat/csk_chat_setup.py --install-deps`

### Debug Mode

Enable verbose logging:
```bash
python3 csk_langchain.py --interactive --verbose
```

### Reset System

If issues persist:
```bash
# Test system status
python3 csk_langchain.py --test

# Re-run full setup
python3 csk_chat/csk_chat_setup.py --install-all
```

## Advanced Usage

### Programmatic Usage

Import and use the system in your own Python code:

```python
import csk_chat.csk_langchain as ccskchat

# Initialize configuration
config = ccskchat.CSKChatConfig()

# Create chat system
chat_system = ccskchat.CSKChatSystem(config)

# Process queries
result = chat_system.process_query("How do I write documentation?")

print("Response:", result["response"])
print("Sources:", result["source_files"])
print("Document count:", result["document_count"])
```

### Custom Configuration

Modify system behavior through the configuration class:

```python
config = ccskchat.CSKChatConfig()

# Adjust retrieval parameters
config.top_k = 10  # Retrieve more documents
config.score_threshold = 0.1  # Lower relevance threshold
config.temperature = 0.5  # More focused responses

# Use custom Weaviate endpoint
config.weaviate_url = "http://your-weaviate-host:8080/retrieval"
```

### Batch Processing

Process multiple queries programmatically:

```python
queries = [
    "What are the coding standards?",
    "How do I write tests?",
    "What is the deployment process?"
]

chat_system = ccskchat.CSKChatSystem(ccskchat.CSKChatConfig())

for query in queries:
    result = chat_system.process_query(query)
    print(f"Q: {query}")
    print(f"A: {result['response']}\n")
```

## Resources

- [Weaviate Integration Guide](/all.weaviate_integration.how_to_guide.md)
- [Weaviate Integration Reference](/all.weaviate_integration.reference.md)