
<!-- toc -->

- [DocsGPT Tutorial](#docsgpt-tutorial)
  - [What is DocsGPT?](#what-is-docsgpt)
  - [What We Demonstrate in This Notebook](#what-we-demonstrate-in-this-notebook)
  - [Autoreload Setup](#autoreload-setup)
  - [Imports](#imports)
  - [Configuration](#configuration)
  - [Model Initialization](#model-initialization)
  - [Document Ingestion](#document-ingestion)
  - [Querying Documents](#querying-documents)
  - [Manual Prompting](#manual-prompting)
  - [Answer Extraction](#answer-extraction)
  - [Interactive Q\&A Loop](#interactive-qa-loop)
    - [Sample Interaction:](#sample-interaction)
  - [Demonstration with CSV and Web Link](#demonstration-with-csv-and-web-link)
  - [Comparison Table](#comparison-table)
  - [Notebook Naming Convention](#notebook-naming-convention)
  - [References](#references)


<!-- tocstop -->

# DocsGPT Tutorial

This tutorial explains how to use the native API of [DocsGPT](https://github.com/arc53/DocsGPT), a self-hosted, open-source Retrieval-Augmented Generation (RAG) system. DocsGPT allows users to get grounded, accurate answers from their own documents using LLMs like LLaMA via `llama-cpp-python`.

---


## What is DocsGPT?

DocsGPT is a local, offline question-answering system that:

- Ingests and indexes your documents using embeddings  
- Enables semantic search and context retrieval  
- Uses LLMs to answer questions based on your content  
- Returns answers with optional source citations  
- Supports formats like PDF, DOCX, TXT, CSV, Markdown, and HTML  

It can be accessed via a:

- Web UI  
- CLI  
- REST API  
- Python integration (as shown in this notebook)

---

## What We Demonstrate in This Notebook

This notebook (`BitcoinLLMQA.API.ipynb`) demonstrates how to:

- Load a quantized LLaMA model locally using `llama-cpp-python`  
- Ingest documents via DocsGPT's REST API  
- Send queries and retrieve accurate, document-based answers  
- Build prompts manually for low-level control  
- Interact with the system in a loop for dynamic Q&A  
- Demonstrate DocsGPT’s functionality on formats like CSV and PDF via URLs  

---

## Autoreload Setup

This section sets up `%autoreload` to reload imported modules automatically during development, ensuring iterative changes are reflected live.

---

## Imports

The notebook uses standard libraries such as:
- `requests` for sending REST API calls  
- `logging` for system diagnostics  
- `llama_cpp` for loading and using a local LLaMA model  

---

## Configuration

Logging is initialized to track system behavior, model load time, and response time, which is essential for debugging and understanding performance.

---

## Model Initialization

A quantized LLaMA model is loaded using `llama-cpp-python`. Parameters like context window size, thread count, and GPU layers are set for performance.

This step enables running a powerful LLM completely offline for document question-answering.

---

## Document Ingestion

A function is defined to ingest local files (PDFs, DOCXs, CSVs) via the DocsGPT API. This allows the system to chunk and embed documents into its internal vector store for retrieval.

**Why it's important:** This step makes the document searchable and accessible to the LLM during query time.

---

## Querying Documents

This section introduces safe API querying logic. User questions are submitted to the `/query` endpoint, and responses are handled with error resilience for production-readiness.

**Why use it:** To make sure the system handles network errors, malformed inputs, and edge cases gracefully.

---

## Manual Prompting

Manual prompting lets developers experiment with custom prompt formats, directly invoking the LLM. This gives fine-tuned control over how document context and questions are structured.

---

## Answer Extraction

After querying, the response is parsed and printed. This part includes logic for multiple response formats (choices, text, or default fallback).

---

## Interactive Q&A Loop

A live prompt-and-answer loop is implemented to simulate a human-AI interaction, just like a ChatGPT terminal.

### Sample Interaction:

- **User:** What is the stock market price trend  
- **Assistant:** I'm just an AI, I don't have real-time access to current stock market data. However, I can provide general information on stock market trends.

- **User:** You can take reference from this website: https://tradingeconomics.com/united-states/stock-market  
- **Assistant:** Thank you for providing the website link. Based on the data, the stock market price trend in the U.S. has generally been upward with fluctuations.

- **User:** Which commodity has the highest stocks currently?  
- **Assistant:** I don't have real-time access, but you can refer to data from the World Bank or USDA on commodities like wheat, corn, and soybeans.

- **User:** What is the summary of this book: https://sopheaksrey.wordpress.com/wp-content/uploads/2012/04/rich_dad_poor_dad_by_robert_t-_kiyosaki.pdf  
- **Assistant:** "Rich Dad Poor Dad" challenges traditional views on money. It compares the teachings of the author’s real dad vs. his mentor (Rich Dad), emphasizing financial literacy, passive income, and investment mindset.

---

## Demonstration with CSV and Web Link

In this notebook, a **CSV file** is ingested to showcase DocsGPT's compatibility with structured tabular data. This could be:
- Financial datasets
- Log files
- Historical records  

Additionally, a **web link to a public PDF book** was queried to demonstrate that DocsGPT can:
- Parse remote documents  
- Extract relevant text chunks  
- Answer questions about long documents (e.g., "Rich Dad Poor Dad")  

This confirms that **DocsGPT supports a wide variety of formats and sources** beyond just plain text or local files.

---

## Comparison Table
| Feature                       | OpenAI GPT API           | LangChain (RAG)                   | DocsGPT                    |
| ----------------------------- | ------------------------ | --------------------------------- | -------------------------- |
| Cloud Dependency              | Required                 | Required                          | Optional (can run locally) |
| Runs Locally                  | Not supported            | Supported                         | Supported                  |
| REST API Availability         | Not available            | Available (custom setup required) | Available out of the box   |
| Citation Support              | Not supported            | Partial support                   | Fully supported            |
| Interactive UI                | Available                | Not available                     | Available                  |
| Multi-format Document Support | Limited (manual parsing) | Supported                         | Supported                  |


---

## Notebook Naming Convention

This notebook follows the template-guided naming convention:

**BitcoinLLMQA.API.ipynb**

---

## References

- [DocsGPT GitHub](https://github.com/arc53/DocsGPT)  
- [llama-cpp-python](https://github.com/abetlen/llama-cpp-python)  
- [Causify Notebook Tutorial Template](https://github.com/causify-ai/tutorials)  
- [TradingEconomics Stock Market](https://tradingeconomics.com/united-states/stock-market)  
- [Rich Dad Poor Dad (PDF Link)](https://sopheaksrey.wordpress.com/wp-content/uploads/2012/04/rich_dad_poor_dad_by_robert_t-_kiyosaki.pdf)
