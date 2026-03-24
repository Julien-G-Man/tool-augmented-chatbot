"""
Vector Store Abstraction Layer

This module defines a common interface for different vector databases.
Swap between Pinecone, Milvus, Weaviate, SQLite with pgvector, etc.
without changing higher-level code.

Learning Goal: Vector stores are just key-value stores where keys are
high-dimensional vectors. Search finds "closest" vectors by distance.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Any, Optional
from dataclasses import dataclass
import json
from pathlib import Path


@dataclass
class StoredDocument:
    """Represents a document chunk in the vector store."""
    id: str                    # Unique identifier
    content: str              # The actual text
    embedding: List[float]    # Vector representation
    metadata: Dict[str, Any]  # Source file, page number, etc.


class VectorStore(ABC):
    """
    Abstract base class for vector stores.
    
    A vector store:
    1. Stores embeddings (vectors) with associated documents
    2. Supports similarity search: "Find vectors closest to this query"
    3. Uses distance metrics (cosine, euclidean, etc.)
    """
    
    @abstractmethod
    def add_documents(self, documents: List[StoredDocument]) -> None:
        """
        Add documents with their embeddings to the store.
        
        Args:
            documents: List of StoredDocument objects with embeddings
        """
        pass
    
    @abstractmethod
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Find most similar documents to query embedding.
        
        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            
        Returns:
            List of (document_id, similarity_score) tuples
            Higher score = more similar (typically 0-1)
        """
        pass
    
    @abstractmethod
    def get_document(self, doc_id: str) -> StoredDocument:
        """Retrieve a document by ID."""
        pass
    
    @abstractmethod
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document from the store."""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all documents from the store."""
        pass


class InMemoryVectorStore(VectorStore):
    """
    Simple In-Memory Vector Store
    
    Stores everything in RAM using cosine similarity.
    Perfect for dev/testing, small datasets, or single-machine deployments.
    
    Why In-Memory?
    - Simple, no dependencies
    - Fast for small datasets (<100K docs)
    - Easy to understand and debug
    
    Limitation: Everything lost on restart (no persistence)
    """
    
    def __init__(self, persistence_path: Optional[str] = None):
        self.documents: Dict[str, StoredDocument] = {}
        self.embeddings: List[List[float]] = []
        self.ids: List[str] = []
        self.persistence_path = Path(persistence_path) if persistence_path else None
        if self.persistence_path and self.persistence_path.exists():
            self._load_from_disk()
    
    def add_documents(self, documents: List[StoredDocument]) -> None:
        """Add documents to in-memory store."""
        for doc in documents:
            # Upsert behavior: replace existing doc in-place if id already exists.
            if doc.id in self.documents:
                idx = self.ids.index(doc.id)
                self.documents[doc.id] = doc
                self.embeddings[idx] = doc.embedding
            else:
                self.documents[doc.id] = doc
                self.embeddings.append(doc.embedding)
                self.ids.append(doc.id)
        self._persist_to_disk()
    
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Search using cosine similarity.
        
        Cosine similarity = dot product / (magnitude1 * magnitude2)
        Ranges from -1 to 1 (we normalize to 0-1)
        Higher = more similar
        """
        if not self.embeddings:
            return []
        
        # Calculate cosine similarity with all documents
        similarities = []
        for i, embedding in enumerate(self.embeddings):
            sim = self._cosine_similarity(query_embedding, embedding)
            similarities.append((self.ids[i], sim))
        
        # Sort by similarity (highest first) and return top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        This is the most common distance metric for embeddings.
        """
        import math
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        
        # Magnitudes
        mag1 = math.sqrt(sum(a ** 2 for a in vec1))
        mag2 = math.sqrt(sum(b ** 2 for b in vec2))
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        # Similarity (0 to 1)
        return (dot_product / (mag1 * mag2) + 1) / 2
    
    def get_document(self, doc_id: str) -> StoredDocument:
        """Retrieve document by ID."""
        if doc_id not in self.documents:
            raise ValueError(f"Document {doc_id} not found")
        return self.documents[doc_id]
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete document by ID."""
        if doc_id not in self.documents:
            return False
        
        del self.documents[doc_id]
        idx = self.ids.index(doc_id)
        self.ids.pop(idx)
        self.embeddings.pop(idx)
        self._persist_to_disk()
        return True
    
    def clear(self) -> None:
        """Clear all documents."""
        self.documents.clear()
        self.embeddings.clear()
        self.ids.clear()
        self._persist_to_disk()
    
    def count(self) -> int:
        """Return number of documents in store."""
        return len(self.documents)

    def list_documents(self) -> List[Dict[str, Any]]:
        """Return lightweight metadata for all indexed chunks."""
        items = []
        for doc_id in self.ids:
            doc = self.documents[doc_id]
            items.append(
                {
                    "id": doc.id,
                    "source_file": doc.metadata.get("source_file", "unknown"),
                    "chunk_index": doc.metadata.get("chunk_index"),
                }
            )
        return items

    def _persist_to_disk(self) -> None:
        if not self.persistence_path:
            return

        self.persistence_path.parent.mkdir(parents=True, exist_ok=True)
        serializable_docs = []
        for doc_id in self.ids:
            doc = self.documents[doc_id]
            serializable_docs.append(
                {
                    "id": doc.id,
                    "content": doc.content,
                    "embedding": doc.embedding,
                    "metadata": doc.metadata,
                }
            )

        with self.persistence_path.open("w", encoding="utf-8") as f:
            json.dump(serializable_docs, f)

    def _load_from_disk(self) -> None:
        try:
            with self.persistence_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            return

        self.documents.clear()
        self.embeddings.clear()
        self.ids.clear()

        for item in data:
            doc = StoredDocument(
                id=item["id"],
                content=item["content"],
                embedding=item["embedding"],
                metadata=item.get("metadata", {}),
            )
            self.documents[doc.id] = doc
            self.ids.append(doc.id)
            self.embeddings.append(doc.embedding)
