import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    """Application configuration loaded from environment variables."""

    app_name: str = "semantic-search-engine"
    model_name: str = os.getenv("MODEL_NAME", "all-MiniLM-L6-v2")
    database_path: str = os.getenv("DATABASE_PATH", "data/search_engine.db")
    uploads_dir: str = os.getenv("UPLOADS_DIR", "uploads")
    max_content_length: int = int(os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))
    max_chunk_size: int = int(os.getenv("MAX_CHUNK_SIZE", 450))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", 70))
    max_search_results: int = int(os.getenv("MAX_SEARCH_RESULTS", 10))
    min_similarity_score: float = float(os.getenv("MIN_SIMILARITY_SCORE", 0.1))
    hybrid_semantic_weight: float = float(os.getenv("HYBRID_SEMANTIC_WEIGHT", 0.75))
    hybrid_lexical_weight: float = float(os.getenv("HYBRID_LEXICAL_WEIGHT", 0.25))
    rerank_top_k: int = int(os.getenv("RERANK_TOP_K", 30))
    ingestion_workers: int = int(os.getenv("INGESTION_WORKERS", 2))
    flask_debug: bool = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    port: int = int(os.getenv("PORT", 5000))

    def ensure_runtime_dirs(self) -> None:
        """Create required runtime directories if missing."""
        Path(self.uploads_dir).mkdir(parents=True, exist_ok=True)
        Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
