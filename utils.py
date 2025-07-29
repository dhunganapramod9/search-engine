import os
import re
from collections import Counter
from typing import List, Tuple, Optional
from PyPDF2 import PdfReader
import docx


def load_documents(folder_path: str = "documents") -> Tuple[List[str], List[str]]:
    """
    Load all text documents from the specified folder.
    
    Args:
        folder_path: Path to the documents directory
        
    Returns:
        Tuple of (document_contents, filenames)
    """
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


def extract_keywords(docs: List[str], top_n: int = 10) -> List[str]:
    """
    Extract the most common keywords from document corpus.
    
    Args:
        docs: List of document strings
        top_n: Number of top keywords to return
        
    Returns:
        List of most common keywords
    """
    if not docs:
        return []
        
    all_text = " ".join(docs).lower()
    # Extract words with 4+ characters, excluding common stop words
    words = re.findall(r'\b[a-z]{4,}\b', all_text)
    
    # Filter out common stop words
    stop_words = {'that', 'this', 'with', 'from', 'they', 'been', 'have', 
                  'were', 'said', 'each', 'which', 'their', 'would', 'there'}
    words = [word for word in words if word not in stop_words]
    
    common = Counter(words).most_common(top_n)
    return [word for word, _ in common]


def extract_text_from_file(file) -> str:
    """
    Extract text content from uploaded files (TXT, PDF, DOCX).
    
    Args:
        file: Flask uploaded file object
        
    Returns:
        Extracted text content
    """
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
    """
    Sanitize filename to prevent directory traversal attacks.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename safe for filesystem operations
    """
    # Remove path components and potentially dangerous characters
    filename = os.path.basename(filename)
    filename = re.sub(r'[^\w\s.-]', '', filename)
    return filename.strip()


def extract_snippet(content: str, max_length: int = 150) -> str:
    """
    Extract a meaningful snippet from document content.
    
    Args:
        content: Full document content
        max_length: Maximum snippet length
        
    Returns:
        Meaningful snippet from the content
    """
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
