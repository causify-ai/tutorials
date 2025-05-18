# Quick Start Guide

This guide provides a quick overview of how to use the Local AI-Powered Document Search Engine with Ollama.

## Starting the Application

### Local Installation
```bash
# Navigate to the project directory
cd DATA605/Spring2025/projects/TutorTask125_Spring2025_Local_AI-Powered_Document_Search_Engine_with_Ollama

# Run the Streamlit app
streamlit run app.py
```

### Docker Installation (Windows)
```powershell
# Build the Docker image
docker build -t ollama-notebook -f ./docker_data605_style/Dockerfile .

# If you have an existing container, remove it
docker stop ollama-notebook
docker rm ollama-notebook

# Run the container
docker run -d --name ollama-notebook -p 8501:8501 -p 8888:8888 -p 11434:11434 -v ${PWD}:/app -v C:/Users:/data/home -v C:/Documents:/data/documents ollama-notebook
```

Then open your browser and go to: http://localhost:8501

## 5-Minute Setup

1. **Create a Searchable** (or use the default one):
   - In the sidebar, expand "➕ Create New Searchable"
   - Enter a name (e.g., "Work Documents")
   - Click "Create"

2. **Add Document Paths**:
   - Enter a folder path containing your documents (e.g., `C:\Users\YourName\Documents`)
   - Click "Add Path"
   - You can add multiple paths if needed

3. **Select File Types**:
   - Choose which file types to include (PDF, TXT, etc.)

4. **Scan for Documents**:
   - Click "🔍 Scan Files"
   - Review the list of found documents

5. **Process Documents**:
   - Check "✅ Confirm to proceed with document processing"
   - Click "🚀 Make Documents Searchable"
   - Wait for processing to complete (this may take a few minutes for large document collections)

## Searching Documents

1. Enter your question or keywords in the search box
2. Adjust the number of results if needed
3. Click "🔍 Search"
4. Click on results to expand them and view snippets
5. Use "📄 Preview Document" to view the full content

## Tips & Tricks

- **Create Multiple Searchables**: Create different searchables for different projects or topics
- **Mix Folders and Files**: You can add both entire folders and individual files to a searchable
- **Natural Language Queries**: Try asking questions instead of just using keywords
- **Document Preview**: Use the preview feature to quickly check document contents without leaving the app
- **Switch Between Searchables**: Use the dropdown at the top of the sidebar to switch between your document collections

## Troubleshooting

- If the search returns no results, try:
  - Using simpler or more general terms
  - Making sure your documents contain the information you're looking for
  - Checking if the right searchable is selected
  
- If document processing is slow:
  - Try processing smaller batches of documents
  - Limit file types to only what you need
  - Exclude very large files 