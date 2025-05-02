# utils/build_index.py

import os
import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
from utils.processing import extract_text, chunk_text

def build_faiss_index(file_paths, index_path="index/faiss_index.bin", metadata_path="index/metadata.pkl", progress_callback=None):
    model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
    
    # Check if we have an existing index and metadata
    existing_index = None
    existing_metadata = []
    indexed_files = set()
    
    if os.path.exists(index_path) and os.path.exists(metadata_path):
        try:
            # Load existing index and metadata
            existing_index = faiss.read_index(index_path)
            with open(metadata_path, "rb") as f:
                existing_metadata = pickle.load(f)
            
            # Get set of already indexed files
            indexed_files = set(m["path"] for m in existing_metadata)
            print(f"Found existing index with {len(indexed_files)} files.")
        except Exception as e:
            print(f"Error loading existing index: {e}")
            # If there's an error, we'll rebuild the index from scratch
            existing_index = None
            existing_metadata = []
            indexed_files = set()
    
    # Filter out files that are already indexed
    new_files = [path for path in file_paths if path not in indexed_files]
    
    if not new_files:
        print("No new files to index.")
        if progress_callback:
            progress_callback(1.0, "No new files to index")  # 100% complete
        return
    
    print(f"Adding {len(new_files)} new files to the index.")
    
    embeddings = []
    new_metadata = []
    
    # Initialize progress
    total_files = len(new_files)
    if progress_callback:
        progress_callback(0.0, f"Starting to index {total_files} files")
    
    # Process only new files
    for i, path in enumerate(new_files):
        try:
            # Update progress
            if progress_callback:
                progress_pct = (i / total_files)
                file_name = os.path.basename(path)
                progress_callback(progress_pct, f"Processing {file_name} ({i+1}/{total_files})")
            
            text = extract_text(path)
            chunks = chunk_text(text)
            emb = model.encode(chunks)
            embeddings.append(emb)

            new_metadata.append({
                "path": path,
                "folder": os.path.dirname(path),
                "snippet": chunks[:300],
            })
        except Exception as e:
            print(f"⚠️ Skipped {path}: {e}")
            
        # Update progress after each file
        if progress_callback:
            progress_pct = ((i+1) / total_files) * 0.9  # Reserve 10% for final steps
            progress_callback(progress_pct, f"Processed {i+1}/{total_files} files")

    if not embeddings:
        print("⚠️ No new embeddings to add to index.")
        if progress_callback:
            progress_callback(1.0, "Completed - no new content to index")
        return
    
    # Update progress for embedding matrix preparation
    if progress_callback:
        progress_callback(0.9, "Preparing embeddings...")
    
    # Prepare embedding matrix for new files
    new_embedding_matrix = np.vstack(embeddings)
    
    # Create or update index
    os.makedirs(os.path.dirname(index_path), exist_ok=True)
    
    # Update progress for saving index
    if progress_callback:
        progress_callback(0.95, "Saving index to disk...")
    
    if existing_index is not None:
        # Add new embeddings to existing index
        existing_index.add(new_embedding_matrix)
        combined_metadata = existing_metadata + new_metadata
        
        # Save updated index and metadata
        faiss.write_index(existing_index, index_path)
        with open(metadata_path, "wb") as f:
            pickle.dump(combined_metadata, f)
            
        print(f"✅ Added {len(new_metadata)} new chunks from {len(new_files)} files to existing index")
        print(f"✅ Index now contains {len(combined_metadata)} total chunks from {len(set(m['path'] for m in combined_metadata))} files")
    else:
        # Create new index from scratch
        dim = new_embedding_matrix.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(new_embedding_matrix)
        
        # Save new index and metadata
        faiss.write_index(index, index_path)

        with open(metadata_path, "wb") as f:
            pickle.dump(new_metadata, f)
            
        print(f"✅ Created new index with {len(new_metadata)} chunks from {len(new_files)} files")
    
    # Indexing complete
    if progress_callback:
        progress_callback(1.0, "Indexing complete!")