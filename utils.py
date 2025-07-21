import os
import re
from collections import Counter
from PyPDF2 import PdfReader
import docx

def load_documents(folder_path="documents"):
    docs = []
    filenames = []
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    for filename in os.listdir(folder_path):
        path = os.path.join(folder_path, filename)
        if filename.endswith(".txt"):
            with open(path, "r", encoding="utf-8") as f:
                docs.append(f.read())
                filenames.append(filename)
    return docs, filenames

def extract_keywords(docs, top_n=10):
    all_text = " ".join(docs).lower()
    words = re.findall(r'\b[a-z]{4,}\b', all_text)
    common = Counter(words).most_common(top_n)
    return [word for word, _ in common]

def extract_text_from_file(file):
    if file.filename.endswith(".txt"):
        return file.read().decode("utf-8")
    elif file.filename.endswith(".pdf"):
        reader = PdfReader(file)
        return "\n".join([page.extract_text() or "" for page in reader.pages])
    elif file.filename.endswith(".docx"):
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    return ""
import os
import re
from collections import Counter
from PyPDF2 import PdfReader
import docx

# I use this to load all .txt files into memory
def load_documents(folder_path="documents"):
    docs = []
    filenames = []
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    for filename in os.listdir(folder_path):
        path = os.path.join(folder_path, filename)
        if filename.endswith(".txt"):
            with open(path, "r", encoding="utf-8") as f:
                docs.append(f.read())
                filenames.append(filename)
    return docs, filenames

# This function pulls out the top frequent words (4+ letters) as keywords
def extract_keywords(docs, top_n=10):
    all_text = " ".join(docs).lower()
    words = re.findall(r'\b[a-z]{4,}\b', all_text)
    common = Counter(words).most_common(top_n)
    return [word for word, _ in common]

# I created this to extract raw text from PDF, DOCX, or TXT
def extract_text_from_file(file):
    if file.filename.endswith(".txt"):
        return file.read().decode("utf-8")
    elif file.filename.endswith(".pdf"):
        reader = PdfReader(file)
        return "\n".join([page.extract_text() or "" for page in reader.pages])
    elif file.filename.endswith(".docx"):
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    return ""
