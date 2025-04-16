# utils/build_index.py

import os
import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
from utils.processing import extract_text, chunk_text

def build_faiss_index(file_paths, index_path="index/faiss_index.bin", metadata_path="index/metadata.pkl"):
    model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

    embeddings = []
    metadata = []

    for path in file_paths:
        try:
            text = extract_text(path)
            chunks = chunk_text(text)

            for idx, chunk in enumerate(chunks):
                if not chunk.strip():
                    continue

                emb = model.encode(chunk)
                embeddings.append(emb)

                metadata.append({
                    "path": path,
                    "folder": os.path.dirname(path),
                    "snippet": chunk[:300],
                    "chunk_id": idx,
                    "filetype": os.path.splitext(path)[1][1:]
                })

        except Exception as e:
            print(f"⚠️ Skipped {path}: {e}")

    if embeddings:
        embedding_matrix = np.vstack(embeddings)
        dim = embedding_matrix.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(embedding_matrix)

        os.makedirs(os.path.dirname(index_path), exist_ok=True)
        faiss.write_index(index, index_path)

        with open(metadata_path, "wb") as f:
            pickle.dump(metadata, f)

        print(f"✅ Indexed {len(metadata)} chunks from {len(set(m['path'] for m in metadata))} files")
    else:
        print("⚠️ No embeddings to index.")
