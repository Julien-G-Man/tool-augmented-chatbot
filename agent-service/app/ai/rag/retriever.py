"""
RAG Retriever Module

The Retriever orchestrates the RAG pipeline:
1. Take user query
2. Convert to embedding
3. Search vector store for similar documents
4. Return top results to LLM

This is where everything comes together!
"""

from typing import List, Dict, Any
from app.ai.rag.embeddings import EmbeddingProvider
from app.ai.rag.vector_store import VectorStore, StoredDocument
from app.ai.rag.document_processor import DocumentProcessor, DocumentChunk


class RAGRetriever:
    """
    Main RAG interface for retrieving documents.
    
    Usage:
        retriever = RAGRetriever(embeddings_provider, vector_store)
        retriever.add_documents(chunks)
        results = retriever.search("What is the company policy?")
    """
    
    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
    ):
        """
        Initialize RAG retriever.
        
        Args:
            embedding_provider: Provider for converting text to vectors
            vector_store: Storage for vectors and documents
        """
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
    
    def add_documents(self, chunks: List[DocumentChunk]) -> None:
        """
        Add document chunks to the RAG system.
        
        Process:
        1. For each chunk, generate embedding
        2. Create StoredDocument with embedding + metadata
        3. Add to vector store
        
        Args:
            chunks: List of DocumentChunk objects from processor
        """
        print(f"Adding {len(chunks)} chunks to RAG system...")
        
        stored_docs = []
        for i, chunk in enumerate(chunks):
            # Generate embedding for this chunk
            embedding = self.embedding_provider.embed_text(chunk.content)
            
            # Create document for storage
            stored_doc = StoredDocument(
                id=f"{chunk.source_file}_chunk_{chunk.chunk_index}",
                content=chunk.content,
                embedding=embedding,
                metadata={
                    **chunk.metadata,
                    "source_file": chunk.source_file,
                    "chunk_index": chunk.chunk_index,
                }
            )
            stored_docs.append(stored_doc)
            
            if (i + 1) % 10 == 0:
                print(f"  Processed {i + 1}/{len(chunks)} chunks...")
        
        # Add all to vector store
        self.vector_store.add_documents(stored_docs)
        print(f"Successfully added {len(chunks)} chunks!")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for documents related to query.
        
        Process:
        1. Embed the query using same provider as documents
        2. Search vector store for similar embeddings
        3. Retrieve full documents and format results
        
        Args:
            query: User's question or search text
            top_k: Number of results to return
            
        Returns:
            List of dicts with 'content', 'source', 'score', 'metadata'
        """
        # Step 1: Embed the query
        query_embedding = self.embedding_provider.embed_text(query)
        
        # Step 2: Search vector store
        search_results = self.vector_store.search(query_embedding, top_k=top_k)
        
        # Step 3: Format results
        formatted_results = []
        for doc_id, similarity_score in search_results:
            doc = self.vector_store.get_document(doc_id)
            formatted_results.append({
                "content": doc.content,
                "source": doc.metadata.get("source_file", "unknown"),
                "score": similarity_score,
                "metadata": doc.metadata,
            })
        
        return formatted_results
    
    def get_context_string(
        self,
        query: str,
        top_k: int = 5,
        include_source: bool = True
    ) -> str:
        """
        Get search results formatted as context for LLM.
        
        This is what you pass to the LLM as context.
        Format makes it easy for LLM to understand and cite sources.
        
        Args:
            query: User's question
            top_k: Number of results
            include_source: Whether to include source file info
            
        Returns:
            Formatted string ready for LLM context
        """
        results = self.search(query, top_k=top_k)
        
        if not results:
            return "No relevant documents found."
        
        context_parts = ["Retrieved relevant documents:\n"]
        
        for i, result in enumerate(results, 1):
            source_info = f" (Source: {result['source']}, Score: {result['score']:.2f})" if include_source else ""
            context_parts.append(
                f"\n[Document {i}]{source_info}\n{result['content']}\n"
            )
        
        return "".join(context_parts)
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """
        List all indexed documents.
        
        Returns:
            List of document info dicts
        """
        # Prefer vector store native listing if available.
        if not hasattr(self.vector_store, "list_documents"):
            return []

        chunk_rows = self.vector_store.list_documents()
        if not chunk_rows:
            return []

        # Group chunks by source file for a useful, compact CLI output.
        grouped: Dict[str, int] = {}
        for row in chunk_rows:
            source = row.get("source_file", "unknown")
            grouped[source] = grouped.get(source, 0) + 1

        return [
            {"source_file": source, "chunks": count}
            for source, count in sorted(grouped.items(), key=lambda item: item[0].lower())
        ]
    
    def clear(self) -> None:
        """Clear all documents from the system."""
        self.vector_store.clear()
