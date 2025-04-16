import streamlit as st
from utils.file_scanner import scan_files
from utils.build_index import build_faiss_index

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

        confirm = st.checkbox("✅ Confirm to proceed with indexing")

        if confirm and st.button("🚀 Build Index"):
            with st.spinner("Processing and indexing documents..."):
                build_faiss_index(found_files)
            st.success("Index built successfully!")
    else:
        st.warning("No supported documents found in the selected path.")

from utils.search import load_index_and_metadata, search_documents
from sentence_transformers import SentenceTransformer

# Section: Search
st.markdown("---")
st.header("🔍 Search Your Documents")

query = st.text_input("Enter your question or keyword:")
if query:
    with st.spinner("Searching..."):
        # Load model + index + metadata once
        @st.cache_resource
        def load_search_components():
            model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
            index, metadata = load_index_and_metadata()
            return model, index, metadata

        model, index, metadata = load_search_components()
        results = search_documents(query, model, index, metadata)

    st.subheader("Top Results:")
    for r in results:
        st.markdown(f"**Score**: `{r['score']:.4f}`")
        st.markdown(f"**Snippet**: {r['snippet']}")
        st.markdown(f"📄 **File**: `{r['path']}`")
        st.markdown(f"📁 **Folder**: `{r['folder']}`")
        st.markdown("---")
