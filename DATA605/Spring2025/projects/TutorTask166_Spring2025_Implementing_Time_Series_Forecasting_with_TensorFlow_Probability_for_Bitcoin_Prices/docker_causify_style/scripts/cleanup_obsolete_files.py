#!/usr/bin/env python3
"""
Script to identify and optionally delete obsolete files in the Bitcoin forecast project.
This script helps clean up the project by removing unused template and example files.
"""
import os
import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Define the project root directory
PROJECT_ROOT = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Files that are obsolete and can be safely deleted
OBSOLETE_FILES = [
    # Template and example files
    "template.example.py",
    "template.example.ipynb",
    "template.example.md",
    "template.API.py",
    "template.API.ipynb",
    "template.API.md",
    
    # Utility files that have been consolidated into template_utils.py
    "utilities/timestamp_format.py",
    "utilities/logger.py",
    "utilities/price_format.py",
    "utilities/data_loader.py",
    "utilities/config_parser.py",
]

# Directories to check for obsolete files (recursive)
DIRECTORIES_TO_CHECK = [
    "src/utils",
    "src/dashboard",
    "src/features",
    "src/models",
    "src/trainers",
    "src/data_loader",
]

def is_file_used(file_path, project_root):
    """Check if a file is referenced anywhere in the project."""
    # Get the file's basename for simpler matching
    basename = os.path.basename(file_path)
    
    # Skip checking certain files that might have many false positives
    if basename in ["__init__.py", "README.md", "requirements.txt"]:
        return True
    
    # Check if the file is imported or referenced in other files
    import_count = 0
    
    # Different ways the file might be imported
    module_name = os.path.splitext(basename)[0]
    import_patterns = [
        f"import {module_name}",
        f"from {module_name} import",
        f"from .{module_name} import",
        f"from ..{module_name} import",
    ]
    
    # Walk through all Python files in the project
    for root, _, files in os.walk(project_root):
        for f in files:
            if not f.endswith('.py') or os.path.join(root, f) == file_path:
                continue
                
            try:
                with open(os.path.join(root, f), 'r', encoding='utf-8') as file:
                    content = file.read()
                    
                    # Check if any import pattern is found
                    for pattern in import_patterns:
                        if pattern in content:
                            import_count += 1
                            logger.debug(f"File {file_path} is imported in {os.path.join(root, f)}")
            except Exception as e:
                logger.warning(f"Error reading file {os.path.join(root, f)}: {e}")
    
    return import_count > 0

def find_obsolete_files(project_root, check_usage=False):
    """Find obsolete files in the project."""
    obsolete_files = []
    
    # Check predefined obsolete files
    for file_path in OBSOLETE_FILES:
        full_path = os.path.join(project_root, file_path)
        if os.path.exists(full_path):
            if not check_usage or not is_file_used(full_path, project_root):
                obsolete_files.append(full_path)
    
    # Check directories for potentially unused files
    if check_usage:
        for directory in DIRECTORIES_TO_CHECK:
            dir_path = os.path.join(project_root, directory)
            if os.path.exists(dir_path) and os.path.isdir(dir_path):
                for root, _, files in os.walk(dir_path):
                    for f in files:
                        if f.endswith('.py') and f != '__init__.py':
                            file_path = os.path.join(root, f)
                            if not is_file_used(file_path, project_root):
                                obsolete_files.append(file_path)
    
    return obsolete_files

def delete_files(files, dry_run=True):
    """Delete the specified files."""
    for file_path in files:
        try:
            if dry_run:
                logger.info(f"Would delete: {file_path}")
            else:
                os.remove(file_path)
                logger.info(f"Deleted: {file_path}")
        except Exception as e:
            logger.error(f"Failed to delete {file_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description='Clean up obsolete files in the Bitcoin forecast project')
    parser.add_argument('--delete', action='store_true', help='Actually delete the files (default is dry run)')
    parser.add_argument('--check-usage', action='store_true', help='Check if files are used before marking as obsolete')
    args = parser.parse_args()
    
    logger.info(f"Starting cleanup script in {'delete' if args.delete else 'dry run'} mode")
    logger.info(f"Project root: {PROJECT_ROOT}")
    
    # Find obsolete files
    obsolete_files = find_obsolete_files(PROJECT_ROOT, args.check_usage)
    
    if obsolete_files:
        logger.info(f"Found {len(obsolete_files)} obsolete files:")
        for file in obsolete_files:
            logger.info(f"  - {os.path.relpath(file, PROJECT_ROOT)}")
        
        # Delete files if requested
        delete_files(obsolete_files, dry_run=not args.delete)
        
        if not args.delete:
            logger.info("\nTo delete these files, run: python scripts/cleanup_obsolete_files.py --delete")
    else:
        logger.info("No obsolete files found")

if __name__ == "__main__":
    main() 