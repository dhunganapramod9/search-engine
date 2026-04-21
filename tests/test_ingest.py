from services.ingest import IngestService
from services.storage import StorageService
from tests.helpers import FakeEmbedder


def test_ingest_persists_document_and_chunks(tmp_path):
    storage = StorageService(str(tmp_path / "ingest.db"))
    ingest = IngestService(
        storage_service=storage,
        embedder=FakeEmbedder(),
        uploads_dir=str(tmp_path / "uploads"),
        max_chunk_size=4,
        chunk_overlap=1,
    )

    result = ingest.ingest_document("notes.txt", b"python backend api search engine")
    document = storage.get_document(result["document_id"])
    chunks = storage.get_all_chunks()

    assert result["chunks_indexed"] > 0
    assert document is not None
    assert document["filename"] == "notes.txt"
    assert len(chunks) == result["chunks_indexed"]
