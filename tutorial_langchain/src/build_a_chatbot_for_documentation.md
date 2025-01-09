# Tutorial: Building a Documentation QA Bot with LangChain

## Introduction
This tutorial demonstrates how to use LangChain to build a documentation-based QA bot. The bot parses Markdown files, creates embeddings, stores them in a vector database, and retrieves relevant information in response to user queries. Additionally, it supports dynamic updates when documentation changes.

## Setup and Dependencies
### Environment Setup
Set the `OPENAI_API_KEY` environment variable for API access:
```python
import os
os.environ["OPENAI_API_KEY"] = "<your_openai_api_key>"
```

### Required Libraries
```python
from langchain_openai import ChatOpenAI
from langchain.document_loaders import TextLoader
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS, Chroma
from langchain.chains import RetrievalQA
from typing import List
import glob
```

## Key Components

### 1. RecursiveCharacterTextSplitter
`RecursiveCharacterTextSplitter` is a utility in LangChain for splitting large text into smaller, manageable chunks. This ensures that each chunk is processed meaningfully without losing context.

#### Key Features:
- **Recursive Splitting**:
  - Splits text hierarchically using multiple delimiters (e.g., paragraphs, sentences, words).
  - Begins with larger units like paragraphs and progressively splits into smaller units as needed.
- **Customizable Parameters**:
  - `chunk_size`: Maximum length of each text chunk, measured in characters.
  - `chunk_overlap`: Number of characters to overlap between consecutive chunks, ensuring continuity and context.
- **Preprocessing**:
  - Trims unnecessary whitespace and ensures each chunk respects the defined size constraints.

#### Example:
```python
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
split_documents = text_splitter.split_documents(documents)
```
This divides the document into chunks of up to 500 characters, with a 50-character overlap between chunks.

### 2. OpenAIEmbeddings
`OpenAIEmbeddings` generates dense vector representations of text using OpenAI models. These embeddings capture the semantic meaning of text, enabling similarity comparisons.

#### Key Features:
- **Semantic Understanding**:
  - Converts text into high-dimensional vectors that represent its meaning.
  - Useful for tasks like similarity search, clustering, and classification.
- **Integration with Vector Stores**:
  - Works seamlessly with vector databases like FAISS and Chroma for efficient storage and retrieval.
- **Customizable**:
  - Supports various OpenAI models to tailor embeddings for specific use cases.

#### Example:
```python
embeddings = OpenAIEmbeddings()
embedded_text = embeddings.embed_query("What are the guidelines on creating new projects?")
```
This generates an embedding for the query, which can be used for similarity searches.

### 3. FAISS (Facebook AI Similarity Search)
FAISS is a library designed for efficient similarity search and clustering of dense vectors. In LangChain, FAISS serves as a vector store for storing and retrieving embeddings.

#### Key Features:
- **Fast and Scalable**:
  - Optimized for searching large datasets of embeddings.
  - Provides various indexing methods to balance speed and accuracy (e.g., Flat, IVF, HNSW).
- **Similarity Metrics**:
  - Supports cosine similarity, dot product, and other distance metrics for comparing vectors.
- **Efficient Updates**:
  - Allows adding and deleting embeddings dynamically, enabling updates as documents change.

#### Example:
```python
# Create a FAISS vector store
vector_store = FAISS.from_documents(split_documents, embeddings)
retriever = vector_store.as_retriever()
```
This initializes a FAISS vector store with embeddings computed from the split documents, enabling similarity-based retrieval.

### 4. Creating Embeddings and Vector Stores
LangChain supports FAISS and Chroma as vector databases. These libraries store and retrieve embeddings based on similarity search.
```python
# Initialize embeddings
embeddings = OpenAIEmbeddings()

# Create a FAISS vector store
vector_store = FAISS.from_documents(split_documents, embeddings)
retriever = vector_store.as_retriever()
```

### 5. QA Chain Setup
The `RetrievalQA` chain uses a retriever to fetch relevant documents and a language model to answer queries.
```python
qa_chain = RetrievalQA.from_chain_type(
    llm=chat_model,
    retriever=retriever,
    return_source_documents=True
)
```

### 6. Querying the QA Bot
Users can ask questions, and the bot retrieves answers along with the source documents.
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
The bot detects changes in the document folder and updates the vector store accordingly.

#### Detecting Changes
```python
def get_changes_in_documents_folder(folder: str) -> Dict[List[str]]:
    """
    Detect changes in the Markdown files within a folder.

    :param folder: path to the folder containing Markdown files

    :return: dictionary with a `modified` key listing new or updated files.
    """
    markdown_files = list_markdown_files(folder)
    changes = {"modified": []}
    for file_path in markdown_files:
        md5sum, _ = hsystem.system_to_string(f"md5sum {file_path}")[1].split()
        # Detect files that are new or have changed.
        if file_path not in filename_to_md5sum or filename_to_md5sum[file_path] != md5sum:
            changes["modified"].append(file_path)
    return changes
```
- **Key Detail**: The `modified` key lists files that are new or whose contents have changed compared to the stored checksums. This ensures that only updated files are processed.

#### Updating the Vector Store
```python
def update_files_in_vector_store(vector_store: VectorStore, files:List[str]) -> VectorStore:
    """
    Update the vector store with new or modified files.

    :param vector_store: the current vector store instance (FAISS or Chroma)
    :param files: list of file paths to update in the vector store

    :return: updated vector store instance       
    """
    if len(files) == 0:
        print("No new files found")
        return
    # Delete existing embeddings for updated files
    ids_to_delete = []
    for file in files:
        for doc in vector_store:
            if doc.metadata.get('source') == file:
                ids_to_delete.append(doc.id)
    vector_store.delete(ids_to_delete)
    # Why delete existing entries?
    # Deleting ensures that old embeddings associated with outdated content are removed.
    # This prevents stale or conflicting data in the vector store, maintaining its accuracy
    # and consistency.
    # Reprocess the modified files
    documents = parse_markdown_files(files)
    split_documents = text_splitter.split_documents(documents)
    texts = [doc.page_content for doc in split_documents]
    embeddings_list = embeddings.embed_documents(texts)
    vector_store.add_documents(
        documents=split_documents,
        embeddings=embeddings_list
    )
    return vector_store
```

#### Workflow for Updating the Bot
```python
if vector_store:
    changes = get_changes_in_documents_folder(folder)
    vector_store = update_files_in_vector_store(vector_store, changes["modified"])
else:
    vector_store = create_vector_store_from_markdown_files(folder)
```

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
