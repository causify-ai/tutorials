# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.6
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Tutorial For Langchain
#
# The notebook shows how to use langchain API with an example. In this example we will be building chatbot for the internal documentation using lancgchain.
#
# Refernces: 
#  - Official docs : https://python.langchain.com/docs/introduction/

# ## Imports

# %load_ext autoreload
# %autoreload 2
# %matplotlib inline

# +
import os
import glob
import logging

import langchain_openai as langOpenAI
import langchain.document_loaders as docloader
import langchain.docstore.document as docstore
import langchain.text_splitter as txtsplitter
import langchain.embeddings as lang_embeddings
import langchain.vectorstores as vectorstores
import langchain.chains as chains
import langchain.chat_models as chatmodels

from typing import List

import helpers.hsystem as hsystem
import helpers.hprint as hprint
import helpers.hdbg as hdbg
import helpers.hpandas as hpanda



# +
hdbg.init_logger(verbosity=logging.INFO)

_LOG = logging.getLogger(__name__)
# -

# ### Define the GPT Model to use.

# +
os.environ["OPENAI_API_KEY"] = "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"

chat_model = langOpenAI.ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)


# -

def parse_markdown_files(file_paths) -> List[docstore.Document]:
    """
    Parse all the markdown files into Documents.

    :param file_paths: list of md file_paths
    """
    documents = []
    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Create a Document object for each file
        documents.append(docstore.Document(page_content=content, metadata={"source": file_path}))
    return documents


def list_markdown_files(directory:str) -> List[str]:
    return list(glob.glob(f"{directory}/*.md"))


# ### RecursiveCharacterTextSplitter 
# Utility function in LangChain  for splitting large chunks of text into smaller more manageable pieces while ensuring minimal overlap or fragmentation of meaningful content.
#

# +
# Directory containing Markdown files
directory = "../../docs"

# List Markdown files
markdown_files = list_markdown_files(directory)

# Parse Markdown files into LangChain documents
documents = parse_markdown_files(markdown_files)

# Split long documents into smaller chunks
text_splitter = txtsplitter.RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
split_documents = text_splitter.split_documents(documents)

# Print sample chunked documents
for doc in split_documents[:5]:
    _LOG.info("Source: %s", {doc.metadata['source']})
    _LOG.info("Content: %s", {doc.page_content})
# -

# ### VECTOR STORES
#
# #### FAISS (Facebook AI Similarity Search) 
# It is a library designed for efficient similarity search and clustering of dense vectors. In LangChain, FAISS is commonly used as a vector store to store and retrieve embeddings, which are vector representations of text or other data.
#

# +
# Initialize embeddings
embeddings = lang_embeddings.OpenAIEmbeddings()

# Embed and store split_documents
vector_store = vectorstores.FAISS.from_documents(split_documents, embeddings)

retriever = vector_store.as_retriever()
# -

# Create the QA chain
qa_chain = chains.RetrievalQA.from_chain_type(
    llm=chat_model,
    retriever=retriever,
    return_source_documents=True
)


# +
# User's question
query = "What are the guidelines on creating new project"

# Get the answer and source documents
result = qa_chain({"query": query})

# Print the answer
_LOG.info("Answer: %s", result['result'])

# Print the source file references
_LOG.info("\nSource Documents:")
for doc in result['source_documents']:
    _LOG.info("File: %s", {doc.metadata['source']})
    _LOG.info("Excerpt: %s", {doc.page_content[:200]})


# -

def get_vectors_by_document_name(vector_store: vectorstores.FAISS, document_name: str) -> List:
    """
    Retrieve vectors from a FAISS vector store based on the document name.

    :param vector_store: FAISS vector store object that supports similarity search.
    :param document_name:  name of the document used as a filter in the metadata.

    :return: list of results from the FAISS vector store that match the given document name.
    """
    # Query using the metadata field source
    results = vector_store.similarity_search(
        # Pass an empty query or a dummy vector if supported
        query="",
        # Retrieve all matching documents
        k=None,
        # Filter by the document name
        filter={"source": document_name} 
    )
    return results



# +
# Example usage
document_name = "all.how_write_tutorials.how_to_guide.md"
results = get_vectors_by_document_name(vector_store, document_name)

# Print results
for doc in results:
    _LOG.info("File: %s", {doc.metadata['source']})
    _LOG.info("Content: %s", {doc.page_content[:200]})
# -

# ### Demo to create a documentation QA bot but the docs can be updated or deleted.

# Initialize some state.
vector_store = None
folder = "../docs"
filename_to_md5sum = {}

# +
from typing import List
from langchain.schema import Document

def parse_markdown_files(file_paths: List[str]) -> List[Document]:
    """
    Parse and structure Markdown files into LangChain Document objects.

    :param file_paths: list of file paths to the Markdown files

    :return: list of Document objects, where each document contains the content
                        of a Markdown file and metadata with the file's source path.
    """
    documents = []
    filename_to_md5sum = {}
    for file_path in file_paths:
        # Read the content of the Markdown file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()       
        # Compute the MD5 checksum of the file
        md5sum, _ = hsystem.system_to_string(f"md5sum {file_path}")[1].split()
        filename_to_md5sum[file_path] = md5sum 
        # Create a Document object for each file
        documents.append(Document(page_content=content, metadata={"source": file_path}))
    
    return documents



# -

def create_vector_store_from_markdown_files(folder):
    # List Markdown files
    markdown_files = list_markdown_files(directory)
    # Parse Markdown files into LangChain documents
    documents = parse_markdown_files(markdown_files)
    # Split long documents into smaller chunks
    text_splitter = txtsplitter.RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_documents = text_splitter.split_documents(documents)
    # Create embeddings for all documents.
    vector_store = vectorstores.Chroma.from_documents(split_documents, embeddings)
    return vector_store


def get_changes_in_documents_folder(folder):
    # List Markdown files
    markdown_files = list_markdown_files(folder)
    changes = {}
    changes["modified"] = []
    for file_path in markdown_files:
        md5sum, _ = hsystem.system_to_string(f"md5sum {file_path}")[1].split()
        if file_path not in filename_to_md5sum or filename_to_md5sum[file_path] == md5sum:
            print(f"Found a new / modified file {file_path}")
            changes["modified"].append(file_path)
    return changes


def update_files_in_vector_store(vector_store, files):
    if len(files) == 0:
        print("No new files found")
        return
    ids_to_delete = []
    for file in files:
        for doc in vector_store:
            if doc.metadata.get('source') == file:
                ids_to_delete.append(doc.id)
    vector_store.delete(ids_to_delete)
    documents = parse_markdown_files(files)
    # Split long documents into smaller chunks
    text_splitter = txtsplitter.RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_documents = text_splitter.split_documents(documents)
    texts = [doc.page_content for doc in split_documents]
    embeddings_list = embeddings.embed_documents(texts)  # Compute embeddings for multiple documents
    # Add documents to vector store with computed embeddings
    vector_store.add_documents(
        documents=split_documents,
        embeddings=embeddings_list
    )
    return vector_store


query = "What are the goals for tutorial project?"

if vector_store:
    changes = get_changes_in_documents_folder(folder)
    vector_store = update_files_in_vector_store(vector_store, changes["modified"])
else:
    vector_store = create_vector_store_from_markdown_files(folder)


# Create the QA chain
qa_chain = chains.RetrievalQA.from_chain_type(
    llm=chat_model,
    retriever=retriever,
    return_source_documents=True
)

# +
# Get the answer and source documents
result = qa_chain({"query": query})

# Print the answer
_LOG.info("Answer: %s", result['result'])

# Print the source file references
_LOG.info("\nSource Documents:")
for doc in result['source_documents']:
    _LOG.info("File: %s", {doc.metadata['source']})
    _LOG.info("Excerpt: %s", {doc.page_content[:200]})
# -




