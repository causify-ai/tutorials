# Local AI-Powered Document Search Engine

A streamlined document search engine that leverages AI embeddings to enable semantic search across your local files using Ollama and FAISS.

## Features

- **Local Document Indexing**: Index text, PDF, and Word documents from any local directory
- **Semantic Search**: Find documents based on meaning, not just keywords
- **AI-Enhanced Queries**: Automatically improve search queries using LLM
- **Query Fallback**: Intelligently reverts to original query if enhanced search fails
- **Privacy-Focused**: All processing happens locally on your machine
- **User-Friendly Interface**: Simple Streamlit UI for easy interaction
- **Efficient Search**: Fast retrieval using FAISS vector database with optimized thresholds
- **Multithreaded Indexing**: Parallel processing for faster document indexing
- **Smart Chunking**: Improved document chunking with sentence awareness and better overlap

## Requirements

- Python 3.8+
- Ollama (for embedding generation and query enhancement)

## Installation

1. Clone this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Ensure you have [Ollama](https://ollama.ai/) installed and running locally
4. Pull a model (e.g., llama3): `ollama pull llama3`

## Usage

1. Start the application:

```bash
streamlit run app.py
```

2. In the web interface:
   - Enter the directory path you want to index or upload individual files
   - Click "Scan Files" to locate supported documents
   - Confirm and click "Build Index" to process the documents
   - Use the search bar to find information across your documents
   - Adjust the similarity threshold for more or fewer results
   - Toggle "Enhance Query" to use LLM for improving search queries

## Docker Support

For easier deployment, you can use Docker:

```bash
# Build the image
docker build -t document-search-engine .

# Run the container
docker run -d --name doc-search -p 8501:8501 -p 11434:11434 -v ${PWD}:/app document-search-engine
```

Access the application at http://localhost:8501

## Architecture

The application consists of several components:

- `app.py`: Main Streamlit interface
- `Ollama_utils.py`: Core functionality including:
  - Document processing and chunking
  - Vector embedding
  - FAISS index creation and searching
  - Query enhancement with Ollama
  - Question answering with document context

## Supported File Types

- Text files (.txt)
- Markdown (.md)
- PDF documents (.pdf)
- Word documents (.docx)
- Source code files (.py, .js, .html, .css, .json)
- CSV data (.csv)

## Advanced Configuration

You can modify these settings in the code:

- `MAX_FILE_SIZE`: Maximum file size to process (default: 50MB)
- `EXCLUDED_DIR_NAMES`: Directories to skip during scanning
- `SUPPORTED_EXTENSIONS`: File types to index
- `CHUNK_SIZE`: Size of document chunks (default: 1000 characters)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 400 characters)
- `SIMILARITY_THRESHOLD`: Minimum similarity score (default: 0.1)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Uses [sentence-transformers](https://www.sbert.net/) for text embeddings
- Employs [FAISS](https://github.com/facebookresearch/faiss) for efficient similarity search
- Built with [Streamlit](https://streamlit.io/) for the user interface
- Powered by [Ollama](https://ollama.ai/) for local AI processing
