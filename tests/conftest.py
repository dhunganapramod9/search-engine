import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app import create_app
from config import Config
from tests.helpers import FakeEmbedder


@dataclass
class TestConfig(Config):
    model_name: str = "fake-model"


@pytest.fixture()
def app(tmp_path):
    config = TestConfig(
        database_path=str(tmp_path / "test.db"),
        uploads_dir=str(tmp_path / "uploads"),
        max_chunk_size=50,
        chunk_overlap=10,
        max_search_results=5,
        min_similarity_score=-1.0,
    )
    return create_app(config=config, embedder=FakeEmbedder())


@pytest.fixture()
def client(app):
    return app.test_client()

