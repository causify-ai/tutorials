import streamlit as st
import Ollama_utils as ou
import os
import subprocess
import json

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
    
# Initialize searchables
if 'searchables' not in st.session_state:
    st.session_state['searchables'] = {
        'Default': {
            'paths': [],
            'file_types': [".txt", ".md", ".pdf", ".docx"],
            'is_indexed': False,
            'index_path': "index/default",
            'indexed_files': []
        }
    }
if 'current_searchable' not in st.session_state:
    st.session_state['current_searchable'] = 'Default'
    
# Function to load searchables from disk
def load_searchables():
    try:
        if os.path.exists("searchables.json"):
            with open("searchables.json", "r") as f:
                searchables = json.load(f)
                st.session_state['searchables'] = searchables
                # Ensure every searchable has all required fields
                for name, searchable in st.session_state['searchables'].items():
                    if 'paths' not in searchable:
                        searchable['paths'] = []
                    if 'file_types' not in searchable:
                        searchable['file_types'] = [".txt", ".md", ".pdf", ".docx"]
                    if 'is_indexed' not in searchable:
                        searchable['is_indexed'] = False
                    if 'index_path' not in searchable:
                        searchable['index_path'] = f"index/{name.lower().replace(' ', '_')}"
                    if 'indexed_files' not in searchable:
                        searchable['indexed_files'] = []
    except Exception as e:
        print(f"Error loading searchables: {str(e)}")

# Function to save searchables to disk
def save_searchables():
    try:
        with open("searchables.json", "w") as f:
            json.dump(st.session_state['searchables'], f)
    except Exception as e:
        print(f"Error saving searchables: {str(e)}")

# Load searchables at startup
load_searchables()

# ALWAYS check if index exists on disk to handle page reloads
# This check happens on every page load, regardless of session state
for searchable_name, searchable in st.session_state['searchables'].items():
    index_path = searchable.get('index_path', f"index/{searchable_name.lower().replace(' ', '_')}")
    faiss_path = f"{index_path}/faiss_index.bin"
    metadata_path = f"{index_path}/metadata.pkl"
    
    if os.path.exists(faiss_path) and os.path.exists(metadata_path):
        # If index files exist, mark as indexed
        searchable['is_indexed'] = True
        try:
            # Load metadata to get count
            import pickle
            with open(metadata_path, "rb") as f:
                metadata = pickle.load(f)
                
                # Extract file paths based on metadata structure
                paths = []
                if isinstance(metadata, list):
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
                searchable['indexed_files'] = paths
        except Exception as e:
            print(f"Error loading metadata for {searchable_name}: {str(e)}")

# Set current searchable's indexing status
current = st.session_state['searchables'].get(st.session_state['current_searchable'], 
                                            st.session_state['searchables']['Default'])
st.session_state['indexing_complete'] = current.get('is_indexed', False)
if 'indexed_files' in current:
    st.session_state['indexed_files'] = current['indexed_files']
    st.session_state['indexed_files_count'] = len(current['indexed_files'])

st.title("📁 Document Search Engine")

# Sidebar for searchables management
st.sidebar.title("📁 Searchables")
st.sidebar.markdown("*Create and manage your document collections*")

# Searchable selector
searchable_names = list(st.session_state['searchables'].keys())
selected_searchable = st.sidebar.selectbox(
    "Select a Searchable:",
    searchable_names,
    index=searchable_names.index(st.session_state['current_searchable']),
    key="searchable_selector"
)

# Update current searchable if changed
if selected_searchable != st.session_state['current_searchable']:
    st.session_state['current_searchable'] = selected_searchable
    current = st.session_state['searchables'][selected_searchable]
    # Update indexing status
    st.session_state['indexing_complete'] = current.get('is_indexed', False)
    st.session_state['indexed_files'] = current.get('indexed_files', [])
    st.session_state['indexed_files_count'] = len(current.get('indexed_files', []))
    # Clear search-related states when switching searchables
    st.session_state['search_results'] = []
    if 'found_files' in st.session_state:
        del st.session_state['found_files']
    st.rerun()

# Create new searchable
with st.sidebar.expander("➕ Create New Searchable", expanded=False):
    new_searchable_name = st.text_input("Searchable Name:", key="new_searchable_name")
    if st.button("Create", key="create_searchable_button"):
        if new_searchable_name and new_searchable_name not in st.session_state['searchables']:
            st.session_state['searchables'][new_searchable_name] = {
                'paths': [],
                'file_types': [".txt", ".md", ".pdf", ".docx"],
                'is_indexed': False,
                'index_path': f"index/{new_searchable_name.lower().replace(' ', '_')}",
                'indexed_files': []
            }
            st.session_state['current_searchable'] = new_searchable_name
            save_searchables()
            st.success(f"Created new searchable: {new_searchable_name}")
            st.rerun()
        elif new_searchable_name in st.session_state['searchables']:
            st.error("A searchable with this name already exists.")
        else:
            st.error("Please enter a valid name.")

# Delete current searchable (with confirmation)
if len(st.session_state['searchables']) > 1 and selected_searchable != 'Default':  # Prevent deleting Default or last searchable
    with st.sidebar.expander("🗑️ Delete Current Searchable", expanded=False):
        st.warning(f"Are you sure you want to delete '{selected_searchable}'?")
        st.markdown("*This action cannot be undone.*")
        if st.button("Delete", key="delete_searchable_button"):
            # Delete index files if they exist
            index_path = st.session_state['searchables'][selected_searchable].get('index_path')
            if index_path and os.path.exists(index_path):
                import shutil
                try:
                    shutil.rmtree(index_path, ignore_errors=True)
                except Exception as e:
                    print(f"Error deleting index: {str(e)}")
                    
            # Remove from searchables
            del st.session_state['searchables'][selected_searchable]
            st.session_state['current_searchable'] = 'Default'  # Always go back to Default after deletion
            save_searchables()
            # Clear search-related states
            st.session_state['search_results'] = []
            if 'found_files' in st.session_state:
                del st.session_state['found_files']
            st.success(f"Deleted searchable: {selected_searchable}")
            st.rerun()
elif selected_searchable == 'Default':
    # Show a message that Default cannot be deleted
    with st.sidebar.expander("ℹ️ About Default Searchable", expanded=False):
        st.info("The Default searchable cannot be deleted.")
        st.markdown("You can create additional searchables for different document collections.")

# Get current searchable
current_searchable = st.session_state['searchables'][st.session_state['current_searchable']]

# Manage paths in current searchable
st.sidebar.markdown("---")
st.sidebar.subheader(f"📂 Manage '{selected_searchable}'")

# Add a new path to current searchable
new_path = st.sidebar.text_input(
    "Add folder or file path:",
    "",
    placeholder="C:\\Users\\Documents",
    help="Enter a folder path like 'C:\\Users\\Documents' or a specific file path",
    key="new_path_input"
)

if st.sidebar.button("Add Path", key="add_path_button"):
    if new_path:
        if os.path.exists(new_path):
            if new_path not in current_searchable['paths']:
                current_searchable['paths'].append(new_path)
                save_searchables()
                st.sidebar.success(f"Added: {new_path}")
            else:
                st.sidebar.info("This path is already in the searchable.")
        else:
            st.sidebar.error("Path not found. Please enter a valid path.")
st.sidebar.info("""
### Running in Docker?
When adding paths, use the data directory:
Example: `data/dummy.txt` or `data/`
""")
# Display current paths and allow removal
if current_searchable['paths']:
    st.sidebar.markdown("### Current Paths:")
    for i, path in enumerate(current_searchable['paths']):
        col1, col2 = st.sidebar.columns([4, 1])
        with col1:
            st.markdown(f"{i+1}. `{path}`")
        with col2:
            if st.button("🗑️", key=f"remove_path_{i}"):
                current_searchable['paths'].remove(path)
                save_searchables()
                st.rerun()
else:
    st.sidebar.info("No paths added yet. Add a folder or file path above.")

# File types to include
st.sidebar.markdown("### File Types to Include:")
file_types = st.sidebar.multiselect(
    "Select file types:",
    [".txt", ".md", ".py", ".js", ".html", ".css", ".json", ".csv", ".pdf", ".docx"],
    default=current_searchable.get('file_types', [".txt", ".md", ".pdf", ".docx"]),
    key="file_types_select"
)
if file_types != current_searchable.get('file_types', []):
    current_searchable['file_types'] = file_types
    save_searchables()

# Step 1: Scan files
if st.sidebar.button("🔍 Scan Files", key="scan_files_button"):
    with st.spinner("Scanning for documents..."):
        try:
            all_files = []
            for path in current_searchable['paths']:
                # Check if path exists
                if not os.path.exists(path):
                    st.sidebar.error(f"Path not found: {path}")
                    continue
                
                # Check if it's a file or directory
                if os.path.isfile(path):
                    if any(path.endswith(ext) for ext in file_types):
                        all_files.append(path)
                else:
                    # It's a directory, scan for files
                    files = ou.scan_directory(path, extensions=file_types)
                    all_files.extend(files)
                    
            if all_files:
                st.session_state['found_files'] = all_files
            else:
                st.session_state['found_files'] = []
                st.sidebar.warning("No matching files found in the selected paths.")
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

        # Always show processing options, but with different messaging based on state
        if current_searchable.get('is_indexed', False):
            total_files = len(found_files)
            indexed_files = len(current_searchable.get('indexed_files', []))
            
            if indexed_files < total_files:
                st.info(f"There are {total_files - indexed_files} new files that can be added to make searchable.")
                if st.button("🔄 Process New Documents", key="update_index_button"):
                    # Create index directory if it doesn't exist
                    index_dir = current_searchable.get('index_path', f"index/{selected_searchable.lower().replace(' ', '_')}")
                    os.makedirs(index_dir, exist_ok=True)
                    
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
                        index_path=f"{index_dir}/faiss_index.bin",
                        metadata_path=f"{index_dir}/metadata.pkl"
                    )
                    current_searchable['indexed_files'] = found_files
                    st.session_state['indexed_files'] = found_files
                    st.session_state['indexed_files_count'] = len(found_files)
                    
                    # Mark as indexed
                    current_searchable['is_indexed'] = True
                    st.session_state['indexing_complete'] = True
                    
                    # Increment index version to invalidate cache
                    st.session_state['index_version'] += 1
                    
                    # Save the updated searchable
                    save_searchables()
                    
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
                    index_dir = current_searchable.get('index_path', f"index/{selected_searchable.lower().replace(' ', '_')}")
                    import shutil
                    try:
                        shutil.rmtree(index_dir, ignore_errors=True)
                        os.makedirs(index_dir, exist_ok=True)
                        current_searchable['is_indexed'] = False
                        current_searchable['indexed_files'] = []
                        st.session_state['indexing_complete'] = False
                        st.session_state['indexed_files_count'] = 0
                        st.session_state['indexed_files'] = []
                        save_searchables()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error clearing processed files: {str(e)}")
        else:
            # First-time indexing
            confirm = st.checkbox("✅ Confirm to proceed with document processing", key="confirm_processing")
            if confirm:
                if st.button("🚀 Make Documents Searchable", key="build_index_button"):
                    # Create index directory if it doesn't exist
                    index_dir = current_searchable.get('index_path', f"index/{selected_searchable.lower().replace(' ', '_')}")
                    os.makedirs(index_dir, exist_ok=True)
                    
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
                        index_path=f"{index_dir}/faiss_index.bin",
                        metadata_path=f"{index_dir}/metadata.pkl"
                    )
                    
                    # Increment index version to invalidate cache
                    st.session_state['index_version'] += 1
                    
                    # Keep the final progress state
                    progress_bar.progress(1.0)
                    message_placeholder.text("✅ Processing complete!")
                    
                    # Set indexing complete flag
                    current_searchable['is_indexed'] = True
                    current_searchable['indexed_files'] = found_files
                    st.session_state['indexing_complete'] = True
                    st.session_state['indexed_files_count'] = len(found_files)
                    st.session_state['indexed_files'] = found_files
                    
                    # Save the updated searchable
                    save_searchables()
                    
                    st.success(f"✅ Documents processed successfully! {len(found_files)} files are now searchable.")
                    st.balloons()
    else:
        st.warning("No supported documents found in the selected paths.")

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
        st.markdown(f"*{unique_doc_count} unique documents ready for search in '{selected_searchable}'*")
    elif st.session_state['indexed_files_count'] > 0:
        st.markdown(f"*{st.session_state['indexed_files_count']} documents ready for search in '{selected_searchable}'*")
        
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
                
                # Get index paths for current searchable
                index_dir = current_searchable.get('index_path', f"index/{selected_searchable.lower().replace(' ', '_')}")
                faiss_path = f"{index_dir}/faiss_index.bin"
                metadata_path = f"{index_dir}/metadata.pkl"
                
                # Search documents
                results = ou.search_documents(
                    refined_query, 
                    top_k=st.session_state['num_results'], 
                    index_path=faiss_path, 
                    metadata_path=metadata_path
                )
                
                if isinstance(results, list):
                    st.session_state['search_results'] = results
                elif isinstance(results, dict) and "error" in results:
                    st.error(results["error"])
                    st.session_state['search_results'] = []
else:
    # Show a more comprehensive guide when no documents have been processed yet
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
            <div style="background-color:var(--background-color);border-radius:10px;padding:10px;">
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
        No supported documents were found in the selected paths.
        
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