import io
import re
from pathlib import Path
from typing import Set

import docx
from PyPDF2 import PdfReader

ALLOWED_EXTENSIONS: Set[str] = {".txt", ".pdf", ".docx"}


def sanitize_filename(filename: str) -> str:
    clean_name = Path(filename).name
    clean_name = re.sub(r"[^\w\s.-]", "", clean_name)
    return clean_name.strip()


def is_allowed_extension(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def extract_text_from_bytes(filename: str, payload: bytes) -> str:
    extension = Path(filename).suffix.lower()
    if extension == ".txt":
        return payload.decode("utf-8", errors="ignore")
    if extension == ".pdf":
        reader = PdfReader(io.BytesIO(payload))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if extension == ".docx":
        document = docx.Document(io.BytesIO(payload))
        return "\n".join(paragraph.text for paragraph in document.paragraphs if paragraph.text.strip())
    raise ValueError("Unsupported file extension")
