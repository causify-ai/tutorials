# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.7
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Building a Documentation Chatbot with LangChain
#
# This script demonstrates how to build an intelligent chatbot that queries documentation using LangChain.
# The chatbot can:
# - Parse and preprocess Markdown files.
# - Embed document content for efficient similarity-based retrieval.
# - Answer detailed, context-aware queries from users.

# %%
# #!sudo /venv/bin/pip install langchain --quiet
# #!sudo /venv/bin/pip install -U langchain-community --quiet
# #!sudo /venv/bin/pip install -U langchain-openai --quiet
# #!sudo /venv/bin/pip install -U langchain-core --quiet
# #!sudo /venv/bin/pip install -U langchainhub --quiet
# #!sudo /venv/bin/pip install -U unstructured python-magic pandoc markdown faiss-cpu --quiet
# #!sudo /venv/bin/pip install --quiet chromadb

# %%
import hashlib
import logging
import os
import pathlib
from typing import Dict, List

import helpers.hdbg as hdbg
import langchain
import langchain.chains
import langchain.docstore.document as lngchdocstordoc
import langchain.embeddings
import langchain.hub
import langchain.text_splitter
import langchain_openai
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_community.vectorstores import FAISS

# %%
hdbg.init_logger(verbosity=logging.INFO)

_LOG = logging.getLogger(__name__)

# %% [markdown]
# ## Define Config

# %%
config = {
    "open_ai_api_key": "",
    # Define language model arguments.
    "language_model": {
        # Define your model here.
        "model": "gpt-4o-mini",
        "temperature": 0,
    },
    # Define input directory path containing documents.
    "source_directory": "../../helpers_root/docs",
    "parse_data_into_chunks": {
        "chunk_size": 500,
        "chunk_overlap": 50,
    },
}

# %% [markdown]
# ## Setting Up
#
# We'll begin by importing the required libraries and configuring the environment. The chatbot will use:
# - OpenAI's GPT-4o-mini as the core language model.
# - FAISS for fast document retrieval.
# - LangChain utilities for document parsing, text splitting, and chaining.

# %%
# Set the OpenAI API key.
os.environ["OPENAI_API_KEY"] = config["open_ai_api_key"]
# Initialize the chat model.
chat_model = langchain_openai.ChatOpenAI(**config["language_model"])


# %% [markdown]
# ## Define Functions


# %%
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
    known_files = {}
    for file_path in list_markdown_files(dir_path):
        path = pathlib.Path(file_path)
        known_files[str(path)] = path.stat().st_mtime
    return known_files


def parse_markdown_files(file_paths: List[str]) -> List[lngchdocstordoc.Document]:
    """
    Parse markdown files into LangChain Documents with metadata.

    :param file_paths: list of paths to markdown files
    :return: list of Document objects with content and metadata
    """
    documents = []
    for file_path in file_paths:
        try:
            loader = UnstructuredMarkdownLoader(file_path)
            docs = loader.load()
            for doc in docs:
                doc.metadata["source"] = file_path
                doc.metadata["last_modified"] = os.path.getmtime(file_path)
                doc.metadata["checksum"] = hashlib.md5(
                    doc.page_content.encode()
                ).hexdigest()
            documents.extend(docs)
        except Exception as e:
            _LOG.error("Error loading %s: %s", file_path, str(e))
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


def build_retriever(vector_store: FAISS, search_kwargs: Dict = {"k": 4}):
    """
    Build retriever from vector store.

    :param vector_store: FAISS vector store
    :param search_kwargs: keyword arguments for retriever
    :return: retriever
    """
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


# %% [markdown]
# ## Parse and Preprocess Documentation
#
# Markdown files serve as the primary data source for this chatbot.
# We'll parse the files into LangChain `Document` objects and split them into manageable chunks to ensure efficient retrieval.

# %%
# Initialize with documents
md_files = list_markdown_files(config["source_directory"])
raw_documents = parse_markdown_files(md_files)
chunked_documents = split_documents(
    raw_documents,
    chunk_size=config["parse_data_into_chunks"]["chunk_size"],
    chunk_overlap=config["parse_data_into_chunks"]["chunk_overlap"],
)

# %% [markdown]
# ## Create a FAISS Vector Store
#
# To enable fast document retrieval, we'll embed the document chunks using OpenAI's embeddings and store them in a FAISS vector store.

# %%
# Initialize OpenAI embeddings.
embeddings = langchain.embeddings.OpenAIEmbeddings()
# Create a FAISS vector store.
vector_store = create_vector_store(chunked_documents, embeddings)
_LOG.info("FAISS vector store created with %d documents.", len(chunked_documents))

# %% [markdown]
# ## Build a QA Chain
#
# The `RetrievalQA` chain combines document retrieval with OpenAI's GPT-3.5 for question answering.
# It retrieves the most relevant document chunks and uses them as context to generate answers.

# %%
# Build the retriever from the vector store
retriever = build_retriever(vector_store)

# Create the RetrievalQA chain
qa_chain = langchain.chains.RetrievalQA.from_chain_type(
    llm=chat_model, retriever=retriever, return_source_documents=True
)

_LOG.info("RetrievalQA chain initialized.")

# %% [markdown]
# ## Step 5: Query the Chatbot
#
# Let's interact with the chatbot! We'll ask it questions based on the documentation.
# The chatbot will retrieve relevant chunks and generate context-aware responses.

# %%
# Define a user query.
query = "What are the guidelines for setting up a new project?"

# Query the chatbot.
response = qa_chain({"query": query})

# Display the answer and source documents.
print(f"Answer:\n{response['result']}\n")
print("Source Documents:")
for doc in response["source_documents"]:
    print(f"- Source: {doc.metadata['source']}")
    print(f"  Excerpt: {doc.page_content[:200]}")

# %% [markdown]
# ## Step 6: Dynamic Updates
#
# What if the documentation changes? We'll handle this by monitoring the folder for new or modified files.
# The vector store will be updated dynamically to ensure the chatbot stays up-to-date.

# %%
# Monitor the folder for changes and update the vector store.
known_files = initialize_known_files(config["source_directory"])

# Detect changes using our custom watcher.
changes = watch_folder_for_changes(
    dir_path=config["source_directory"], known_files=known_files
)

if changes["new"] or changes["modified"]:
    # Process changed files.
    changed_files = changes["new"] + changes["modified"]
    # Parse markdown files using our custom parser.
    raw_new_docs = parse_markdown_files(changed_files)
    if raw_new_docs:
        # Split into chunks using configured parameters.
        chunked_new_docs = split_documents(
            documents=raw_new_docs,
            chunk_size=config["parse_data_into_chunks"]["chunk_size"],
            chunk_overlap=config["parse_data_into_chunks"]["chunk_overlap"],
        )
        # Update vector store with new chunks.
        update_vector_store(
            vector_store=vector_store,
            new_documents=chunked_new_docs,
            embeddings=embeddings,
        )
        _LOG.info(
            "Updated vector store with %d new chunks from %d files",
            len(chunked_new_docs),
            len(changed_files),
        )
        _LOG.debug("New/modified files: %s", changed_files)
    else:
        _LOG.warning(
            "No valid documents found in %d changed files", len(changed_files)
        )
# Handle deleted files if needed.
if changes["deleted"]:
    _LOG.warning(
        "Deletion handling not implemented. Found %d deleted files: %s",
        len(changes["deleted"]),
        changes["deleted"],
    )

# %% [markdown]
# ## Step 7: Enhancements - Personalization
#
# We can extend the chatbot to include personalized responses:
# - Filter documents by metadata (e.g., tags, categories).
# - Customize responses based on user preferences.
#
# For example, users can ask for specific sections of the documentation or request summaries tailored to their needs.

# %%
# Example query with personalized intent.
personalized_query = "Show me onboarding guidelines for new employees."

# Query the chatbot.
personalized_response = qa_chain({"query": personalized_query})

# Display the personalized response.
print(f"Answer:\n{personalized_response['result']}\n")
print("Source Documents:")
for doc in personalized_response["source_documents"]:
    print(f"- Source: {doc.metadata['source']}")
    print(f"  Excerpt: {doc.page_content[:200]}")

# %% [markdown]
# ## Summary
#
# In this script, we:
# 1. Parsed and processed Markdown documentation.
# 2. Embedded document chunks into a FAISS vector store for efficient retrieval.
# 3. Built a RetrievalQA chain for context-aware question answering.
# 4. Enabled dynamic updates to handle changing documentation.
# 5. Enhanced the chatbot with personalized query handling.
#
# This showcases how LangChain can be used to build intelligent, flexible chatbots tailored for specific tasks.
