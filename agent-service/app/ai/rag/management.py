"""
RAG Management Utilities

Command-line tools for managing documents in the RAG system.
- Index PDFs from a directory
- Clear indexed documents
- List indexed documents

Usage:
    python -m app.ai.rag.management index /path/to/pdfs
    python -m app.ai.rag.management list
    python -m app.ai.rag.management clear
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from app.ai.rag.builders import build_rag_system
from app.ai.rag.document_processor import DocumentProcessor
from app.core.config import settings


def index_documents(directory: str) -> None:
    """
    Index all PDF/text files in a directory.
    
    Process:
    1. Load all documents from directory
    2. Process and chunk them
    3. Generate embeddings
    4. Store in vector database
    
    Args:
        directory: Path to directory containing PDFs
    """
    print(f"\n📂 Indexing documents from: {directory}\n")
    
    # Check directory exists
    dir_path = Path(directory)
    if not dir_path.exists():
        print(f"❌ Directory not found: {directory}")
        return
    
    print("🔧 Initializing RAG system...")
    rag = build_rag_system(
        embedding_provider=settings.RAG_EMBEDDING_PROVIDER,
        vector_store=settings.RAG_VECTOR_STORE,
        persistence_path=str(settings.RAG_STORE_PATH),
    )
    
    print("📄 Processing documents...")
    processor = DocumentProcessor(
        chunk_size=settings.RAG_CHUNK_SIZE,
        chunk_overlap=settings.RAG_CHUNK_OVERLAP,
    )
    chunks = processor.process_directory(str(dir_path))
    
    if not chunks:
        print("❌ No documents found to index!")
        return
    
    # Add to RAG system
    print(f"\n🚀 Adding {len(chunks)} chunks to RAG system...")
    rag.add_documents(chunks)
    
    print(f"\n✅ Successfully indexed {len(chunks)} chunks!\n")


def list_documents() -> None:
    """List all indexed documents."""
    print("\n📚 Indexed Documents:\n")
    
    rag = build_rag_system(
        embedding_provider=settings.RAG_EMBEDDING_PROVIDER,
        vector_store=settings.RAG_VECTOR_STORE,
        persistence_path=str(settings.RAG_STORE_PATH),
    )
    
    docs = rag.list_documents()
    if not docs:
        print("No documents indexed yet.")
    else:
        for i, doc in enumerate(docs, 1):
            print(f"{i}. {doc}")
    print()


def clear_documents() -> None:
    """Clear all indexed documents."""
    print("\n⚠️  Clearing all indexed documents...\n")
    
    response = input("Are you sure? This cannot be undone. (yes/no): ")
    if response.lower() != "yes":
        print("Cancelled.")
        return
    
    rag = build_rag_system(
        embedding_provider=settings.RAG_EMBEDDING_PROVIDER,
        vector_store=settings.RAG_VECTOR_STORE,
        persistence_path=str(settings.RAG_STORE_PATH),
    )
    
    rag.clear()
    print("✅ All documents cleared!\n")


def test_search(query: str) -> None:
    """Test search functionality."""
    print(f"\n🔍 Searching for: {query}\n")
    
    rag = build_rag_system(
        embedding_provider=settings.RAG_EMBEDDING_PROVIDER,
        vector_store=settings.RAG_VECTOR_STORE,
        persistence_path=str(settings.RAG_STORE_PATH),
    )
    
    results = rag.search(query, top_k=5)
    
    if not results:
        print("No results found.")
    else:
        for i, result in enumerate(results, 1):
            print(f"Result {i} (Score: {result['score']:.3f})")
            print(f"Source: {result['source']}")
            print(f"Content: {result['content'][:400]}...\n")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="RAG Management Utilities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m app.ai.rag.management index ./documents
  python -m app.ai.rag.management list
  python -m app.ai.rag.management clear
  python -m app.ai.rag.management search "company policy"
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Index command
    index_parser = subparsers.add_parser("index", help="Index documents from directory")
    index_parser.add_argument("directory", help="Directory containing PDFs")
    
    # List command
    subparsers.add_parser("list", help="List indexed documents")
    
    # Clear command
    subparsers.add_parser("clear", help="Clear all indexed documents")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Test search functionality")
    search_parser.add_argument("query", help="Search query")
    
    args = parser.parse_args()
    
    if args.command == "index":
        index_documents(args.directory)
    elif args.command == "list":
        list_documents()
    elif args.command == "clear":
        clear_documents()
    elif args.command == "search":
        test_search(args.query)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
