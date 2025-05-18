# utils/search.py
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

def load_index_and_metadata(index_path="index/faiss_index.bin", metadata_path="index/metadata.pkl"):
    index = faiss.read_index(index_path)
    with open(metadata_path, "rb") as f:
        metadata = pickle.load(f)
    return index, metadata

def search_documents(query, model, index, metadata, k=5):
    query_vector = model.encode([query])
    D, I = index.search(query_vector, k)

    results = []
    for i, idx in enumerate(I[0]):
        result = metadata[idx]
        result['score'] = 1 / (1 + D[0][i])  # Convert L2 distance to similarity-ish
        results.append(result)

    return results


