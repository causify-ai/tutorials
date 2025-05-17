import streamlit as st
import Ollama_utils as ou
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
user_path = st.sidebar.text_input("Enter the local file path to index:", ".", 
                                help="Enter a folder path like 'C:\\Users\\Documents' or '.' for current directory")

# Help text for drag and drop
st.sidebar.info("💡 **Tip**: You can enter any local folder path to index its files.")

# File types to include
file_types = st.sidebar.multiselect(
    "Select file types to index",
    [".txt", ".md", ".py", ".js", ".html", ".css", ".json", ".csv", ".pdf"],
    default=[".txt", ".md", ".py"]
)

# Step 1: Scan files
if st.sidebar.button("🔍 Scan Files"):
    with st.spinner("Scanning for documents..."):
        try:
            # Check if path exists
            if not os.path.exists(user_path):
                st.sidebar.error(f"Path not found: {user_path}")
            else:
                files = ou.scan_directory(user_path, extensions=file_types)
                st.session_state['found_files'] = files
        except Exception as e:
            st.sidebar.error(f"Error scanning files: {str(e)}")

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
                    
                    # Call build_document_index with the progress callback
                    ou.build_document_index(
                        found_files, 
                        progress_callback=update_progress,
                        index_path="index/faiss_index.bin",
                        metadata_path="index/metadata.pkl"
                    )
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
                    
                    # Call build_document_index with the progress callback
                    success = ou.build_document_index(
                        found_files, 
                        progress_callback=update_progress,
                        index_path="index/faiss_index.bin",
                        metadata_path="index/metadata.pkl"
                    )
                    
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

# Caching for search components
@st.cache_resource
def load_embedding_model(_index_version=None):
    """
    Load the embedding model. The _index_version parameter ensures the cache is invalidated
    when the index is updated, even though it's not used in the function.
    """
    return ou.get_embedding_model()

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
        try:
            # Attempt to enhance the query using Ollama
            refined_query = ou.query_ollama(
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
        except Exception as e:
            st.warning(f"Could not refine query with Ollama: {str(e)}. Using original query.")
            refined_query = query
        
        with st.spinner("Searching..."):
            # Make sure the model is loaded (with cache invalidation via index_version)
            _ = load_embedding_model(_index_version=st.session_state['index_version'])
            
            # Search documents
            results = ou.search_documents(
                refined_query, 
                top_k=10, 
                index_path="index/faiss_index.bin", 
                metadata_path="index/metadata.pkl"
            )
            
            if isinstance(results, list):
                st.session_state['search_results'] = results
            elif isinstance(results, dict) and "error" in results:
                st.error(results["error"])
                st.session_state['search_results'] = []

# Always display results if they exist in session state
if st.session_state['search_results']:
    st.subheader("Top Results:")
    for i, r in enumerate(st.session_state['search_results']):
        # Prepare snippet for display - ensure it's not empty and format it nicely
        snippet = r['snippet'] if r['snippet'] else "No preview available for this file type."
        
        # Format the snippet - break long lines and limit width
        formatted_snippet = snippet
        # Replace tabs with spaces to prevent layout issues
        formatted_snippet = formatted_snippet.replace('\t', '    ')
        
        # Determine if file is likely code based on extension
        code_extensions = ['.py', '.js', '.html', '.css', '.json', '.md', '.ts', '.jsx', '.tsx', '.cpp', '.c', '.java']
        is_code_file = any(r['file_path'].lower().endswith(ext) for ext in code_extensions)
        
        # Determine language for syntax highlighting
        file_ext = os.path.splitext(r['file_path'])[1][1:] if os.path.splitext(r['file_path'])[1] else ""
        lang_map = {
            'py': 'python',
            'js': 'javascript',
            'html': 'html',
            'css': 'css',
            'json': 'json',
            'md': 'markdown',
            'ts': 'typescript',
            'jsx': 'jsx',
            'tsx': 'tsx',
            'cpp': 'cpp',
            'c': 'c',
            'java': 'java'
        }
        code_lang = lang_map.get(file_ext, "text")
        
        with st.expander(f"**Result {i+1}** - Score: {r['score']:.4f} - {os.path.basename(r['file_path'])}", expanded=False):
            # Display snippet with code formatting if it's a code file
            if is_code_file and snippet != "No preview available for this file type.":
                st.markdown("**Snippet**:")
                st.code(formatted_snippet, language=code_lang)
            else:
                st.markdown("**Snippet**:")
                st.text_area("", formatted_snippet, height=min(200, 30 + 20 * (formatted_snippet.count('\n') + 1)), label_visibility="collapsed")
            
            st.markdown(f"📄 **File**: `{r['file_path']}`")
            st.markdown(f"📁 **Folder**: `{os.path.dirname(r['file_path'])}`")
            
            # Document preview button
            if st.button(f"📄 Preview Document", key=f"preview_{i}", on_click=preview_document, args=(r['file_path'], i)):
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
            document_text = ou.extract_text(doc_path)
            
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