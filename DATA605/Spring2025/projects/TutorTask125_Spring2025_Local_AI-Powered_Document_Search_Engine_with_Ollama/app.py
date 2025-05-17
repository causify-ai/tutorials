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
if 'num_results' not in st.session_state:
    st.session_state['num_results'] = 10

# ALWAYS check if index exists on disk to handle page reloads
# This check happens on every page load, regardless of session state
if os.path.exists("index/faiss_index.bin") and os.path.exists("index/metadata.pkl"):
    # If index files exist, mark as complete regardless of session state
    st.session_state['indexing_complete'] = True
    try:
        # Load metadata to get count
        import pickle
        with open("index/metadata.pkl", "rb") as f:
            metadata = pickle.load(f)
            st.session_state['full_metadata'] = metadata  # Store the full metadata for debugging
            
            # Print metadata structure for debugging
            print(f"Metadata type: {type(metadata)}")
            print(f"Metadata sample: {str(metadata)[:500]}..." if len(str(metadata)) > 500 else str(metadata))
            
            if isinstance(metadata, list):
                st.session_state['indexed_files_count'] = len(metadata)
                
                # Extract file paths based on metadata structure
                paths = []
                for item in metadata:
                    if isinstance(item, dict):
                        # Try different possible keys
                        if 'file_path' in item:
                            paths.append(item['file_path'])
                        elif 'path' in item:
                            paths.append(item['path'])
                        elif 'filename' in item:
                            paths.append(item['filename'])
                        elif 'source' in item:
                            paths.append(item['source'])
                
                # Store file paths for display
                st.session_state['indexed_files'] = paths
                print(f"Found {len(paths)} file paths in metadata")
                
                # Ensure we have at least one valid file path
                if not any(st.session_state['indexed_files']):
                    st.session_state['indexed_files_count'] = 0
                    print("No valid file paths found in metadata")
            else:
                # For older index versions or different formats
                st.session_state['indexed_files_count'] = 1
                st.session_state['indexed_files'] = []
                print("Metadata is not a list, cannot extract file paths")
    except Exception as e:
        # If error reading metadata, just set a placeholder value but keep indexing_complete True
        # since we confirmed the files exist
        st.session_state['indexed_files_count'] = 1
        st.session_state['indexed_files'] = []
        st.session_state['metadata_error'] = str(e)
        print(f"Error loading metadata: {str(e)}")

st.title("📁 Document Search Engine")

st.sidebar.title("📁 Document Setup & Organization")
user_path = st.sidebar.text_input("Enter the local file path to index:", "", 
                                placeholder="C:\\Users\\Documents",
                                help="Enter a folder path like 'C:\\Users\\Documents' or '.' for current directory",
                                key="user_path_input")

# Help text for drag and drop
st.sidebar.info("💡 **Tip**: You can enter any local folder path to index its files.")

# File types to include
file_types = st.sidebar.multiselect(
    "Select file types to include",
    [".txt", ".md", ".py", ".js", ".html", ".css", ".json", ".csv", ".pdf"],
    default=[".txt", ".md", ".pdf"]
)

# Step 1: Scan files
if st.sidebar.button("🔍 Scan Files", key="scan_files_button"):
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
                st.info(f"There are {total_files - indexed_files} new files that can be added to make searchable.")
                if st.button("🔄 Process New Documents", key="update_index_button"):
                    # Create a placeholder for the progress bar
                    progress_placeholder = st.empty()
                    progress_bar = progress_placeholder.progress(0)
                    
                    # Create a placeholder for progress message
                    message_placeholder = st.empty()
                    message_placeholder.text("Starting to process documents...")
                    
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
                    message_placeholder.text("✅ Processing complete!")
                    
                    st.success(f"✅ New documents processed! Total files ready for search: {total_files}")
                    st.balloons()
            else:
                st.success(f"✅ All {total_files} files are ready for search!")
                
                # Option to rebuild index from scratch
                if st.button("🔄 Reprocess All Documents", key="rebuild_index_button"):
                    # Delete existing index files
                    import shutil
                    try:
                        shutil.rmtree('index', ignore_errors=True)
                        st.session_state['indexing_complete'] = False
                        st.session_state['indexed_files_count'] = 0
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error clearing processed files: {str(e)}")
        else:
            # First-time indexing
            confirm = st.checkbox("✅ Confirm to proceed with document processing", key="confirm_processing")
            if confirm:
                if st.button("🚀 Make Documents Searchable", key="build_index_button"):
                    # Create a placeholder for the progress bar
                    progress_placeholder = st.empty()
                    progress_bar = progress_placeholder.progress(0)
                    
                    # Create a placeholder for progress message
                    message_placeholder = st.empty()
                    message_placeholder.text("Starting to process documents...")
                    
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
                    message_placeholder.text("✅ Processing complete!")
                    
                    # Set indexing complete flag
                    st.session_state['indexing_complete'] = True
                    st.session_state['indexed_files_count'] = len(found_files)
                    # Save the list of indexed files to session state
                    st.session_state['indexed_files'] = found_files
                    st.success(f"✅ Documents processed successfully! {len(found_files)} files are now searchable.")
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
# Only show search section if documents have been indexed
if st.session_state['indexing_complete']:
    st.markdown("---")
    st.header("🔍 Search Your Documents")
    
    # Calculate count of unique documents
    unique_doc_count = 0
    unique_docs_dict = {}
    if 'indexed_files' in st.session_state and st.session_state['indexed_files']:
        indexed_files = st.session_state['indexed_files']
        # Get unique documents by normalizing paths
        for file_path in indexed_files:
            if file_path and isinstance(file_path, str):
                norm_path = file_path.strip()
                if norm_path not in unique_docs_dict:
                    unique_docs_dict[norm_path] = 1
                else:
                    unique_docs_dict[norm_path] += 1
        unique_doc_count = len(unique_docs_dict)
    
    # Display indexed file count with unique documents
    if unique_doc_count > 0:
        st.markdown(f"*{unique_doc_count} unique documents ready for search*")
    elif st.session_state['indexed_files_count'] > 0:
        st.markdown(f"*{st.session_state['indexed_files_count']} documents ready for search*")
        
    # Show list of indexed documents in an expander
    with st.expander("📄 View Indexed Documents", expanded=False):
        # Display the list of unique documents
        if unique_doc_count > 0:
            # Group files by folder for better organization, but only show unique files
            files_by_folder = {}
            
            for file_path in unique_docs_dict.keys():
                folder = os.path.dirname(file_path)
                filename = os.path.basename(file_path)
                
                if folder not in files_by_folder:
                    files_by_folder[folder] = []
                
                # Add file without chunk count
                files_by_folder[folder].append(filename)
            
            # Display files organized by folder
            for folder, files in files_by_folder.items():
                st.markdown(f"**Folder: `{folder}`**")
                for filename in sorted(files):
                    st.markdown(f"- {filename}")
                st.markdown("---")
        else:
            st.info("No documents have been indexed yet, or the document list could not be loaded.")

    # Function to handle document preview
    def preview_document(doc_path, index):
        st.session_state['preview_document'] = {'path': doc_path, 'index': index}

    # Add num_results slider
    num_results = st.slider("Number of results to show:", min_value=5, max_value=50, value=st.session_state['num_results'], step=5)
    st.session_state['num_results'] = num_results

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
                
                # Search documents - use the selected number of results instead of hardcoded 10
                results = ou.search_documents(
                    refined_query, 
                    top_k=st.session_state['num_results'], 
                    index_path="index/faiss_index.bin", 
                    metadata_path="index/metadata.pkl"
                )
                
                if isinstance(results, list):
                    st.session_state['search_results'] = results
                elif isinstance(results, dict) and "error" in results:
                    st.error(results["error"])
                    st.session_state['search_results'] = []
else:
    # Only show the welcome guide for first-time users (no files found yet)
    if 'found_files' not in st.session_state:
        # First-time user experience - provide a comprehensive guide
        st.markdown("---")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("## 👋 Welcome to Your Document Search Engine!")
            st.markdown("""
            This tool helps you search through your local documents using AI technology.
            
            **How it works:**
            1. The tool analyzes your documents
            2. It creates a searchable database
            3. You can then ask questions or search for information
            4. AI helps find the most relevant content
            """)
        
        with col2:
            st.markdown("## 🚀 Get Started")
            st.markdown("""
            **Follow these simple steps:**
            
            1️⃣ Use the sidebar to enter a folder path containing your documents
            
            2️⃣ Select which file types you want to include
            
            3️⃣ Click "Scan Files" to find documents
            
            4️⃣ Process the documents to make them searchable
            
            5️⃣ Start searching with natural language questions!
            """)
            
        # Add a visual divider
        st.markdown("---")
        
        # Add example use cases
        st.markdown("### 💡 Example Uses")
        use_case1, use_case2, use_case3 = st.columns(3)
        
        with use_case1:
            st.markdown("#### 📚 Research")
            st.markdown("Search through your research papers, notes, and references to find relevant information quickly.")
            
        with use_case2:
            st.markdown("#### 💻 Code Projects")
            st.markdown("Search across your codebase to find specific functions, patterns, or documentation.")
            
        with use_case3:
            st.markdown("#### 📝 Documents")
            st.markdown("Find information across your personal or work documents without opening each file.")
    
    elif len(st.session_state['found_files']) > 0:
        # Files found but not processed yet
        st.markdown("---")
        st.markdown("## 🔍 Almost There!")
        
        # Progress indicator
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### Files Found! ✅")
            st.markdown(f"**{len(st.session_state['found_files'])} documents** have been located.")
            st.markdown("### Next Step: Process Documents ⏩")
            st.markdown("""
            Your documents need to be processed before you can search them.
            
            Use the sidebar options to process your documents and make them searchable.
            """)
            
        with col2:
            # Visual representation of progress
            st.markdown("### Your Progress")
            progress_html = """
            <div style="background-color:#3b3b3b;border-radius:10px;padding:10px;">
                <div style="display:flex;align-items:center;margin-bottom:10px;">
                    <div style="background-color:#4CAF50;color:white;border-radius:50%;width:25px;height:25px;display:flex;align-items:center;justify-content:center;margin-right:10px;">1</div>
                    <div><strong>Select folder</strong> ✅</div>
                </div>
                <div style="display:flex;align-items:center;margin-bottom:10px;">
                    <div style="background-color:#4CAF50;color:white;border-radius:50%;width:25px;height:25px;display:flex;align-items:center;justify-content:center;margin-right:10px;">2</div>
                    <div><strong>Scan files</strong> ✅</div>
                </div>
                <div style="display:flex;align-items:center;margin-bottom:10px;">
                    <div style="background-color:#ff9800;color:white;border-radius:50%;width:25px;height:25px;display:flex;align-items:center;justify-content:center;margin-right:10px;">3</div>
                    <div><strong>Process documents</strong> ⏳</div>
                </div>
                <div style="display:flex;align-items:center;">
                    <div style="background-color:#e0e0e0;color:black;border-radius:50%;width:25px;height:25px;display:flex;align-items:center;justify-content:center;margin-right:10px;">4</div>
                    <div><strong>Search documents</strong></div>
                </div>
            </div>
            """
            st.markdown(progress_html, unsafe_allow_html=True)
            
            # Add a hint pointing to the sidebar
            st.markdown("""
            👈 **Look at the sidebar** to complete the process!
            """)
    else:
        # No files found
        st.markdown("---")
        st.markdown("## 🔍 No Documents Found")
        st.markdown("""
        No supported documents were found in the selected path.
        
        **Try the following:**
        - Check that you entered the correct folder path
        - Make sure the folder contains documents of the selected file types
        - Try selecting different file types in the sidebar
        
        Need help? Check that the path exists and contains readable files.
        """)

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
                st.text_area("", formatted_snippet, height=min(200, 30 + 20 * (formatted_snippet.count('\n') + 1)), label_visibility="collapsed", key=f"snippet_text_area_{i}")
            
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
                st.text_area("Document Content", document_text, height=300, key="document_preview_text_area")
                
                # Replace download button with 'Open File' button
                if st.button("📂 Open File with Default Application", key="open_file_button"):
                    open_file(doc_path)
            else:
                st.warning("Could not preview this document format.")
                
                # Still offer to open the file even if preview fails
                if st.button("📂 Open File with Default Application", key="open_file_button_fallback"):
                    open_file(doc_path)
    except Exception as e:
        st.error(f"Error previewing document: {str(e)}")
        # Offer to open the file even if preview fails
        if st.button("📂 Open File with Default Application", key="open_file_button_error"):
            open_file(doc_path)
    
    # Add a button to go back to results
    if st.button("← Back to Results", key="back_to_results_button"):
        st.session_state['preview_document'] = None
        st.rerun()