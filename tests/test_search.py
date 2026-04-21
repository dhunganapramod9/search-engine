from services.ingest import IngestService
from services.search import SearchService
from services.storage import StorageService
from tests.helpers import FakeEmbedder


def test_search_returns_ranked_matches(tmp_path):
    storage = StorageService(str(tmp_path / "search.db"))
    embedder = FakeEmbedder()
    ingest = IngestService(
        storage_service=storage,
        embedder=embedder,
        uploads_dir=str(tmp_path / "uploads"),
        max_chunk_size=80,
        chunk_overlap=10,
    )
    search = SearchService(storage_service=storage, embedder=embedder)

    ingest.ingest_document("python.txt", b"python backend flask api project")
    ingest.ingest_document("ml.txt", b"ml model embeddings and ranking")

    results = search.hybrid_search("python backend", limit=2, min_score=-1.0)

    assert results
    assert results[0]["filename"] == "python.txt"
    assert "semantic_score" in results[0]
    assert "lexical_score" in results[0]
