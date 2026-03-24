"""
RAG Builder Functions

Factory functions to easily construct RAG systems.
Makes it simple to swap implementations without touching application code.

Learning Goal: This is the FACTORY PATTERN - creates objects based on config.
Super useful when you have many implementations of same interface.
"""

from app.ai.rag.embeddings import (
    EmbeddingProvider,
    OpenAIEmbeddings,
    MockEmbeddings,
)
from app.ai.rag.vector_store import (
    VectorStore,
    InMemoryVectorStore,
)
from app.ai.rag.retriever import RAGRetriever


def build_rag_system(
    embedding_provider: str = "mock",
    vector_store: str = "memory",
    **kwargs
) -> RAGRetriever:
    """
    Build a RAG system from configuration.
    
    This is your main entry point for creating RAG systems.
    Just specify which implementations to use!
    
    Args:
        embedding_provider: "mock", "openai", or your own
        vector_store: "memory", "pinecone", "milvus", etc.
        **kwargs: Additional arguments passed to builders
        
    Returns:
        Initialized RAGRetriever ready to use
        
    Example:
        # Quick development setup
        rag = build_rag_system(
            embedding_provider="mock",
            vector_store="memory"
        )
        
        # Production setup (when ready)
        rag = build_rag_system(
            embedding_provider="openai",
            vector_store="pinecone",
            pinecone_index="company-docs"
        )
    """
    
    embedding = _build_embedding_provider(embedding_provider, **kwargs)
    
    vector_store_obj = _build_vector_store(vector_store, **kwargs)
    
    # Combine into RAG system
    retriever = RAGRetriever(embedding, vector_store_obj)
    
    return retriever


def _build_embedding_provider(
    provider_type: str,
    **kwargs
) -> EmbeddingProvider:
    """
    Create embedding provider based on type.
    
    Args:
        provider_type: Type of provider to create
        **kwargs: Config for specific provider
        
    Returns:
        EmbeddingProvider instance
    """
    
    if provider_type == "openai":
        model = kwargs.get("embedding_model", "text-embedding-3-small")
        return OpenAIEmbeddings(model=model)
    
    elif provider_type == "mock":
        dimension = kwargs.get("dimension", 384)
        return MockEmbeddings(dimension=dimension)
    
    # We'll add more providers here as needed!
    # elif provider_type == "ollama":
    #     return OllamaEmbeddings(**kwargs)
    # elif provider_type == "huggingface":
    #     return HuggingFaceEmbeddings(**kwargs)
    
    else:
        raise ValueError(f"Unknown embedding provider: {provider_type}")


def _build_vector_store(
    store_type: str,
    **kwargs
) -> VectorStore:
    """
    Create vector store based on type.
    
    Args:
        store_type: Type of store to create
        **kwargs: Config for specific store
        
    Returns:
        VectorStore instance
    """
    
    if store_type == "memory":
        persistence_path = kwargs.get("persistence_path")
        return InMemoryVectorStore(persistence_path=persistence_path)
    
    # We'll add more stores here as needed!
    # elif store_type == "pinecone":
    #     api_key = kwargs.get("pinecone_api_key")
    #     index = kwargs.get("pinecone_index")
    #     return PineconeVectorStore(api_key, index)
    # elif store_type == "milvus":
    #     host = kwargs.get("milvus_host", "localhost")
    #     port = kwargs.get("milvus_port", 19530)
    #     return MilvusVectorStore(host, port)
    # elif store_type == "weaviate":
    #     url = kwargs.get("weaviate_url")
    #     return WeaviateVectorStore(url)
    
    else:
        raise ValueError(f"Unknown vector store: {store_type}")
