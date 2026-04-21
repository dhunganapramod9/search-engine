import json
from collections import Counter
from functools import lru_cache
from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer

from utils.text_processing import snippet_for_chunk


class SentenceTransformerEmbedder:
    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)

    def encode(self, texts: List[str]) -> np.ndarray:
        return np.array(self.model.encode(texts, convert_to_numpy=True))


class SearchService:
    def __init__(self, storage_service, embedder):
        self.storage_service = storage_service
        self.embedder = embedder

    @staticmethod
    def _cosine_similarity(query_vector: np.ndarray, vectors: np.ndarray) -> np.ndarray:
        query_norm = np.linalg.norm(query_vector) + 1e-12
        vectors_norm = np.linalg.norm(vectors, axis=1) + 1e-12
        return np.dot(vectors, query_vector) / (vectors_norm * query_norm)

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        return [token for token in text.lower().split() if token]

    def _lexical_scores(self, query: str, chunks: List[dict]) -> np.ndarray:
        query_terms = self._tokenize(query)
        if not query_terms:
            return np.zeros(len(chunks), dtype=np.float32)
        query_counter = Counter(query_terms)
        scores = []
        for chunk in chunks:
            chunk_terms = Counter(self._tokenize(chunk["chunk_text"]))
            overlap = sum(min(chunk_terms[term], query_counter[term]) for term in query_counter)
            scores.append(float(overlap) / (len(query_terms) + 1e-12))
        return np.array(scores, dtype=np.float32)

    @lru_cache(maxsize=128)
    def _cached_query_embedding(self, query: str) -> np.ndarray:
        return self.embedder.encode([query])[0]

    def hybrid_search(
        self,
        query: str,
        limit: int = 10,
        min_score: float = 0.1,
        semantic_weight: float = 0.75,
        lexical_weight: float = 0.25,
        rerank_top_k: int = 30,
    ) -> List[dict]:
        chunks = self.storage_service.get_all_chunks()
        if not chunks:
            return []

        query_vector = self._cached_query_embedding(query)
        chunk_vectors = np.array([json.loads(item["embedding"]) for item in chunks], dtype=np.float32)
        semantic_scores = self._cosine_similarity(query_vector, chunk_vectors)
        lexical_scores = self._lexical_scores(query, chunks)
        combined_scores = (semantic_scores * semantic_weight) + (lexical_scores * lexical_weight)

        ranked = sorted(
            zip(chunks, combined_scores, semantic_scores, lexical_scores),
            key=lambda item: float(item[1]),
            reverse=True,
        )[:rerank_top_k]
        reranked = sorted(
            ranked,
            key=lambda item: float(item[1]),
            reverse=True,
        )

        results = []
        for chunk, score, semantic_score, lexical_score in reranked:
            if float(score) < min_score:
                continue
            results.append(
                {
                    "document_id": chunk["document_id"],
                    "filename": chunk["filename"],
                    "chunk_index": chunk["chunk_index"],
                    "score": round(float(score), 4),
                    "semantic_score": round(float(semantic_score), 4),
                    "lexical_score": round(float(lexical_score), 4),
                    "snippet": snippet_for_chunk(chunk["chunk_text"]),
                }
            )
            if len(results) >= limit:
                break
        return results

    def semantic_search(self, query: str, limit: int = 10, min_score: float = 0.1) -> List[dict]:
        return self.hybrid_search(query=query, limit=limit, min_score=min_score)
