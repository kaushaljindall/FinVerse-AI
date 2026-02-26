"""
FinVerse AI — RAG Retrieval Agent
Retrieves relevant clauses from financial policies, compliance docs, loan agreements.
Provides citation-based responses.
"""

import logging
from backend.agents.base_agent import BaseAgent
from backend.models.agent_response import AvatarState

logger = logging.getLogger(__name__)


class RAGAgent(BaseAgent):
    """
    Agent 5: RAG Retrieval
    - Retrieves from vector database
    - Uses hybrid retrieval (BM25 + semantic)
    - Reranks results
    - Provides citation-based responses
    """

    def __init__(self, llm_provider=None, retriever=None):
        super().__init__(
            name="rag_agent",
            description="Retrieves and synthesizes information from financial documents",
            llm_provider=llm_provider,
        )
        self.retriever = retriever

    async def execute(self, state: dict) -> dict:
        """Retrieve relevant documents and generate grounded response."""
        query = state.get("query", "")

        self.emit_event("thinking", {
            "message": "Searching knowledge base for relevant documents..."
        }, AvatarState.SEARCHING)

        # Retrieve documents
        retrieval_result = {"results": [], "method": "none"}
        citations = []

        if self.retriever:
            self.emit_event("tool_call", {
                "tool": "hybrid_retriever",
                "action": "search",
                "query": query,
            }, AvatarState.SEARCHING)

            retrieval_result = self.retriever.retrieve(query, top_k=5)

            self.emit_event("tool_call", {
                "tool": "hybrid_retriever",
                "action": "results",
                "method": retrieval_result.get("method", "none"),
                "results_count": len(retrieval_result.get("results", [])),
            }, AvatarState.ANALYZING)

        results = retrieval_result.get("results", [])

        if results:
            # Build context from retrieved documents
            context_parts = []
            for i, doc in enumerate(results):
                source = doc.get("metadata", {}).get("source", f"Document {i+1}")
                citations.append(source)
                context_parts.append(f"[Source: {source}]\n{doc['text']}")

            context = "\n\n---\n\n".join(context_parts)

            system_prompt = """You are the RAG Retrieval Agent for FinVerse AI.
Your role is to:
1. Answer questions using ONLY the provided document context
2. Cite your sources using [Source: filename] format
3. If the context doesn't contain relevant information, say so clearly
4. Never fabricate information not found in the documents
5. Provide structured, clear responses"""

            prompt = f"""User Query: {query}

Retrieved Documents:
{context}

Answer the query using the above documents. Cite your sources."""

            analysis = await self.think(prompt, system_prompt)
        else:
            analysis = "No relevant documents found in the knowledge base. Please upload relevant financial documents or try a different query."

            self.emit_event("result", {
                "message": "No documents found",
                "suggestion": "Upload compliance documents, loan agreements, or policy PDFs to enable RAG-powered responses."
            }, AvatarState.IDLE)

        self.emit_event("result", {
            "agent": self.name,
            "analysis": analysis,
            "documents_retrieved": len(results),
            "retrieval_method": retrieval_result.get("method", "none"),
            "citations": citations,
        }, AvatarState.RECOMMENDING)

        state["rag_analysis"] = analysis
        state["citations"] = citations
        state["agents_used"] = state.get("agents_used", []) + [self.name]
        state["events"] = state.get("events", []) + self.get_events()
        return state
