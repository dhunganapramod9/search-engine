import os
import re

from typing import List, Tuple, Optional
from PyPDF2 import PdfReader
import docx


def load_documents(folder_path: str = "documents") -> Tuple[List[str], List[str]]:
    docs = []
    filenames = []
    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            filepath = os.path.join(folder_path, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:  # Only add non-empty files
                        docs.append(content)
                        filenames.append(filename)
            except UnicodeDecodeError:
                print(f"Warning: Could not decode {filename}, skipping...")
            except Exception as e:
                print(f"Error reading {filename}: {e}")
                
    return docs, filenames





def extract_text_from_file(file) -> str:
    if not file or not file.filename:
        return ""
        
    try:
        if file.filename.lower().endswith(".txt"):
            return file.read().decode("utf-8")
        elif file.filename.lower().endswith(".pdf"):
            reader = PdfReader(file)
            text_parts = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            return "\n".join(text_parts)
        elif file.filename.lower().endswith(".docx"):
            doc = docx.Document(file)
            return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    except Exception as e:
        print(f"Error extracting text from {file.filename}: {e}")
        
    return ""


def sanitize_filename(filename: str) -> str:
    # Remove path components and potentially dangerous characters
    filename = os.path.basename(filename)
    filename = re.sub(r'[^\w\s.-]', '', filename)
    return filename.strip()


def extract_snippet(content: str, max_length: int = 150) -> str:
    if not content:
        return ""
        
    # Try to get first complete sentence
    sentences = content.split('.')
    if sentences and len(sentences[0]) < max_length:
        return sentences[0].strip() + '.'
    
    # If first sentence is too long, truncate at word boundary
    if len(content) <= max_length:
        return content
        
    truncated = content[:max_length]
    last_space = truncated.rfind(' ')
    if last_space > max_length * 0.8:  # Only truncate if we don't lose too much
        return truncated[:last_space] + '...'
    
    return truncated + '...'
