import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

from utils.files import extract_text_from_bytes, sanitize_filename
from utils.text_processing import chunk_text, normalize_text


class IngestService:
    def __init__(self, storage_service, embedder, uploads_dir: str, max_chunk_size: int, chunk_overlap: int):
        self.storage_service = storage_service
        self.embedder = embedder
        self.uploads_dir = Path(uploads_dir)
        self.max_chunk_size = max_chunk_size
        self.chunk_overlap = chunk_overlap
        self.uploads_dir.mkdir(parents=True, exist_ok=True)

    def ingest_document(self, filename: str, payload: bytes) -> Dict:
        clean_name = sanitize_filename(filename)
        if not clean_name:
            raise ValueError("Invalid filename.")

        content = normalize_text(extract_text_from_bytes(clean_name, payload))
        if not content:
            raise ValueError("Uploaded file does not contain extractable text.")

        file_path = self.uploads_dir / clean_name
        file_path.write_bytes(payload)

        uploaded_at = datetime.now(timezone.utc).isoformat()
        document_id = self.storage_service.insert_document(clean_name, content, uploaded_at)

        chunks = chunk_text(content, max_chunk_size=self.max_chunk_size, overlap=self.chunk_overlap)
        if not chunks:
            raise ValueError("Document text is too short to index.")

        vectors = self.embedder.encode(chunks)
        self.storage_service.insert_chunks(
            document_id,
            [
                {
                    "chunk_index": index,
                    "chunk_text": chunk,
                    "embedding": json.dumps(vector.tolist()),
                }
                for index, (chunk, vector) in enumerate(zip(chunks, vectors))
            ],
        )

        return {
            "document_id": document_id,
            "filename": clean_name,
            "chunks_indexed": len(chunks),
            "uploaded_at": uploaded_at,
        }
