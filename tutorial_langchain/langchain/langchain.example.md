<!-- toc -->

- [Introduction](#introduction)
- [Setup and Dependencies](#setup-and-dependencies)
  * [Building and Running the Docker Container](#building-and-running-the-docker-container)
  * [Environment Setup](#environment-setup)
- [Key Components](#key-components)
  * [1. RecursiveCharacterTextSplitter](#1-recursivecharactertextsplitter)
    + [Key Features:](#key-features)
    + [Example:](#example)
  * [2. OpenAIEmbeddings](#2-openaiembeddings)
    + [Key Features:](#key-features-1)
    + [Example:](#example-1)
  * [3. FAISS (Facebook AI Similarity Search)](#3-faiss-facebook-ai-similarity-search)
    + [Key Features:](#key-features-2)
    + [Example:](#example-2)
- [4. QA Chain Setup](#4-qa-chain-setup)
  * [6. Querying the QA Bot](#6-querying-the-qa-bot)
  * [7. Dynamic Document Updates](#7-dynamic-document-updates)
    + [Detecting Changes](#detecting-changes)
    + [Workflow for Updating the Bot](#workflow-for-updating-the-bot)
- [Complete Workflow](#complete-workflow)
- [Example Usage](#example-usage)

<!-- tocstop -->

# Introduction

This tutorial demonstrates how to use `LangChain` to build a documentation-based
QA bot. The bot parses Markdown files, creates embeddings, stores them in a
vector database, and retrieves relevant information in response to user queries.
Additionally, it supports dynamic updates when documentation changes.

![alt text](/image-6.png)

## Setup and Dependencies

### Building and Running the Docker Container

1. **Activate virtual environment:**
   ```bash
   > source dev_scripts_tutorial_data/thin_client/setenv.sh
   ```
2. **Build Docker Image:**
   ```bash
   > i docker_build_local_image --version 1.0.0
   ```
3. **Run Container:**
   ```bash
   > i docker_bash --skip-pull --stage local --version 1.0.0
   ```
4. **Launch Jupyter Notebook:**
   ```bash
   > i docker_jupyter --skip-pull --stage local --version 1.0.0 -d
   ```

### Environment Setup

Set the `OPENAI_API_KEY` environment variable for API access:

```python
import os
os.environ["OPENAI_API_KEY"] = "<your_openai_api_key>"
```

## Key Components

### 1. RecursiveCharacterTextSplitter

`RecursiveCharacterTextSplitter` is a utility in `LangChain` for splitting large
text into smaller, manageable chunks. This ensures that each chunk is processed
meaningfully without losing context.

#### Key Features:

- **Recursive Splitting**:
  - Splits text hierarchically using multiple delimiters (e.g., paragraphs,
    sentences, words).
  - Begins with larger units like paragraphs and progressively splits into
    smaller units as needed.
- **Customizable Parameters**:
  - `chunk_size`: Maximum length of each text chunk, measured in characters.
  - `chunk_overlap`: Number of characters to overlap between consecutive chunks,
    ensuring continuity and context.
- **Preprocessing**:
  - Trims unnecessary whitespace and ensures each chunk respects the defined
    size constraints.

#### Example:

```python
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
split_documents = text_splitter.split_documents(documents)
```

This divides the document into chunks of up to 500 characters, with a
50-character overlap between chunks.

### 2. OpenAIEmbeddings

`OpenAIEmbeddings` generates dense vector representations of text using OpenAI
models. These embeddings capture the semantic meaning of text, enabling
similarity comparisons.

#### Key Features:

- **Semantic Understanding**:
  - Converts text into high-dimensional vectors that represent its meaning.
  - Useful for tasks like similarity search, clustering, and classification.
- **Integration with Vector Stores**:
  - Works seamlessly with vector databases like FAISS and Chroma for efficient
    storage and retrieval.
- **Customizable**:
  - Supports various OpenAI models to tailor embeddings for specific use cases.

#### Example:

```python
embeddings = OpenAIEmbeddings()
embedded_text = embeddings.embed_query("What are the guidelines on creating new projects?")
```

This generates an embedding for the query, which can be used for similarity
searches.

### 3. FAISS (Facebook AI Similarity Search)

![alt text](/image-7.png)

FAISS is a library designed for efficient similarity search and clustering of
dense vectors. In `LangChain`, FAISS serves as a vector store for storing and
retrieving embeddings.

#### Key Features:

- **Fast and Scalable**:
  - Optimized for searching large datasets of embeddings.
  - Provides various indexing methods to balance speed and accuracy (e.g., Flat,
    IVF, HNSW).
- **Similarity Metrics**:
  - Supports cosine similarity, dot product, and other distance metrics for
    comparing vectors.
- **Efficient Updates**:
  - Allows adding and deleting embeddings dynamically, enabling updates as
    documents change.

#### Example:

```python
# Create a FAISS vector store
vector_store = FAISS.from_documents(split_documents, embeddings)
retriever = vector_store.as_retriever()
```

This initializes a FAISS vector store with embeddings computed from the split
documents, enabling similarity-based retrieval.

## 4. QA Chain Setup

![alt text](/image-8.png)

The `RetrievalQA` chain uses a retriever to fetch relevant documents and a
language model to answer queries.

```python
qa_chain = RetrievalQA.from_chain_type(
    llm=chat_model,
    retriever=retriever,
    return_source_documents=True
)
```

### 6. Querying the QA Bot

Users can ask questions, and the bot retrieves answers along with the source
documents.

```python
query = "What are the guidelines on creating new projects?"
result = qa_chain({"query": query})

print("Answer:")
print(result['result'])

print("\nSource Documents:")
for doc in result['source_documents']:
    print(f"File: {doc.metadata['source']}")
    print(f"Excerpt: {doc.page_content[:200]}...")
```

### 7. Dynamic Document Updates

![alt text](/image-9.png)

The bot detects changes in the document folder and updates the vector store
accordingly.

#### Detecting Changes

- The function `get_changes_in_documents_folder()` detects changes in the
  Markdown files within a folder by using a hash signature.
- The `modified` key lists files that are new or whose contents have changed
  compared to the stored checksums. This ensures that only updated files are
  processed.

#### Workflow for Updating the Bot

```python
if vector_store:
    changes = get_changes_in_documents_folder(folder)
    vector_store = update_files_in_vector_store(vector_store, changes["modified"])
else:
    vector_store = create_vector_store_from_markdown_files(folder)
```

- `update_files_in_vector_store` update the vector store with new or modified
  files.

## Complete Workflow

1. Parse Markdown files.
2. Split documents into chunks.
3. Create a vector store and compute embeddings.
4. Set up the QA chain.
5. Detect and handle document changes dynamically.

## Example Usage

- Ask a question:

  ```python
  query = "What are the goals for the tutorial project?"
  result = qa_chain({"query": query})
  print(result['result'])
  ```

- View source document excerpts:
  ```python
  for doc in result['source_documents']:
      print(doc.metadata['source'])
      print(doc.page_content[:200])
  ```
