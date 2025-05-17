# Semantic Document Search Engine: Complete Example

This example demonstrates how to build a semantic document search engine using Ollama and FAISS for vector similarity search. This application allows you to:

1. Scan and index a directory of documents
2. Search documents using semantic similarity
3. Enhance search queries using locally-running LLMs

## Prerequisites

- Python 3.9+
- Ollama installed and running locally (https://ollama.ai)
- Required Python packages:
  - faiss-cpu
  - sentence-transformers
  - requests
  - numpy
  - streamlit
  - python-docx (for Word document support)
  - PyMuPDF (for PDF support)

## Supported Document Types

The search engine can process the following document formats:
- Plain text files (.txt)
- Markdown documents (.md)
- PDF documents (.pdf)
- Microsoft Word documents (.docx)
- Code files (Python, JavaScript, HTML, etc.)

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Start Ollama server
4. Pull a model (e.g., llama3):
   ```
   ollama pull llama3
   ```

## Example Application: Technical Documentation Search Engine

Let's build a technical documentation search engine that can help find relevant documents in a codebase or technical documentation repository.

### 1. Set Up the Project Structure

```
project/
├── docs/                 # Technical documentation
├── src/                  # Source code
├── search_engine.py      # Our search engine application
└── requirements.txt      # Dependencies
```

### 2. Create the Search Engine Application

```python
# search_engine.py
import os
import Ollama_utils as ou
import argparse

def setup_index(docs_dir):
    """Set up the document index"""
    print(f"Scanning directory: {docs_dir}")
    file_paths = ou.scan_directory(docs_dir)
    print(f"Found {len(file_paths)} files to index")
    
    def progress_callback(progress, message):
        print(f"Progress: {progress*100:.1f}% - {message}")
    
    print("Building document index...")
    success = ou.build_document_index(
        file_paths,
        progress_callback=progress_callback
    )
    
    if success:
        print("✅ Index built successfully")
    else:
        print("❌ Failed to build index")
    
    return success

def search_docs(query, top_k=5, use_ollama=True, model="llama3"):
    """Search documents with a query, optionally enhanced by Ollama"""
    if use_ollama:
        print(f"Original query: {query}")
        enhanced_query = ou.query_ollama(
            f"Rewrite this search query to better find technical documentation (return only the revised query): '{query}'",
            model=model
        )
        enhanced_query = enhanced_query.strip().replace('"', '').split('\n')[0]
        print(f"Enhanced query: {enhanced_query}")
        query = enhanced_query
    
    print(f"Searching for: {query}")
    results = ou.search_documents(query, top_k=top_k)
    
    if "error" in results:
        print(f"Error: {results['error']}")
        return None
    
    print(f"Found {len(results)} relevant documents:")
    for i, result in enumerate(results):
        print(f"\n[{i+1}] {result['filename']} (Score: {result['score']:.2f})")
        print(f"    Path: {result['file_path']}")
        print(f"    {result['snippet'][:150]}...")
    
    return results

def interactive_mode(model="llama3"):
    """Run an interactive session"""
    print("🔍 Technical Documentation Search Engine")
    print("Type 'exit' to quit, 'index <directory>' to index documents")
    
    use_ollama = True
    
    while True:
        query = input("\n> ")
        
        if query.lower() == "exit":
            break
        
        if query.lower().startswith("index "):
            dir_path = query[6:].strip()
            if os.path.isdir(dir_path):
                setup_index(dir_path)
            else:
                print(f"Directory not found: {dir_path}")
        elif query.lower() == "toggle ollama":
            use_ollama = not use_ollama
            print(f"Ollama query enhancement: {'enabled' if use_ollama else 'disabled'}")
        else:
            search_docs(query, use_ollama=use_ollama, model=model)

def main():
    parser = argparse.ArgumentParser(description="Technical Documentation Search Engine")
    parser.add_argument("--index", help="Directory to index")
    parser.add_argument("--model", default="llama3", help="Ollama model to use for query enhancement")
    parser.add_argument("--query", help="Single query mode")
    parser.add_argument("--no-ollama", action="store_true", help="Disable Ollama query enhancement")
    parser.add_argument("--top-k", type=int, default=5, help="Number of results to return")
    
    args = parser.parse_args()
    
    if args.index:
        setup_index(args.index)
    
    if args.query:
        search_docs(args.query, top_k=args.top_k, use_ollama=not args.no_ollama, model=args.model)
    else:
        interactive_mode(model=args.model)

if __name__ == "__main__":
    main()
```

### 3. Requirements

Add the following to `requirements.txt`:

```
faiss-cpu==1.7.3
sentence-transformers==2.2.2
numpy==1.24.0
requests==2.28.1
streamlit==1.25.0
```

### 4. Using the Search Engine

1. First, index your documents:
   ```
   python search_engine.py --index ./docs
   ```

2. Search interactively:
   ```
   python search_engine.py
   ```

3. Or perform a single search:
   ```
   python search_engine.py --query "How to implement API authentication"
   ```

### Example Session

Here's an example interactive session:

```
🔍 Technical Documentation Search Engine
Type 'exit' to quit, 'index <directory>' to index documents

> index ./docs
Scanning directory: ./docs
Found 47 files to index
Building document index...
Progress: 10.0% - Processed 5/47 files
Progress: 20.0% - Processed 10/47 files
Progress: 30.0% - Processed 15/47 files
...
Progress: 100.0% - Indexing complete!
✅ Index built successfully

> How to secure an API
Original query: How to secure an API
Enhanced query: What are the best practices for securing a RESTful API, including authentication, authorization, and encryption methods?
Searching for: What are the best practices for securing a RESTful API, including authentication, authorization, and encryption methods?
Found 5 relevant documents:

[1] security_guide.md (Score: 0.89)
    Path: ./docs/security_guide.md
    # API Security Guide ## Best Practices for Securing RESTful APIs This document outlines comprehensive security measures for protecting...

[2] authentication.md (Score: 0.85)
    Path: ./docs/authentication.md
    # Authentication Methods ## JSON Web Tokens (JWT) JWTs provide a stateless authentication mechanism. Each token contains encoded...

[3] oauth2_implementation.md (Score: 0.79)
    Path: ./docs/oauth2_implementation.md
    # OAuth 2.0 Implementation This guide explains how to implement OAuth 2.0 for API authentication. ## Authorization Code Flow...

[4] api_design.md (Score: 0.71)
    Path: ./docs/api_design.md
    # API Design Principles ## Security Considerations When designing APIs, security should be a primary concern. Always use HTTPS...

[5] encryption_guide.md (Score: 0.68)
    Path: ./docs/encryption_guide.md
    # Data Encryption Guide This document explains how to properly encrypt data in transit and at rest. ## Transport Layer Security...

> toggle ollama
Ollama query enhancement: disabled

> How to secure an API
Searching for: How to secure an API
Found 5 relevant documents:
[1] security_guide.md (Score: 0.82)
    Path: ./docs/security_guide.md
    # API Security Guide ## Best Practices for Securing RESTful APIs This document outlines comprehensive security measures for protecting...

> exit
```

## Streamlit Web Interface

For a more user-friendly experience, you can create a Streamlit web interface:

```python
# app.py
import streamlit as st
import Ollama_utils as ou
import os

st.set_page_config(
    page_title="Semantic Document Search",
    page_icon="🔍",
    layout="wide"
)

# Initialize session state
if "search_results" not in st.session_state:
    st.session_state.search_results = None
if "enhanced_query" not in st.session_state:
    st.session_state.enhanced_query = None

st.title("🔍 Semantic Document Search")
st.write("Find relevant documents using semantic search technology.")

# Sidebar configuration
with st.sidebar:
    st.header("Configuration")
    docs_dir = st.text_input("Document Directory", value="./docs")
    use_ollama = st.checkbox("Enhance queries with Ollama", value=True)
    
    if st.button("Index Documents"):
        if os.path.exists(docs_dir):
            with st.spinner("Indexing documents..."):
                files = ou.scan_directory(docs_dir)
                st.info(f"Found {len(files)} files")
                success = ou.build_document_index(files)
                if success:
                    st.success("Indexing complete!")
                else:
                    st.error("Indexing failed")
        else:
            st.error(f"Directory not found: {docs_dir}")

# Search interface
query = st.text_input("Search Query")
top_k = st.slider("Number of results", 1, 20, 5)

if st.button("Search") and query:
    # Enhance query with Ollama if enabled
    if use_ollama:
        with st.spinner("Enhancing query..."):
            enhanced_query = ou.query_ollama(
                f"Rewrite this search query to be more comprehensive: '{query}'. Return only the enhanced query.",
                model="llama3"
            )
            st.session_state.enhanced_query = enhanced_query.strip()
            st.info(f"Enhanced query: {st.session_state.enhanced_query}")
            search_query = st.session_state.enhanced_query
    else:
        search_query = query
    
    # Perform search
    with st.spinner("Searching..."):
        st.session_state.search_results = ou.search_documents(search_query, top_k=top_k)
    
    # Display results
    if st.session_state.search_results and "error" not in st.session_state.search_results:
        st.success(f"Found {len(st.session_state.search_results)} relevant documents")
        
        for i, result in enumerate(st.session_state.search_results):
            with st.expander(f"Result {i+1}: {result['filename']} (Score: {result['score']:.3f})"):
                st.text(result['snippet'])
                st.markdown(f"**File:** {result['file_path']}")
    elif st.session_state.search_results:
        st.error(st.session_state.search_results["error"])
```

To run the Streamlit interface:

```
streamlit run app.py
```

## Benefits of This Approach

This document search engine provides several advantages:

1. **Semantic search**: Finds relevant documents based on meaning, not just keywords
2. **Privacy**: All processing happens locally, with no data sent to external services
3. **Query enhancement**: Uses Ollama to improve search queries for better results
4. **Efficient indexing**: Fast vector search with FAISS
5. **Flexible interface**: Command-line or web interface options

## Extending the Application

The search engine can be extended in several ways:

1. **Additional document formats**: Add support for PDFs, Word documents, code files, etc.
2. **Search filters**: Allow filtering by file type, date, author, etc.
3. **Result clustering**: Group similar results together
4. **Relevance feedback**: Let users mark results as relevant/irrelevant to improve future searches
5. **Custom embedding models**: Train domain-specific embedding models for better results 