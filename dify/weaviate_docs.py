"""
Weaviate Document Processing Module.

Process and upload markdown documents to a Weaviate vector database using Ollama embeddings.

Usage:

Library mode:
    import dify.weaviate_docs as dweadocs

    # Default settings
    result = dweadocs.upload_markdown_docs_to_weaviate()

    # Custom parameters
    result = dweadocs.upload_markdown_docs_to_weaviate(
        docs_dir="/path/to/docs",
        collection_name="MyDocs",
        chunk_size=1000
    )

Command-line mode:
    python weaviate_docs.py --help
    python weaviate_docs.py --docs_dir /path/to/docs --collection_name MyDocs

Options:
    --docs_dir: Source directory for markdown files
    --collection_name: Weaviate collection name
    --chunk_size: Text chunk size for splitting
    --chunk_overlap: Overlap between chunks
    --batch_size: Upload batch size
    --ollama_model: Embedding model name
    --ollama_url: Ollama API endpoint
    -v, --verbose: Verbosity level

Prerequisites:
    - Weaviate server (local or remote)
    - Ollama server with embedding model

Workflow:
    1. Start Weaviate and Ollama servers
    2. Run script to upload documentation
    3. Use collection for similarity search

Import as:

import dify.weaviate_docs as dweadocs
"""

import argparse
import logging
import os
from typing import Any, List, Optional

import helpers.hdbg as hdbg
import helpers.hparser as hparser
import langchain.text_splitter as lts
import langchain_community.document_loaders as ldl
import requests
import weaviate
import weaviate.classes.config as wcc

_LOG = logging.getLogger(__name__)

RecursiveCharacterTextSplitter = lts.RecursiveCharacterTextSplitter
UnstructuredMarkdownLoader = ldl.UnstructuredMarkdownLoader
Configure = wcc.Configure
DataType = wcc.DataType
Property = wcc.Property
DEFAULT_COLLECTION_NAME = "Documents"
DEFAULT_ALLOWED_EXTENSIONS = [".md"]
DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 50
DEFAULT_BATCH_SIZE = 100
DEFAULT_OLLAMA_EMBED_URL = "http://localhost:11434/api/embed"
DEFAULT_OLLAMA_MODEL = "nomic-embed-text"

_LOG = logging.getLogger(__name__)


def get_project_root() -> str:
    """
    Get the project root directory from environment variable.

    :return: the project root directory path
    :raises RuntimeError: if PWD environment variable is not set
    """
    project_root = os.environ.get("PWD")
    if not project_root:
        raise RuntimeError(
            "PWD env var not set — please set PWD to your project root"
        )
    return project_root


def create_weaviate_collection(
    client: weaviate.WeaviateClient,
    collection_name: str = DEFAULT_COLLECTION_NAME,
) -> Any:
    """
    Create or get a Weaviate collection for document storage.

    :param client: Weaviate client instance
    :param collection_name: name of the collection to create/get
    :return: the collection object
    """
    if collection_name not in client.collections.list_all():
        _LOG.info("Creating new collection: %s", collection_name)
        client.collections.create(
            name=collection_name,
            vectorizer_config=Configure.Vectorizer.none(),
            properties=[
                Property(name="text", data_type=DataType.TEXT),
                Property(name="filename", data_type=DataType.TEXT),
                Property(name="filepath", data_type=DataType.TEXT),
            ],
        )
    else:
        _LOG.info("Using existing collection: %s", collection_name)

    return client.collections.get(collection_name)


def get_ollama_embedding(
    text: str,
    ollama_url: str = DEFAULT_OLLAMA_EMBED_URL,
    model: str = DEFAULT_OLLAMA_MODEL,
) -> List[float]:
    """
    Get text embedding from Ollama API.

    :param text: text to embed
    :param ollama_url: Ollama API endpoint URL
    :param model: model name to use for embedding
    :return: the embedding vector
    :raises RuntimeError: if Ollama API returns an error
    :raises ValueError: if embedding format is unexpected
    """
    response = requests.post(
        ollama_url,
        headers={"Content-Type": "application/json"},
        json={"model": model, "input": text},
        timeout=30,
    )
    if response.status_code != 200:
        raise RuntimeError(
            f"Ollama error {response.status_code}: {response.text}"
        )
    embedding_list = response.json().get("embeddings")
    if not embedding_list or not isinstance(embedding_list[0], list):
        raise ValueError("Embedding format unexpected or missing.")

    return embedding_list[0]


def process_markdown_file(
    filepath: str,
    docs_dir: str,
    splitter: RecursiveCharacterTextSplitter,
    batch: Any,
    ollama_url: str = DEFAULT_OLLAMA_EMBED_URL,
    model: str = DEFAULT_OLLAMA_MODEL,
) -> None:
    """
    Process a single markdown file and add it to the batch.

    :param filepath: full path to the markdown file
    :param docs_dir: base documentation directory
    :param splitter: text splitter instance
    :param batch: Weaviate batch object
    :param ollama_url: Ollama API endpoint URL
    :param model: model name for embeddings
    :raises RuntimeError: if file processing fails
    """
    filename = os.path.basename(filepath)
    try:
        _LOG.debug("Processing file: %s", filename)

        loader = UnstructuredMarkdownLoader(filepath)
        docs = loader.load()
        chunks = splitter.split_documents(docs)

        chunk_count = 0
        for chunk in chunks:
            text = chunk.page_content.strip()
            if not text:
                continue
            embedding = get_ollama_embedding(text, ollama_url, model)
            batch.add_object(
                properties={
                    "text": text,
                    "filename": filename,
                    "filepath": os.path.relpath(filepath, docs_dir),
                },
                vector=embedding,
            )
            chunk_count += 1
        _LOG.info("Successfully processed %s (%s chunks)", filename, chunk_count)
    except Exception as e:
        _LOG.error("Failed to process %s: %s", filename, e)
        raise RuntimeError(f"Processing failed for {filename}: {e}") from e


def upload_markdown_docs_to_weaviate(
    docs_dir: Optional[str] = None,
    *,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    allowed_extensions: Optional[List[str]] = None,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    batch_size: int = DEFAULT_BATCH_SIZE,
    ollama_url: str = DEFAULT_OLLAMA_EMBED_URL,
    ollama_model: str = DEFAULT_OLLAMA_MODEL,
    weaviate_client: Optional[weaviate.WeaviateClient] = None,
) -> dict:
    """
    Upload markdown documents to Weaviate with Ollama embeddings.

    Process all markdown files in the specified directory, split them
    into chunks, generate embeddings using Ollama, and upload them to a
    Weaviate collection.

    :param docs_dir: directory containing markdown files. Defaults to
        PROJECT_ROOT/docs :param *:
    :param collection_name: name of the Weaviate collection
    :param allowed_extensions: list of file extensions to process
    :param chunk_size: size of text chunks for splitting
    :param chunk_overlap: overlap between consecutive chunks
    :param batch_size: number of objects to batch before uploading
    :param ollama_url: Ollama API endpoint URL
    :param ollama_model: Ollama model name for embeddings
    :param weaviate_client: optional pre-configured Weaviate client
    :return: summary of the upload process with total file count
    :raises RuntimeError: if PWD environment variable is not set (when
        docs_dir is None), or if any file processing fails
    :raises FileNotFoundError: if documentation directory does not exist
    """
    if docs_dir is None:
        project_root = get_project_root()
        docs_dir = os.path.join(project_root, "docs")
    if allowed_extensions is None:
        allowed_extensions = DEFAULT_ALLOWED_EXTENSIONS.copy()
    _LOG.info("Starting document upload process")
    _LOG.info("Documentation directory: %s", docs_dir)
    _LOG.info("Collection name: %s", collection_name)
    _LOG.info("Ollama model: %s", ollama_model)
    _LOG.info("Chunk size: %s, overlap: %s", chunk_size, chunk_overlap)
    if not os.path.exists(docs_dir):
        raise FileNotFoundError(f"Documentation directory not found: {docs_dir}")
    client = weaviate_client or weaviate.connect_to_local()
    should_close_client = weaviate_client is None
    try:
        collection = create_weaviate_collection(client, collection_name)

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
        total_files = 0
        _LOG.info("Starting batch processing with batch size: %s", batch_size)
        with collection.batch.fixed_size(batch_size) as batch:
            for root, _, files in os.walk(docs_dir):
                for filename in files:
                    if not any(
                        filename.endswith(ext) for ext in allowed_extensions
                    ):
                        continue
                    total_files += 1
                    filepath = os.path.join(root, filename)
                    # Process the file (will raise exception if failed).
                    process_markdown_file(
                        filepath,
                        docs_dir,
                        splitter,
                        batch,
                        ollama_url,
                        ollama_model,
                    )
        result = {
            "total_files": total_files,
            "collection_name": collection_name,
            "docs_directory": docs_dir,
        }
        _LOG.info("Upload process completed successfully")
        _LOG.info("Total files processed: %s", total_files)
        _LOG.info("Collection: %s", collection_name)
        _LOG.info(
            "All markdown files uploaded using '%s' via Ollama", ollama_model
        )
        return result
    finally:
        if should_close_client:
            client.close()
            _LOG.debug("Weaviate client connection closed")


def _parse() -> argparse.ArgumentParser:
    """
    Parse command line arguments for the Weaviate document upload script.

    :return: configured argument parser
    """
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--docs_dir",
        type=str,
        help="Directory containing markdown files to upload (default: PROJECT_ROOT/docs)",
    )
    parser.add_argument(
        "--collection_name",
        type=str,
        default=DEFAULT_COLLECTION_NAME,
        help=f"Name of the Weaviate collection (default: {DEFAULT_COLLECTION_NAME})",
    )
    parser.add_argument(
        "--chunk_size",
        type=int,
        default=DEFAULT_CHUNK_SIZE,
        help=f"Size of text chunks for splitting (default: {DEFAULT_CHUNK_SIZE})",
    )
    parser.add_argument(
        "--chunk_overlap",
        type=int,
        default=DEFAULT_CHUNK_OVERLAP,
        help=f"Overlap between consecutive chunks (default: {DEFAULT_CHUNK_OVERLAP})",
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help=f"Number of objects to batch before uploading (default: {DEFAULT_BATCH_SIZE})",
    )
    parser.add_argument(
        "--ollama_model",
        type=str,
        default=DEFAULT_OLLAMA_MODEL,
        help=f"Ollama model name for embeddings (default: {DEFAULT_OLLAMA_MODEL})",
    )
    parser.add_argument(
        "--ollama_url",
        type=str,
        default=DEFAULT_OLLAMA_EMBED_URL,
        help=f"Ollama API endpoint URL (default: {DEFAULT_OLLAMA_EMBED_URL})",
    )
    hparser.add_verbosity_arg(parser)
    return parser


def _main(parser: argparse.ArgumentParser) -> None:
    """
    Run the document upload process with command line arguments.

    :param parser: configured argument parser
    """
    args = parser.parse_args()
    hdbg.init_logger(verbosity=args.log_level, use_exec_path=True)
    try:
        _LOG.info("Starting Weaviate document upload process")
        result = upload_markdown_docs_to_weaviate(
            docs_dir=args.docs_dir,
            collection_name=args.collection_name,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
            batch_size=args.batch_size,
            ollama_url=args.ollama_url,
            ollama_model=args.ollama_model,
        )
        _LOG.info("Document upload process completed successfully")
        return result
    except Exception as e:
        _LOG.error("Error during upload: %s", e)
        raise

if __name__ == "__main__":
    _main(_parse())
