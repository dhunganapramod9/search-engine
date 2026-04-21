import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Dict, Optional
from uuid import uuid4


class JobService:
    """Asynchronous ingestion jobs with persistent status tracking."""

    def __init__(self, storage_service, ingest_service, max_workers: int = 2):
        self.storage_service = storage_service
        self.ingest_service = ingest_service
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    def create_ingestion_job(self, filename: str, payload: bytes) -> Dict:
        created_at = self._now_iso()
        job_id = str(uuid4())
        job = {
            "id": job_id,
            "filename": filename,
            "status": "queued",
            "document_id": None,
            "error_message": None,
            "created_at": created_at,
            "updated_at": created_at,
        }
        self.storage_service.insert_job(job)
        self.executor.submit(self._run_ingestion_job, job_id, filename, payload)
        return job

    def _run_ingestion_job(self, job_id: str, filename: str, payload: bytes) -> None:
        self.storage_service.update_job(job_id=job_id, status="processing", updated_at=self._now_iso())
        try:
            result = self.ingest_service.ingest_document(filename, payload)
            self.storage_service.update_job(
                job_id=job_id,
                status="completed",
                updated_at=self._now_iso(),
                document_id=result["document_id"],
            )
        except Exception as exc:
            logging.exception("Ingestion job failed")
            self.storage_service.update_job(
                job_id=job_id,
                status="failed",
                updated_at=self._now_iso(),
                error_message=str(exc),
            )

    def get_job(self, job_id: str) -> Optional[Dict]:
        return self.storage_service.get_job(job_id)
