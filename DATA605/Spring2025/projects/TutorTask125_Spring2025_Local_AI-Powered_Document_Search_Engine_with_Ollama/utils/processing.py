# utils/processing.py

import os
import fitz  # PyMuPDF
from docx import Document
import re

def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if ext == '.txt':
            return extract_txt(file_path)
        elif ext == '.pdf':
            return extract_pdf(file_path)
        elif ext == '.docx':
            return extract_docx(file_path)
        else:
            return ""
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return ""

def extract_txt(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()

def extract_pdf(file_path):
    doc = fitz.open(file_path)
    text = "\n\n".join([page.get_text() for page in doc])
    doc.close()
    return text

def extract_docx(file_path):
    doc = Document(file_path)
    return "\n\n".join([para.text for para in doc.paragraphs if para.text.strip()])


def chunk_text(text, max_chars=500):
    paragraphs = re.split(r'\n\s*\n', text)  # paragraph splitter
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        # If current chunk + this para exceeds limit, start new chunk
        if len(current_chunk) + len(para) + 1 > max_chars:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para
        else:
            current_chunk += " " + para

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks
