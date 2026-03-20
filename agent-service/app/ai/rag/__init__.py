"""
RAG (Retrieval-Augmented Generation) Module

This module provides document retrieval capabilities for the chatbot.
It abstracts away embedding providers, vector stores, and document processing
so you can easily swap implementations without changing agent code.

Key Components:
- embeddings: Generate text embeddings (abstraction layer)
- vector_store: Store and retrieve vectors (abstraction layer)
- document_processor: Parse PDFs and chunk text
- retriever: Orchestrate the retrieval process
- builders: Factory functions to initialize components
"""

from app.ai.rag.retriever import RAGRetriever
from app.ai.rag.builders import build_rag_system

__all__ = ["RAGRetriever", "build_rag_system"]
