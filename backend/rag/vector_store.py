"""
FinVerse AI — FAISS Vector Store
Semantic vector search using sentence-transformers + FAISS.
"""

import os
import json
import logging
import numpy as np
from typing import Optional

logger = logging.getLogger(__name__)


class VectorStore:
    """
    FAISS-based vector store for RAG retrieval.
    Uses sentence-transformers for embedding generation.
    """

    def __init__(self, index_dir: str = "./data/faiss_index", model_name: str = "all-MiniLM-L6-v2"):
        self.index_dir = index_dir
        self.model_name = model_name
        self._model = None
        self._index = None
        self._documents = []  # Store document texts and metadata
        self._metadata_path = os.path.join(index_dir, "metadata.json")
        self._index_path = os.path.join(index_dir, "index.faiss")

    @property
    def model(self):
        """Lazy-load the embedding model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
                logger.info(f"✅ Loaded embedding model: {self.model_name}")
            except ImportError:
                logger.error("sentence-transformers not installed!")
                raise
        return self._model

    def embed(self, texts: list[str]) -> np.ndarray:
        """Generate embeddings for a list of texts."""
        return self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)

    def add_documents(self, documents: list[dict]):
        """
        Add documents to the vector store.
        Each document: {text: str, metadata: dict}
        """
        import faiss

        if not documents:
            return

        texts = [doc["text"] for doc in documents]
        embeddings = self.embed(texts)

        dim = embeddings.shape[1]

        if self._index is None:
            self._index = faiss.IndexFlatIP(dim)  # Inner product (cosine sim for normalized vecs)

        self._index.add(embeddings.astype(np.float32))
        self._documents.extend(documents)

        logger.info(f"📥 Added {len(documents)} documents. Total: {len(self._documents)}")

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """
        Search for similar documents.
        Returns top-k results with scores.
        """
        if self._index is None or len(self._documents) == 0:
            logger.warning("Vector store is empty")
            return []

        query_embedding = self.embed([query]).astype(np.float32)
        scores, indices = self._index.search(query_embedding, min(top_k, len(self._documents)))

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self._documents) and idx >= 0:
                doc = self._documents[idx]
                results.append({
                    "text": doc["text"],
                    "metadata": doc.get("metadata", {}),
                    "score": float(score),
                })

        return results

    def save(self):
        """Persist index and metadata to disk."""
        import faiss

        os.makedirs(self.index_dir, exist_ok=True)

        if self._index is not None:
            faiss.write_index(self._index, self._index_path)

        with open(self._metadata_path, "w", encoding="utf-8") as f:
            json.dump(self._documents, f, ensure_ascii=False, indent=2)

        logger.info(f"💾 Saved vector store: {len(self._documents)} documents")

    def load(self):
        """Load index and metadata from disk."""
        import faiss

        if os.path.exists(self._index_path) and os.path.exists(self._metadata_path):
            self._index = faiss.read_index(self._index_path)
            with open(self._metadata_path, "r", encoding="utf-8") as f:
                self._documents = json.load(f)
            logger.info(f"📂 Loaded vector store: {len(self._documents)} documents")
        else:
            logger.info("No existing index found, starting fresh")

    @property
    def document_count(self) -> int:
        return len(self._documents)
