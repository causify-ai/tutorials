"""
Import as:

import dify.weaviate_docs as dweadocs
"""

import os

import requests
import weaviate
import langchain.text_splitter as lts
import langchain_community.document_loaders as ldl
import weaviate.classes.config as wcc
RecursiveCharacterTextSplitter = lts.RecursiveCharacterTextSplitter
UnstructuredMarkdownLoader = ldl.UnstructuredMarkdownLoader
Configure = wcc.Configure
DataType = wcc.DataType
Property = wcc.Property

PROJECT_ROOT = os.environ.get("PWD")
if not PROJECT_ROOT:
    raise RuntimeError(
        "PWD env var not set — please set PWD to your project root"
    )


DOCS_DIR = os.path.join(PROJECT_ROOT, "docs")
COLLECTION_NAME = "Documents"
ALLOWED_EXTENSIONS = [".md"]
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
BATCH_SIZE = 100
OLLAMA_EMBED_URL = "http://localhost:11434/api/embed"
OLLAMA_MODEL = "nomic-embed-text"

# Connect to Weaviate
client = weaviate.connect_to_local()

# Create collection with no internal vectorizer
if COLLECTION_NAME not in client.collections.list_all():
    client.collections.create(
        name=COLLECTION_NAME,
        vectorizer_config=Configure.Vectorizer.none(),
        properties=[
            Property(name="text", data_type=DataType.TEXT),
            Property(name="filename", data_type=DataType.TEXT),
            Property(name="filepath", data_type=DataType.TEXT),
        ],
    )

collection = client.collections.get(COLLECTION_NAME)
splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
)

with collection.batch.fixed_size(BATCH_SIZE) as batch:
    for root, _, files in os.walk(DOCS_DIR):
        for filename in files:
            if not any(filename.endswith(ext) for ext in ALLOWED_EXTENSIONS):
                continue
            filepath = os.path.join(root, filename)

            try:
                loader = UnstructuredMarkdownLoader(filepath)
                docs = loader.load()
                chunks = splitter.split_documents(docs)

                for chunk in chunks:
                    text = chunk.page_content.strip()

                    # Call Ollama embed API
                    response = requests.post(
                        OLLAMA_EMBED_URL,
                        headers={"Content-Type": "application/json"},
                        json={"model": OLLAMA_MODEL, "input": text},
                    )
                    if response.status_code != 200:
                        raise RuntimeError(
                            f"Ollama error {response.status_code}: {response.text}"
                        )

                    embedding_list = response.json().get("embeddings")
                    if not embedding_list or not isinstance(
                        embedding_list[0], list
                    ):
                        raise ValueError(
                            "Embedding format unexpected or missing."
                        )
                    embedding = embedding_list[0]
                    batch.add_object(
                        properties={
                            "text": text,
                            "filename": filename,
                            "filepath": os.path.relpath(filepath, DOCS_DIR),
                        },
                        vector=embedding,
                    )
                print(f"Uploaded: {filename}")
            except Exception as e:
                print(f"Failed: {filename}, error: {e}")

client.close()
print("All markdown files uploaded using `nomic-embed-text` via Ollama.")
