# Ollama API Documentation

This document describes both the native Ollama API and our Python wrapper for building a semantic document search engine.

## 1. Native Ollama API

[Ollama](https://ollama.ai/) is a framework for running large language models locally. Its API provides endpoints for generating text, managing models, and more.

### Key Endpoints

#### Generate Text
```
POST http://localhost:11434/api/generate
```

Request body:
```json
{
  "model": "llama3",
  "prompt": "Your prompt here",
  "system": "Optional system prompt",
  "stream": false,
  "max_tokens": 2000,
  "temperature": 0.7
}
```

Response:
```json
{
  "model": "llama3",
  "response": "Generated text here",
  "done": true
}
```

#### List Models
```
GET http://localhost:11434/api/tags
```

Response:
```json
{
  "models": [
    {
      "name": "llama3",
      "size": 4100000000,
      "modified_at": "2023-06-01T12:00:00Z"
    },
    {
      "name": "mistral",
      "size": 3800000000,
      "modified_at": "2023-05-01T12:00:00Z"
    }
  ]
}
```

## 2. Our Python Wrapper Layer

Our wrapper provides a simple, easy-to-use interface for building a semantic document search engine with vector embeddings and optional query enhancement using Ollama.

### Core Components

1. **Document Processing**: Functions to extract and chunk text from documents
2. **Embedding Generation**: Convert text into vector embeddings for semantic search
3. **Vector Indexing**: Build and search FAISS indices for fast similarity search
4. **Query Enhancement**: Use Ollama to improve search queries

### API Functions

#### Ollama API Wrapper

```python
def query_ollama(prompt, model="llama3", system_prompt=None, max_tokens=2000, temperature=0.7)
```
Send a query to the Ollama API and get a response. Used primarily for query enhancement.

```python
def list_ollama_models()
```
List all available Ollama models.

#### Document Processing

```python
def extract_text(file_path)
```
Extract plain text from a file. Supports various formats:
- Plain text files (.txt)
- Markdown documents (.md)
- PDF documents using PyMuPDF
- Word documents (.docx) using python-docx
- Will attempt to read other file types as text

```python
def chunk_text(text, chunk_size=1000, overlap=200)
```
Split text into overlapping chunks for better semantic search.

#### Embedding Generation

```python
def get_embedding_model(model_name="sentence-transformers/all-mpnet-base-v2")
```
Get a singleton embedding model instance for efficient reuse.

```python
def embed_text(text, model=None)
```
Generate embeddings for a piece of text.

#### Document Indexing

```python
def process_document(path, model=None, use_cache=True, cache_dir="index/cache")
```
Process a single document and return its embeddings and metadata.

```python
def build_document_index(file_paths, index_path="index/faiss_index.bin", metadata_path="index/metadata.pkl", 
                      progress_callback=None, use_parallel=True, max_workers=None)
```
Build a FAISS vector index from document files for fast similarity search.

```python
def scan_directory(directory, extensions=None)
```
Scan a directory for files to index based on their extensions.

#### Document Search

```python
def search_documents(query, top_k=5, index_path="index/faiss_index.bin", metadata_path="index/metadata.pkl")
```
Search for documents using semantic similarity.

## 3. Integration Architecture

Our system integrates these components in the following way:

1. **Document Collection**: Files are scanned from directories and processed
2. **Indexing**: Documents are chunked and converted to vector embeddings, then indexed with FAISS
3. **Query Enhancement**: User queries can be optionally improved using Ollama
4. **Search**: Queries are converted to embeddings and matched against the document index
5. **Result Ranking**: Documents are ranked by similarity score

This architecture allows for efficient semantic document search using vector embeddings, optionally enhanced with locally-running LLMs.

## 4. Usage Example

```python
import Ollama_utils as ou

# Scan a directory for documents
file_paths = ou.scan_directory("./my_documents")

# Build a search index
ou.build_document_index(file_paths)

# Simple search
results = ou.search_documents("How do neural networks work?")

# Enhanced search with Ollama
query = "How do neural networks work?"
enhanced_query = ou.query_ollama(
    f"Rewrite this search query to be more comprehensive: '{query}'",
    model="llama3"
)
enhanced_results = ou.search_documents(enhanced_query)

# Print results
for result in enhanced_results:
    print(f"{result['filename']} (Score: {result['score']:.2f})")
    print(result['snippet'][:200])
``` 