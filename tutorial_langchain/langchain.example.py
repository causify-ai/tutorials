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

# !sudo /venv/bin/pip install -U --quiet unstructured markdown

# %%
# %load_ext autoreload
# %autoreload 2

# %%
import logging

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
import langchain_utils as ut

# %%
hdbg.init_logger(verbosity=logging.INFO)

_LOG = logging.getLogger(__name__)

# %% [markdown]
# ## Define Config

# %%
config = {
    # Define language model arguments.
    "language_model": {
        # Define your model here.
        "model": "gpt-4o-mini",
        "temperature": 0,
    },
    # Define input directory path containing documents.
    "source_directory": "docs",
    "parse_data_into_chunks": {
        "chunk_size": 500,
        "chunk_overlap": 50,
    },
}

hdbg.dassert_dir_exists(config["source_directory"])

# %% [markdown]
# ## Setting Up
#
# We'll begin by importing the required libraries and configuring the environment. The chatbot will use:
# - OpenAI's GPT-4o-mini as the core language model.
# - FAISS for fast document retrieval.
# - LangChain utilities for document parsing, text splitting, and chaining.

# %%
# Set the OpenAI API key.
#os.environ["OPENAI_API_KEY"] = config["open_ai_api_key"]
# Initialize the chat model.
print(config["language_model"])
chat_model = langchain_openai.ChatOpenAI(**config["language_model"])


# %% [markdown]
# ## Define Functions


# %% [markdown]
# ## Parse and Preprocess Documentation
#
# Markdown files serve as the primary data source for this chatbot.
# We'll parse the files into LangChain `Document` objects and split them into manageable chunks to ensure efficient retrieval.

# %%
# Initialize with documents
md_files = ut.list_markdown_files(config["source_directory"])
raw_documents = ut.parse_markdown_files(md_files)
chunked_documents = ut.split_documents(
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
vector_store = ut.create_vector_store(chunked_documents, embeddings)
_LOG.info("FAISS vector store created with %d documents.", len(chunked_documents))

# %% [markdown]
# ## Build a QA Chain
#
# The `RetrievalQA` chain combines document retrieval with OpenAI's GPT-3.5 for question answering.
# It retrieves the most relevant document chunks and uses them as context to generate answers.

# %%
# Build the retriever from the vector store
retriever = ut.build_retriever(vector_store)

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
ut.update_vector_store_from_changes(
    config,
    vector_store,
    embeddings,
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
