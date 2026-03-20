"""
Embedding Provider Abstraction Layer

This module defines a common interface for different embedding providers.
This allows you to swap OpenAI, Ollama, HuggingFace, or other providers
without changing downstream code.

Learning Goal: Abstract interfaces let you change implementations easily!
"""

from abc import ABC, abstractmethod
from typing import List
import os


class EmbeddingProvider(ABC):
    """
    Abstract base class for embedding providers.
    
    Any embedding provider must implement the embed_text method.
    This ensures consistent interface regardless of underlying provider.
    """
    
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """
        Convert text to embedding vector.
        
        Args:
            text: The text to embed
            
        Returns:
            List of floats representing the embedding
            
        Raises:
            Exception: If embedding fails
        """
        pass
    
    @abstractmethod
    def get_embedding_dimension(self) -> int:
        """Returns the dimension of embeddings (e.g., 1536 for OpenAI)"""
        pass


class OpenAIEmbeddings(EmbeddingProvider):
    """
    OpenAI Embedding Provider
    
    Uses OpenAI's embedding API. Requires OPENAI_API_KEY in environment.
    Currently a placeholder - will be fully implemented when OpenAI package is available.
    
    Why OpenAI? Fast, accurate, widely used. But replaceable with competitors.
    """
    
    def __init__(self, model: str = "text-embedding-3-small"):
        """
        Initialize OpenAI embeddings.
        
        Args:
            model: OpenAI embedding model to use
                - text-embedding-3-small: 1536 dimensions, cheaper
                - text-embedding-3-large: 3072 dimensions, more accurate
        """
        self.model = model
        self.dimension = 1536 if model == "text-embedding-3-small" else 3072
        
        # Placeholder for now - in real usage would initialize client
        self.client = None
    
    def embed_text(self, text: str) -> List[float]:
        """
        Embed text using OpenAI API.
        
        In production, this would call the OpenAI API.
        For now, returns a dummy embedding for demonstration.
        """
        # TODO: Implement actual OpenAI API call
        # from openai import OpenAI
        # client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        # response = client.embeddings.create(input=text, model=self.model)
        # return response.data[0].embedding
        
        # Dummy implementation
        return [0.0] * self.dimension
    
    def get_embedding_dimension(self) -> int:
        return self.dimension


class MockEmbeddings(EmbeddingProvider):
    """
    Mock Embedding Provider for Testing
    
    Returns random embeddings. Useful for development/testing
    when you don't want to use real APIs yet.
    """
    
    def __init__(self, dimension: int = 384):
        """
        Initialize mock embeddings.
        
        Args:
            dimension: Size of embedding vectors to generate
        """
        self.dimension = dimension
    
    def embed_text(self, text: str) -> List[float]:
        """Return deterministic mock embedding based on text hash."""
        import hashlib
        
        # Create reproducible embeddings based on text
        hash_obj = hashlib.md5(text.encode())
        hash_int = int(hash_obj.hexdigest(), 16)
        
        # Generate embeddings from hash
        embeddings = []
        for i in range(self.dimension):
            # Use hash to generate values between -1 and 1
            val = ((hash_int + i) % 200 - 100) / 100.0
            embeddings.append(val)
        
        return embeddings
    
    def get_embedding_dimension(self) -> int:
        return self.dimension
