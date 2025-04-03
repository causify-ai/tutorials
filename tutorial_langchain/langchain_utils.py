import hashlib
import logging
import os
import pathlib
from typing import Any, Dict, List, Optional

import helpers.hdbg as hdbg
import langchain
import langchain.chains
import langchain.docstore.document as lngchdocstordoc
import langchain.embeddings
import langchain.hub
import langchain.text_splitter
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_community.vectorstores import FAISS
import tqdm

_LOG = logging.getLogger(__name__)


def list_markdown_files(dir_path: str) -> List[str]:
    """
    Recursively list all markdown files in a directory.

    :param dir_path: path to directory containing markdown files
    :return: list of absolute paths to markdown files
    """
    md_files = []
    for root, _, files in os.walk(dir_path):
        for file in files:
            if file.endswith(".md"):
                md_files.append(str(pathlib.Path(root) / file))
    _LOG.info("Found %d markdown files in %s", len(md_files), dir_path)
    return md_files


def initialize_known_files(dir_path: str) -> Dict[str, float]:
    """
    Create initial known_files state with existing markdown files.

    :param dir_path: path to directory containing markdown files
    :return: dictionary of known files and their modification times
    """
    # Store file modification times to track changes.
    # This allows efficient detection of updates without reading file contents
    known_files = {}
    for file_path in list_markdown_files(dir_path):
        path = pathlib.Path(file_path)
        # Use modification time as a lightweight way to detect changes.
        # Avoids having to read and hash file contents
        known_files[str(path)] = path.stat().st_mtime
    return known_files


def parse_markdown_files(file_paths: List[str]) -> List[lngchdocstordoc.Document]:
    """
    Parse markdown files into LangChain Documents with metadata.

    :param file_paths: list of paths to markdown files
    :return: list of Document objects with content and metadata
    """
    documents = []
    # Use tqdm to show progress since parsing large files can be slow.
    for file_path in tqdm.tqdm(file_paths):
        # `UnstructuredMarkdownLoader` handles various markdown formats robustly.
        loader = UnstructuredMarkdownLoader(file_path)
        docs = loader.load()
        for doc in docs:
            # Track source file for traceability.
            doc.metadata["source"] = file_path
            # Store modification time to detect changes later.
            doc.metadata["last_modified"] = os.path.getmtime(file_path)
            # Calculate checksum to identify content changes.
            doc.metadata["checksum"] = hashlib.md5(
                doc.page_content.encode()
            ).hexdigest()
        documents.extend(docs)
    # Log success rate to help debug parsing issues.
    _LOG.info("Successfully parsed %d/%d files", len(documents), len(file_paths))
    return documents


def split_documents(
    documents: List[lngchdocstordoc.Document],
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> List[lngchdocstordoc.Document]:
    """
    Split documents into chunks using text splitter.

    :param documents: list of Documents to split
    :param chunk_size: size of each chunk in characters
    :param chunk_overlap: overlap between chunks in characters
    :return: list of chunked Document objects
    """
    text_splitter = langchain.text_splitter.RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap, add_start_index=True
    )
    chunks = text_splitter.split_documents(documents)
    _LOG.info("Split %d documents into %d chunks", len(documents), len(chunks))
    return chunks


def create_vector_store(
    documents: List[lngchdocstordoc.Document],
    embeddings: langchain.embeddings.OpenAIEmbeddings,
) -> FAISS:
    """
    Create FAISS vector store from documents.

    :param documents: list of Document objects
    :param embeddings: embeddings model to use
    :return: FAISS vector store
    """
    vector_store = FAISS.from_documents(documents, embeddings)
    _LOG.info("Created vector store with %d entries", len(documents))
    return vector_store


def build_retriever(vector_store: FAISS, *, search_kwargs: Optional[Dict[str, int]] = None) -> langchain.schema.retriever.BaseRetriever:
    """
    Build retriever from vector store.

    :param vector_store: FAISS vector store
    :param search_kwargs: keyword arguments for retriever
    :return: retriever
    """
    if search_kwargs is None:
        search_kwargs = {"k": 4}
    retriever = vector_store.as_retriever(search_kwargs=search_kwargs)
    _LOG.info("Built retriever with config: %s", search_kwargs)
    return retriever


def watch_folder_for_changes(
    dir_path: str, known_files: Dict[str, float]
) -> Dict[str, List[str]]:
    """
    Monitor directory for file changes.

    :param dir_path: path to directory to monitor
    :param known_files: dictionary of known files and their modification
        times
    :return: dictionary of changed files
    """
    # Get current files in directory.
    current_files = {
        str(p): p.stat().st_mtime for p in pathlib.Path(dir_path).rglob("*.md")
    }
    # Detect changes.
    changes = {
        "new": [],
        "modified": [],
        "deleted": list(known_files.keys() - current_files.keys()),
    }
    for path, mtime in current_files.items():
        if path not in known_files:
            changes["new"].append(path)
        elif mtime > known_files[path]:
            changes["modified"].append(path)
    # Update known files.
    known_files.update(current_files)
    return changes


def update_vector_store(
    vector_store: FAISS,
    new_documents: List[lngchdocstordoc.Document],
    embeddings: langchain.embeddings.OpenAIEmbeddings,
) -> FAISS:
    """
    Update existing vector store with new documents.

    :param vector_store: FAISS vector store
    :param new_documents: list of new Document objects
    :param embeddings: embeddings model to use
    :return: updated FAISS vector store
    """
    if new_documents:
        new_vector_store = FAISS.from_documents(new_documents, embeddings)
        vector_store.merge_from(new_vector_store)
        _LOG.info("Added %d new documents to vector store", len(new_documents))
    return vector_store


def update_vector_store_from_changes(
    config: Dict[str, Any],
    vector_store: FAISS,
    embeddings: langchain.embeddings.OpenAIEmbeddings,
) -> None:
    """
    Update vector store based on file changes in the source directory.

    :param config: Configuration dictionary containing source directory and chunk parameters
    :param known_files: Dictionary tracking known files and modification times
    :param vector_store: FAISS vector store to update
    :param embeddings: Embeddings model to use
    """
    # Monitor the folder for changes and update the vector store.
    known_files = initialize_known_files(config["source_directory"])
    # First check what files have changed by comparing against our known state.
    changes = watch_folder_for_changes(
        dir_path=config["source_directory"], known_files=known_files
    )
    # Only process if we have new or modified files to avoid unnecessary work.
    if changes["new"] or changes["modified"]:
        changed_files = changes["new"] + changes["modified"]
        # Convert markdown to raw documents first so we can validate the content
        # before spending time on chunking and embedding
        raw_new_docs = parse_markdown_files(changed_files)
        if raw_new_docs:
            # Break documents into smaller chunks to improve retrieval accuracy
            # and stay within model context limits
            chunked_new_docs = split_documents(
                documents=raw_new_docs,
                chunk_size=config["parse_data_into_chunks"]["chunk_size"],
                chunk_overlap=config["parse_data_into_chunks"]["chunk_overlap"],
            )
            # Add the new document chunks to our existing vector store
            # This maintains the searchable knowledge base
            update_vector_store(
                vector_store=vector_store,
                new_documents=chunked_new_docs,
                embeddings=embeddings,
            )
            # Log success metrics to track system health
            _LOG.info(
                "Updated vector store with %d new chunks from %d files",
                len(chunked_new_docs),
                len(changed_files),
            )
            _LOG.debug("New/modified files: %s", changed_files)
        else:
            # Alert if files changed but we couldn't extract valid content
            _LOG.warning(
                "No valid documents found in %d changed files", len(changed_files)
            )
    # Currently we don't handle deletions since it would require rebuilding.
    # indexes Flag this limitation to operators through logs.
    if changes["deleted"]:
        _LOG.warning(
            "Deletion handling not implemented. Found %d deleted files: %s",
            len(changes["deleted"]),
            changes["deleted"],
        )
