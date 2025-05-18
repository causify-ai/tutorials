import os

SUPPORTED_EXTENSIONS = ['.txt', '.pdf', '.docx', '.py', '.js', '.java', '.cpp', '.c', '.ts', '.html', '.css', '.xml', '.ipynb', '.md']

# Any folder name (not full path) in this list will be skipped
EXCLUDED_DIR_NAMES = {
    'AppData', 'anaconda3', 'node_modules', '__pycache__', 'WindowsNoEditor',
    '.git', '.vscode', '.conda', '.cache', '.mamba', 'env', 'venv',
}

# Set max file size (in bytes) – default: 100 MB
MAX_FILE_SIZE = 100 * 1024 * 1024

def scan_files(root_dir, max_file_size=MAX_FILE_SIZE):
    file_paths = []
    for root, dirs, files in os.walk(root_dir):
        # Exclude hidden and known noisy directories
        dirs[:] = [
            d for d in dirs
            if not d.startswith('.') and d not in EXCLUDED_DIR_NAMES
        ]

        for file in files:
            file_path = os.path.join(root, file)
            if any(file.lower().endswith(ext) for ext in SUPPORTED_EXTENSIONS):
                try:
                    if os.path.getsize(file_path) <= max_file_size:
                        file_paths.append(file_path)
                except Exception as e:
                    print(f"⚠️ Skipped {file_path}: {e}")
    return file_paths
