"""
Weaviate Document Processing Module.

This module provides functionality to process and upload markdown documents
to a Weaviate vector database using Ollama embeddings.

Import as:

import dify.weaviate_docs as dweadocs
"""

import logging
import os
from typing import Any, List, Optional

import langchain.text_splitter as lts
import langchain_community.document_loaders as ldl
import requests
import weaviate
import weaviate.classes.config as wcc

# Type aliases for better readability.
RecursiveCharacterTextSplitter = lts.RecursiveCharacterTextSplitter
UnstructuredMarkdownLoader = ldl.UnstructuredMarkdownLoader
Configure = wcc.Configure
DataType = wcc.DataType
Property = wcc.Property

# Default configuration constants.
DEFAULT_COLLECTION_NAME = "Documents"
DEFAULT_ALLOWED_EXTENSIONS = [".md"]
DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 50
DEFAULT_BATCH_SIZE = 100
DEFAULT_OLLAMA_EMBED_URL = "http://localhost:11434/api/embed"
DEFAULT_OLLAMA_MODEL = "nomic-embed-text"

# Configure module logger.
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
    # Create collection with no internal vectorizer if it doesn't exist.
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
) -> bool:
    """
    Process a single markdown file and add it to the batch.

    :param filepath: full path to the markdown file
    :param docs_dir: base documentation directory
    :param splitter: text splitter instance
    :param batch: Weaviate batch object
    :param ollama_url: Ollama API endpoint URL
    :param model: model name for embeddings
    :return: True if successful, False if failed
    """
    filename = os.path.basename(filepath)

    try:
        _LOG.debug("Processing file: %s", filename)

        # Load and split the document.
        loader = UnstructuredMarkdownLoader(filepath)
        docs = loader.load()
        chunks = splitter.split_documents(docs)

        chunk_count = 0
        # Process each chunk.
        for chunk in chunks:
            text = chunk.page_content.strip()

            # Skip empty chunks.
            if not text:
                continue

            # Get embedding from Ollama.
            embedding = get_ollama_embedding(text, ollama_url, model)

            # Add to batch.
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
        return True

    except Exception as e:
        _LOG.error("Failed to process %s: %s", filename, e)
        return False


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
        PROJECT_ROOT/docs
    :param collection_name: name of the Weaviate collection
    :param allowed_extensions: list of file extensions to process
    :param chunk_size: size of text chunks for splitting
    :param chunk_overlap: overlap between consecutive chunks
    :param batch_size: number of objects to batch before uploading
    :param ollama_url: Ollama API endpoint URL
    :param ollama_model: Ollama model name for embeddings
    :param weaviate_client: optional pre-configured Weaviate client
    :return: summary of the upload process with counts of
        successful/failed files
    :raises RuntimeError: if PWD environment variable is not set (when
        docs_dir is None)
    :raises FileNotFoundError: if documentation directory does not exist
    """
    # Set default values.
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

    # Validate docs directory exists.
    if not os.path.exists(docs_dir):
        raise FileNotFoundError(f"Documentation directory not found: {docs_dir}")

    # Initialize Weaviate client if not provided.
    client = weaviate_client or weaviate.connect_to_local()
    should_close_client = weaviate_client is None

    try:
        # Create or get collection.
        collection = create_weaviate_collection(client, collection_name)

        # Initialize text splitter.
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

        # Track processing results.
        successful_files = 0
        failed_files = 0
        total_files = 0

        # Process files in batches.
        _LOG.info("Starting batch processing with batch size: %s", batch_size)
        with collection.batch.fixed_size(batch_size) as batch:
            for root, _, files in os.walk(docs_dir):
                for filename in files:
                    # Filter by allowed extensions.
                    if not any(
                        filename.endswith(ext) for ext in allowed_extensions
                    ):
                        continue

                    total_files += 1
                    filepath = os.path.join(root, filename)

                    # Process the file.
                    if process_markdown_file(
                        filepath,
                        docs_dir,
                        splitter,
                        batch,
                        ollama_url,
                        ollama_model,
                    ):
                        successful_files += 1
                    else:
                        failed_files += 1

        # Summary.
        result = {
            "total_files": total_files,
            "successful_files": successful_files,
            "failed_files": failed_files,
            "collection_name": collection_name,
            "docs_directory": docs_dir,
        }

        _LOG.info("Upload process completed")
        _LOG.info("Total files processed: %s", total_files)
        _LOG.info("Successful uploads: %s", successful_files)
        _LOG.info("Failed uploads: %s", failed_files)
        _LOG.info("Collection: %s", collection_name)
        _LOG.info(
            "All markdown files uploaded using '%s' via Ollama", ollama_model
        )

        return result

    finally:
        # Close client only if we created it.
        if should_close_client:
            client.close()
            _LOG.debug("Weaviate client connection closed")


def configure_logging(
    *, level: int = logging.INFO, format_string: Optional[str] = None
) -> None:
    """
    Configure logging for the module.

    :param level: logging level (e.g., logging.INFO, logging.DEBUG)
    :param format_string: custom format string for log messages
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Only configure if not already configured.
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=level,
            format=format_string,
            handlers=[
                logging.StreamHandler(),
            ],
        )

    _LOG.setLevel(level)


def main():
    """
    Run the document upload process with default settings.
    """
    # Configure logging for standalone execution.
    configure_logging(level=logging.INFO)
    try:
        _LOG.info("Starting Weaviate document upload process")
        result = upload_markdown_docs_to_weaviate()
        _LOG.info("Document upload process completed successfully")
        return result
    except Exception as e:
        _LOG.error("Error during upload: %s", e)
        raise


# Allow running as script.
if __name__ == "__main__":
    main()
