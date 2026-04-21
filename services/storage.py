import sqlite3
from contextlib import contextmanager
from typing import Dict, Generator, List, Optional


class StorageService:
    """SQLite-backed persistence for documents and chunk metadata."""

    def __init__(self, database_path: str):
        self.database_path = database_path
        self._init_db()

    @contextmanager
    def _connection(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self._connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    content TEXT NOT NULL,
                    uploaded_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    status TEXT NOT NULL,
                    document_id INTEGER,
                    error_message TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id INTEGER NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    chunk_text TEXT NOT NULL,
                    embedding TEXT NOT NULL,
                    FOREIGN KEY(document_id) REFERENCES documents(id)
                )
                """
            )

    def insert_document(self, filename: str, content: str, uploaded_at: str) -> int:
        with self._connection() as conn:
            cur = conn.execute(
                "INSERT INTO documents (filename, content, uploaded_at) VALUES (?, ?, ?)",
                (filename, content, uploaded_at),
            )
            return int(cur.lastrowid)

    def insert_chunks(self, document_id: int, chunks_with_embeddings: List[Dict[str, str]]) -> None:
        with self._connection() as conn:
            conn.executemany(
                """
                INSERT INTO chunks (document_id, chunk_index, chunk_text, embedding)
                VALUES (?, ?, ?, ?)
                """,
                [
                    (
                        document_id,
                        item["chunk_index"],
                        item["chunk_text"],
                        item["embedding"],
                    )
                    for item in chunks_with_embeddings
                ],
            )

    def get_document(self, document_id: int) -> Optional[Dict]:
        with self._connection() as conn:
            row = conn.execute("SELECT * FROM documents WHERE id = ?", (document_id,)).fetchone()
            return dict(row) if row else None

    def get_all_chunks(self) -> List[Dict]:
        with self._connection() as conn:
            rows = conn.execute(
                """
                SELECT c.id, c.document_id, c.chunk_index, c.chunk_text, c.embedding, d.filename
                FROM chunks c
                JOIN documents d ON c.document_id = d.id
                """
            ).fetchall()
            return [dict(row) for row in rows]

    def insert_job(self, job: Dict) -> None:
        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO jobs (id, filename, status, document_id, error_message, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job["id"],
                    job["filename"],
                    job["status"],
                    job.get("document_id"),
                    job.get("error_message"),
                    job["created_at"],
                    job["updated_at"],
                ),
            )

    def update_job(
        self,
        job_id: str,
        status: str,
        updated_at: str,
        document_id: Optional[int] = None,
        error_message: Optional[str] = None,
    ) -> None:
        with self._connection() as conn:
            conn.execute(
                """
                UPDATE jobs
                SET status = ?, updated_at = ?, document_id = COALESCE(?, document_id), error_message = ?
                WHERE id = ?
                """,
                (status, updated_at, document_id, error_message, job_id),
            )

    def get_job(self, job_id: str) -> Optional[Dict]:
        with self._connection() as conn:
            row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
            return dict(row) if row else None
