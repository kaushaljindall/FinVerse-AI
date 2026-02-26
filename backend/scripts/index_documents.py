import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config.settings import settings
from backend.rag.document_processor import DocumentProcessor
from backend.rag.vector_store import VectorStore
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("🚀 Indexing compliance documents...")
    
    docs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "compliance_docs")
    
    # 1. Process documents
    processor = DocumentProcessor(chunk_size=1000, chunk_overlap=100)
    chunks = processor.process_directory(docs_dir)
    
    if not chunks:
        logger.warning("⚠️ No documents found to index.")
        return
        
    logger.info(f"✅ Extracted {len(chunks)} chunks from documents.")
    
    # 2. Build vector store
    store = VectorStore(
        index_dir=settings.FAISS_INDEX_DIR,
        model_name=settings.EMBEDDING_MODEL
    )
    
    # Generate embeddings and add to index
    logger.info("Generating embeddings and building FAISS index...")
    store.add_documents(chunks)
    
    # Save to disk
    store.save()
    logger.info("✅ FAISS index successfully built and saved!")

if __name__ == "__main__":
    main()
