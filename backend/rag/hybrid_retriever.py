"""
FinVerse AI — Hybrid Retriever
Combines BM25 keyword search + FAISS vector search + Cross-encoder reranking.
Implements the full Agentic RAG pipeline with multi-level fallback.
"""

import logging
import math
from typing import Optional
from collections import Counter

logger = logging.getLogger(__name__)


class BM25Retriever:
    """Simple BM25 retriever for keyword-based search."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self._documents = []
        self._doc_freqs = Counter()
        self._doc_lens = []
        self._avg_dl = 0
        self._tokenized_docs = []

    def add_documents(self, documents: list[dict]):
        """Index documents for BM25 search."""
        for doc in documents:
            tokens = self._tokenize(doc["text"])
            self._tokenized_docs.append(tokens)
            self._documents.append(doc)
            self._doc_freqs.update(set(tokens))

        total_len = sum(len(t) for t in self._tokenized_docs)
        self._avg_dl = total_len / len(self._tokenized_docs) if self._tokenized_docs else 0
        self._doc_lens = [len(t) for t in self._tokenized_docs]

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """Search using BM25 scoring."""
        if not self._documents:
            return []

        query_tokens = self._tokenize(query)
        scores = []
        n = len(self._documents)

        for i, doc_tokens in enumerate(self._tokenized_docs):
            score = 0
            doc_len = self._doc_lens[i]
            token_freq = Counter(doc_tokens)

            for qt in query_tokens:
                if qt not in token_freq:
                    continue

                tf = token_freq[qt]
                df = self._doc_freqs.get(qt, 0)
                idf = math.log((n - df + 0.5) / (df + 0.5) + 1)

                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * doc_len / self._avg_dl)
                score += idf * numerator / denominator

            scores.append((score, i))

        scores.sort(reverse=True)
        results = []
        for score, idx in scores[:top_k]:
            if score > 0:
                doc = self._documents[idx]
                results.append({
                    "text": doc["text"],
                    "metadata": doc.get("metadata", {}),
                    "score": float(score),
                    "retriever": "bm25",
                })

        return results

    def _tokenize(self, text: str) -> list[str]:
        """Simple whitespace + lowercase tokenization."""
        import re
        text = text.lower()
        tokens = re.findall(r'\b\w+\b', text)
        return tokens


class CrossEncoderReranker:
    """Reranks retrieval results using a cross-encoder model."""

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        self._model = None

    @property
    def model(self):
        if self._model is None:
            try:
                from sentence_transformers import CrossEncoder
                self._model = CrossEncoder(self.model_name)
                logger.info(f"✅ Loaded reranker: {self.model_name}")
            except ImportError:
                logger.warning("sentence-transformers not installed, reranking disabled")
        return self._model

    def rerank(self, query: str, documents: list[dict], top_k: int = 5) -> list[dict]:
        """Rerank documents using cross-encoder scores."""
        if not documents or self.model is None:
            return documents[:top_k]

        pairs = [(query, doc["text"]) for doc in documents]
        scores = self.model.predict(pairs)

        for i, doc in enumerate(documents):
            doc["rerank_score"] = float(scores[i])

        reranked = sorted(documents, key=lambda x: x.get("rerank_score", 0), reverse=True)
        return reranked[:top_k]


class HybridRetriever:
    """
    Combines vector search + BM25 + cross-encoder reranking.
    Implements multi-level retrieval fallback.
    """

    def __init__(self, vector_store, bm25_retriever: Optional[BM25Retriever] = None,
                 reranker: Optional[CrossEncoderReranker] = None):
        self.vector_store = vector_store
        self.bm25 = bm25_retriever or BM25Retriever()
        self.reranker = reranker

    def retrieve(self, query: str, top_k: int = 5) -> dict:
        """
        Hybrid retrieval with multi-level fallback:
        1. Vector search (primary)
        2. BM25 search (secondary)
        3. Merge & deduplicate
        4. Rerank with cross-encoder (if available)

        If primary fails → use secondary only.
        If both fail → return empty with notification.
        """
        vector_results = []
        bm25_results = []
        retrieval_method = []

        # Level 1: Vector search
        try:
            vector_results = self.vector_store.search(query, top_k=top_k * 2)
            if vector_results:
                retrieval_method.append("vector")
        except Exception as e:
            logger.warning(f"Vector search failed: {e}")

        # Level 2: BM25 search
        try:
            bm25_results = self.bm25.search(query, top_k=top_k * 2)
            if bm25_results:
                retrieval_method.append("bm25")
        except Exception as e:
            logger.warning(f"BM25 search failed: {e}")

        # Merge results
        merged = self._merge_results(vector_results, bm25_results)

        if not merged:
            return {
                "results": [],
                "method": "none",
                "message": "No relevant documents found. Please try a different query or upload relevant documents.",
            }

        # Level 3: Rerank
        if self.reranker and len(merged) > 1:
            try:
                merged = self.reranker.rerank(query, merged, top_k=top_k)
                retrieval_method.append("reranked")
            except Exception as e:
                logger.warning(f"Reranking failed: {e}")

        return {
            "results": merged[:top_k],
            "method": "+".join(retrieval_method),
            "total_candidates": len(vector_results) + len(bm25_results),
        }

    def _merge_results(self, vector_results: list, bm25_results: list) -> list:
        """Merge and deduplicate results from both retrievers."""
        seen_texts = set()
        merged = []

        # Interleave results giving priority to vector search
        for result in vector_results:
            text_key = result["text"][:100]
            if text_key not in seen_texts:
                seen_texts.add(text_key)
                result["retriever"] = result.get("retriever", "vector")
                merged.append(result)

        for result in bm25_results:
            text_key = result["text"][:100]
            if text_key not in seen_texts:
                seen_texts.add(text_key)
                merged.append(result)

        return merged
