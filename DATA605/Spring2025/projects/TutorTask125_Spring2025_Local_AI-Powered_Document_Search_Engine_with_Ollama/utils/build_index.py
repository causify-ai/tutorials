# utils/build_index.py

import os
import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
from utils.processing import extract_text, chunk_text
import concurrent.futures
import threading

# Thread-safe progress tracking
class ProgressTracker:
    def __init__(self, total_files, callback=None):
        self.lock = threading.Lock()
        self.processed_count = 0
        self.total_files = total_files
        self.callback = callback
    
    def update(self, file_name=None):
        with self.lock:
            self.processed_count += 1
            if self.callback:
                progress_pct = (self.processed_count / self.total_files) * 0.9  # Reserve 10% for final steps
                self.callback(progress_pct, f"Processed {self.processed_count}/{self.total_files} files{f' - {file_name}' if file_name else ''}")
            return self.processed_count

def process_file(file_path, model, progress_tracker=None):
    """Process a single file and return its embeddings and metadata"""
    try:
        text = extract_text(file_path)
        chunks = chunk_text(text)
        
        file_embeddings = []
        file_metadata = []
        
        for idx, chunk in enumerate(chunks):
            if not chunk.strip():
                continue
                
            emb = model.encode(chunk)
            file_embeddings.append(emb)
            
            file_metadata.append({
                "path": file_path,
                "folder": os.path.dirname(file_path),
                "snippet": chunk[:300],
                "chunk_id": idx,
                "filetype": os.path.splitext(file_path)[1][1:]
            })
        
        # Update progress
        if progress_tracker:
            progress_tracker.update(os.path.basename(file_path))
            
        return file_embeddings, file_metadata
        
    except Exception as e:
        print(f"⚠️ Skipped {file_path}: {e}")
        if progress_tracker:
            progress_tracker.update()
        return [], []

def build_faiss_index(file_paths, index_path="index/faiss_index.bin", metadata_path="index/metadata.pkl", progress_callback=None, max_workers=None):
    # If max_workers is None, concurrent.futures will determine an appropriate value based on CPU count
    if max_workers is None:
        max_workers = min(32, os.cpu_count() + 4)  # Default ThreadPoolExecutor formula
    
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
    
    print(f"Adding {len(new_files)} new files to the index using {max_workers} workers.")
    
    # Initialize progress
    total_files = len(new_files)
    if progress_callback:
        progress_callback(0.0, f"Starting to index {total_files} files using {max_workers} threads")
    
    # Create progress tracker
    progress_tracker = ProgressTracker(total_files, progress_callback)
    
    all_embeddings = []
    all_metadata = []
    
    # Process files in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all file processing tasks
        future_to_file = {executor.submit(process_file, file_path, model, progress_tracker): file_path 
                          for file_path in new_files}
        
        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                file_embeddings, file_metadata = future.result()
                all_embeddings.extend(file_embeddings)
                all_metadata.extend(file_metadata)
            except Exception as e:
                print(f"⚠️ Error processing {file_path}: {e}")

    if not all_embeddings:
        print("⚠️ No new embeddings to add to index.")
        if progress_callback:
            progress_callback(1.0, "Completed - no new content to index")
        return
    
    # Update progress for embedding matrix preparation
    if progress_callback:
        progress_callback(0.9, "Preparing embeddings...")
    
    # Prepare embedding matrix for new files
    new_embedding_matrix = np.vstack(all_embeddings)
    
    # Create or update index
    os.makedirs(os.path.dirname(index_path), exist_ok=True)
    
    # Update progress for saving index
    if progress_callback:
        progress_callback(0.95, "Saving index to disk...")
    
    if existing_index is not None:
        # Add new embeddings to existing index
        existing_index.add(new_embedding_matrix)
        combined_metadata = existing_metadata + all_metadata
        
        # Save updated index and metadata
        faiss.write_index(existing_index, index_path)
        with open(metadata_path, "wb") as f:
            pickle.dump(combined_metadata, f)
            
        print(f"✅ Added {len(all_metadata)} new chunks from {len(new_files)} files to existing index")
        print(f"✅ Index now contains {len(combined_metadata)} total chunks from {len(set(m['path'] for m in combined_metadata))} files")
    else:
        # Create new index from scratch
        dim = new_embedding_matrix.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(new_embedding_matrix)
        
        # Save new index and metadata
        faiss.write_index(index, index_path)
        with open(metadata_path, "wb") as f:
            pickle.dump(all_metadata, f)
            
        print(f"✅ Created new index with {len(all_metadata)} chunks from {len(new_files)} files")
    
    # Indexing complete
    if progress_callback:
        progress_callback(1.0, "Indexing complete!")
