import streamlit as st
from utils.file_scanner import scan_files
from utils.build_index import build_faiss_index
from utils.processing import extract_text  # Import extract_text function
import os
import subprocess

# Initialize session state variables if they don't exist
if 'search_results' not in st.session_state:
    st.session_state['search_results'] = []
if 'preview_document' not in st.session_state:
    st.session_state['preview_document'] = None
if 'indexing_complete' not in st.session_state:
    st.session_state['indexing_complete'] = False
if 'indexed_files_count' not in st.session_state:
    st.session_state['indexed_files_count'] = 0
if 'indexing_progress' not in st.session_state:
    st.session_state['indexing_progress'] = 0
if 'indexing_message' not in st.session_state:
    st.session_state['indexing_message'] = ""
if 'index_version' not in st.session_state:
    st.session_state['index_version'] = 1

st.title("📁 Document Search Engine")

st.sidebar.title("📁 Indexing Configuration")
user_path = st.sidebar.text_input("Enter the directory or drive to index:", "C:/Users/YOUR_USERNAME/")

# Step 1: Scan files
if st.sidebar.button("🔍 Scan Files"):
    with st.spinner("Scanning for documents..."):
        files = scan_files(user_path)
        st.session_state['found_files'] = files

# Step 2: Show results if available
if 'found_files' in st.session_state:
    found_files = st.session_state['found_files']

    if found_files:
        st.success(f"Found {len(found_files)} document(s).")

        with st.expander("📄 View File List", expanded=False):
            for file in found_files:
                st.markdown(f"- `{file}`")

        # Always show indexing options, but with different messaging based on state
        if st.session_state['indexing_complete']:
            total_files = len(found_files)
            indexed_files = st.session_state['indexed_files_count']
            
            if indexed_files < total_files:
                st.info(f"There are {total_files - indexed_files} new files that can be added to your existing index.")
                if st.button("🔄 Update Index with New Files"):
                    # Create a placeholder for the progress bar
                    progress_placeholder = st.empty()
                    progress_bar = progress_placeholder.progress(0)
                    
                    # Create a placeholder for progress message
                    message_placeholder = st.empty()
                    message_placeholder.text("Starting indexing...")
                    
                    # Progress callback function
                    def update_progress(progress, message):
                        progress_bar.progress(progress)
                        message_placeholder.text(message)
                        st.session_state['indexing_progress'] = progress
                        st.session_state['indexing_message'] = message
                    
                    # Call build_faiss_index with the progress callback and max_workers
                    build_faiss_index(found_files, progress_callback=update_progress)
                    st.session_state['indexed_files_count'] = total_files
                    
                    # Increment index version to invalidate cache
                    st.session_state['index_version'] += 1
                    
                    # Keep the final progress state
                    progress_bar.progress(1.0)
                    message_placeholder.text("✅ Indexing complete!")
                    
                    st.success(f"✅ Index updated with new files! Total files indexed: {total_files}")
                    st.balloons()
            else:
                st.success(f"✅ All {total_files} files are already indexed!")
                
                # Option to rebuild index from scratch
                if st.button("🔄 Rebuild Index from Scratch"):
                    # Delete existing index files
                    import shutil
                    try:
                        shutil.rmtree('index', ignore_errors=True)
                        st.session_state['indexing_complete'] = False
                        st.session_state['indexed_files_count'] = 0
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error clearing index: {str(e)}")
        else:
            # First-time indexing
            confirm = st.checkbox("✅ Confirm to proceed with indexing")
            if confirm:
                if st.button("🚀 Build Index"):
                    # Create a placeholder for the progress bar
                    progress_placeholder = st.empty()
                    progress_bar = progress_placeholder.progress(0)
                    
                    # Create a placeholder for progress message
                    message_placeholder = st.empty()
                    message_placeholder.text("Starting indexing...")
                    
                    # Progress callback function
                    def update_progress(progress, message):
                        progress_bar.progress(progress)
                        message_placeholder.text(message)
                        st.session_state['indexing_progress'] = progress
                        st.session_state['indexing_message'] = message
                    
                    # Call build_faiss_index with the progress callback and max_workers
                    build_faiss_index(found_files, progress_callback=update_progress)
                    
                    # Increment index version to invalidate cache
                    st.session_state['index_version'] += 1
                    
                    # Keep the final progress state
                    progress_bar.progress(1.0)
                    message_placeholder.text("✅ Indexing complete!")
                    
                    # Set indexing complete flag
                    st.session_state['indexing_complete'] = True
                    st.session_state['indexed_files_count'] = len(found_files)
                    st.success(f"✅ Index built successfully! Indexed {len(found_files)} files.")
                    st.balloons()
    else:
        st.warning("No supported documents found in the selected path.")

from utils.search import load_index_and_metadata, search_documents
from sentence_transformers import SentenceTransformer
from utils.ollama_client import chat_with_ollama


 # Load model + index + metadata once
@st.cache_resource
def load_search_components(_index_version=None):
    """
    Load the search components. The _index_version parameter ensures the cache is invalidated
    when the index is updated, even though it's not used in the function.
    """
    model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
    index, metadata = load_index_and_metadata()
    return model, index, metadata

# Section: Search
st.markdown("---")
st.header("🔍 Search Your Documents")

# Function to handle document preview
def preview_document(doc_path, index):
    st.session_state['preview_document'] = {'path': doc_path, 'index': index}

search_button = False
query = st.text_input("Enter your question or keyword:")
if query and st.button("🔍 Search"):
    search_button = True

# Only run the search if the search button is clicked
if search_button:
    with st.spinner("Refining query using Ollama..."):
        refined_query = chat_with_ollama(
            f"""
            You are a helpful assistant designed to improve search queries for document retrieval.

            Your task is to rewrite the following user query to make it more descriptive and specific, using just a single line. Do not answer the query or provide examples.

            ONLY return the rewritten query — no explanations, no suggestions, and no lists.

            Query: "{query}"

            Rewritten Query:
            """
            )
        refined_query = refined_query.split('\n')[0].strip()
        st.info(f"🔁 Refined Query: **{refined_query}**")
        
        with st.spinner("Searching..."):
            # Pass the index_version to invalidate cache when needed
            model, index, metadata = load_search_components(_index_version=st.session_state['index_version'])
            results = search_documents(refined_query, model, index, metadata)
            st.session_state['search_results'] = results

# Always display results if they exist in session state
if st.session_state['search_results']:
    st.subheader("Top Results:")
    for i, r in enumerate(st.session_state['search_results']):
        with st.expander(f"**Result {i+1}** - Score: {r['score']:.4f} - {os.path.basename(r['path'])}", expanded=False):
            st.markdown(f"**Snippet**: {r['snippet']}")
            st.markdown(f"📄 **File**: `{r['path']}`")
            st.markdown(f"📁 **Folder**: `{r['folder']}`")
            
            # Document preview button
            if st.button(f"📄 Preview Document", key=f"preview_{i}", on_click=preview_document, args=(r['path'], i)):
                pass  # The on_click handler does the work
            
            st.markdown("---")

# Function to open a file with the system's default application
def open_file(file_path):
    try:
        # For Windows
        if os.name == 'nt':
            os.startfile(file_path)
        # For macOS
        elif os.name == 'posix' and os.uname().sysname == 'Darwin':
            subprocess.run(['open', file_path], check=True)
        # For Linux
        elif os.name == 'posix':
            subprocess.run(['xdg-open', file_path], check=True)
        return True
    except Exception as e:
        st.error(f"Error opening file: {str(e)}")
        return False

# Display document preview if one is selected
if st.session_state['preview_document']:
    preview_info = st.session_state['preview_document']
    doc_path = preview_info['path']
    
    st.subheader(f"Document Preview: {os.path.basename(doc_path)}")
    
    try:
        with st.spinner("Loading document preview..."):
            document_text = extract_text(doc_path)
            
            if document_text:
                st.text_area("Document Content", document_text, height=300)
                
                # Replace download button with 'Open File' button
                if st.button("📂 Open File with Default Application"):
                    open_file(doc_path)
            else:
                st.warning("Could not preview this document format.")
                
                # Still offer to open the file even if preview fails
                if st.button("📂 Open File with Default Application"):
                    open_file(doc_path)
    except Exception as e:
        st.error(f"Error previewing document: {str(e)}")
        # Offer to open the file even if preview fails
        if st.button("📂 Open File with Default Application"):
            open_file(doc_path)
    
    # Add a button to go back to results
    if st.button("← Back to Results"):
        st.session_state['preview_document'] = None
        st.rerun()
