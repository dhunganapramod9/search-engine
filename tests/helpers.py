import numpy as np


class FakeEmbedder:
    """Deterministic low-dimensional embedder for fast tests."""

    def encode(self, texts):
        vectors = []
        for text in texts:
            lower = text.lower()
            vectors.append(
                [
                    lower.count("python") + lower.count("backend"),
                    lower.count("ml") + lower.count("model"),
                    len(lower.split()) / 100.0,
                ]
            )
        return np.array(vectors, dtype=np.float32)
