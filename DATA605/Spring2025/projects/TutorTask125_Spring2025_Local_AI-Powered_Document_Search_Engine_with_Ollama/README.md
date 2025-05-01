# Local AI-Powered Document Search Engine

A streamlined document search engine that leverages AI embeddings to enable semantic search across your local files using Ollama and FAISS.

## Features

- **Local Document Indexing**: Index text, PDF, and Word documents from any local directory
- **Semantic Search**: Find documents based on meaning, not just keywords
- **Privacy-Focused**: All processing happens locally on your machine
- **User-Friendly Interface**: Simple Streamlit UI for easy interaction
- **Efficient Search**: Fast retrieval using FAISS vector database
- **Multithreaded Indexing**: Parallel processing for faster document indexing

## Requirements

- Python 3.8+
- Ollama (for embedding generation)

## Installation

1. Clone this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Ensure you have [Ollama](https://ollama.ai/) installed and running locally

## Usage

1. Start the application:

```bash
streamlit run app.py
```

2. In the web interface:
   - Enter the directory path you want to index
   - Click "Scan Files" to locate supported documents
   - Confirm and click "Build Index" to process the documents
   - Use the search bar to find information across your documents

## Architecture

The application consists of several components:

- `app.py`: Main Streamlit interface
- `utils/`:
  - `file_scanner.py`: Identifies supported documents in specified directories
  - `processing.py`: Extracts and chunks text from various document formats
  - `build_index.py`: Creates FAISS vector index from document chunks
  - `search.py`: Handles semantic search against the index

## Supported File Types

- Text files (.txt)
- PDF documents (.pdf)
- Word documents (.docx)

## Advanced Configuration

You can modify these settings in the code:

- `MAX_FILE_SIZE`: Maximum file size to process (default: 100MB)
- `EXCLUDED_DIR_NAMES`: Directories to skip during scanning
- `SUPPORTED_EXTENSIONS`: File types to index

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Uses [sentence-transformers](https://www.sbert.net/) for text embeddings
- Employs [FAISS](https://github.com/facebookresearch/faiss) for efficient similarity search
- Built with [Streamlit](https://streamlit.io/) for the user interface
