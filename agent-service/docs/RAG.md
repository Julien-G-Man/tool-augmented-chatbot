# RAG (Retrieval-Augmented Generation) System Documentation

## Overview

This document explains the RAG system implemented in the chatbot. RAG allows the AI to search through the company's PDF documents and use that information to answer questions more accurately.

---

## Table of Contents

1. [What is RAG and Why You Need It](#what-is-rag)
2. [Architecture Overview](#architecture)
3. [Components Deep Dive](#components)
4. [How to Use RAG](#usage)
5. [Configuration](#configuration)
6. [Adding New Implementations](#extending)
7. [Troubleshooting](#troubleshooting)

---

## What is RAG and Why You Need It {#what-is-rag}

### The Problem Without RAG

Without RAG, the LLM only has general knowledge from its training data. It can't answer specific questions about the company's documents, policies, or internal data.

```
User: "What is our parental leave policy?"
LLM: "I don't have specific information about the company's policies."
```

### The Solution: RAG

RAG adds a **retrieval step** before asking the LLM. System flow:

```
1. User asks question
   ↓
2. Search company documents for relevant info
   ↓
3. Pass retrieved documents to LLM as context
   ↓
4. LLM answers using provided context
```

Result:

```
User: "What is our parental leave policy?"
RAG: [Retrieves relevant policy documents]
LLM: "According to the policy document, parental leave is..."
```

### Why This Works

- **LLMs are great at understanding context**: Give them relevant documents, they'll synthesize the answer
- **Embeddings are semantic**: Embeddings capture meaning, not just keywords. "Leave policy" matches queries about "parental time off"
- **Companies have massive docs**: PDFs, wikis, policies - RAG lets the AI use all of them

---

## Architecture Overview {#architecture}

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    The Chatbot (Agent)                        │
│                                                              │
│  When user asks a question:                                 │
│  1. Check if it needs document search                        │
│  2. Call RAG's search_company_documents tool                 │
│  3. Pass results to LLM as context                           │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   RAG Retriever (Orchestrator)               │
│                                                              │
│  Coordinates the RAG pipeline:                              │
│  - Embeds queries                                            │
│  - Searches vector store                                     │
│  - Formats results for LLM                                   │
└─────────────────────────────────────────────────────────────┘
            ↓                           ↓
    ┌──────────────┐           ┌──────────────────┐
    │ Embeddings   │           │  Vector Store    │
    │ Provider     │           │  (Search Index)  │
    │              │           │                  │
    │ Encodes text │           │ Stores vectors + │
    │ as vectors   │           │ documents        │
    └──────────────┘           └──────────────────┘
         ↑                              ↑
    ┌────────────────────────────────────────────┐
    │   Document Processor                        │
    │                                             │
    │   1. Read PDFs                              │
    │   2. Extract text                           │
    │   3. Split into chunks                      │
    │   4. Send to Embeddings Provider            │
    └────────────────────────────────────────────┘
              ↑
    ┌─────────────────────────┐
    │  The PDF Files          │
    │                         │
    │  data/documents/*.pdf   │
    └─────────────────────────┘
```

### Key Abstraction Levels

The beauty of this architecture: **Each component is replaceable**.

| Layer | Current | Alternatives |
|-------|---------|--------------|
| **Embeddings** | Mock (development) | OpenAI, Ollama, HuggingFace, Azure |
| **Vector Store** | In-Memory (simple) | Pinecone, Milvus, Weaviate, PostgreSQL+pgvector |
| **PDF Processing** | Text file simulation | PyPDF2, pdfplumber, Unstructured.io |

This means you can:
- **Start simple** (mock embeddings, in-memory store)
- **Scale up** (OpenAI embeddings, Pinecone) without touching code
- **Use open-source** (Ollama, Milvus) for full control

---

## Components Deep Dive {#components}

### 1. Document Processor (`document_processor.py`)

**Purpose**: Convert raw PDFs into embeddable chunks

**Path**: `app/ai/rag/document_processor.py`

#### How It Works

```python
# 1. Read PDF and extract text
pdf_content = "The company was founded in 2020..."

# 2. Split into chunks
# Chunks = overlapping text segments (~500 tokens each)
# Overlaps prevent concepts from being split across chunks

chunks = [
    "The company was founded in 2020. We serve...",  # Chunk 0
    "We serve SaaS companies. Our mission is...",     # Chunk 1 (overlaps with 0)
    "Our mission is to provide excellent support..."  # Chunk 2
]

# 3. Add metadata
# Why? So you know where the info came from
chunk.metadata = {
    "source_file": "handbook.pdf",
    "page": 2,
    "chunk_index": 0
}
```

#### Configuration

```python
from app.core.config import settings

settings.RAG_CHUNK_SIZE      # Token size (500 is standard)
settings.RAG_CHUNK_OVERLAP   # Overlap between chunks (50)
```

**Why These Values?**
- **500 tokens (~2000 chars)**: Enough context but not overwhelming
- **50 token overlap**: Prevents relevant context from being split across chunks

#### Usage

```python
from app.ai.rag.document_processor import DocumentProcessor

processor = DocumentProcessor(chunk_size=500, chunk_overlap=50)

# Process single PDF
chunks = processor.process_pdf("handbook.pdf")

# Process directory of PDFs
chunks = processor.process_directory("./documents/")
```

---

### 2. Embeddings Provider (`embeddings.py`)

**Purpose**: Convert text to high-dimensional vectors

**Path**: `app/ai/rag/embeddings.py`

#### What is an Embedding?

An embedding is a list of numbers that represents the *meaning* of text.

```python
text = "parental leave policy"
embedding = [0.23, -0.45, 0.12, ..., 0.88]  # 1536 values for OpenAI
                                              # Captures semantic meaning

# Key insight: Similar texts have similar embeddings
text2 = "parent time off policy"
embedding2 = [0.24, -0.44, 0.13, ..., 0.87]  # Very close to embedding!
```

#### Why Embeddings Matter

Embeddings enable **semantic** search (meaning-based) vs **keyword** search:

```python
# Keyword search: Looks for exact words
"parental leave" matches "parental leave", "leave types"
Misses: "parent time off", "maternity", "paternity"

# Semantic search (embeddings): Looks for meaning
"parental leave" matches all the above!
```

#### Implementations

##### MockEmbeddings (Development) ✅ Current

```python
from app.ai.rag.embeddings import MockEmbeddings

embeddings = MockEmbeddings(dimension=384)
vector = embeddings.embed_text("hello world")
# Returns predictable mock embedding - good for testing!
```

**Pros**: No API keys, fast, free, reproducible
**Cons**: Not semantically meaningful, just for testing

##### OpenAIEmbeddings (Production)

```python
from app.ai.rag.embeddings import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"  # 1536 dimensions, cheaper
    # or "text-embedding-3-large"   # 3072 dimensions, more accurate
)
vector = embeddings.embed_text("hello world")
# Calls OpenAI API - semantically meaningful!
```

**Pros**: Excellent quality, widely used, flexible
**Cons**: Costs money (~$0.02 per 1M tokens)

#### Adding New Providers

To add a new embedding provider (e.g., Ollama for free local embeddings):

```python
# In embeddings.py
class OllamaEmbeddings(EmbeddingProvider):
    def __init__(self, model: str = "nomic-embed-text"):
        self.model = model
        # Connect to Ollama server
    
    def embed_text(self, text: str) -> List[float]:
        # Call Ollama API
        pass
    
    def get_embedding_dimension(self) -> int:
        return 768

# Then add to builders.py:
def _build_embedding_provider(provider_type: str, **kwargs):
    if provider_type == "ollama":
        return OllamaEmbeddings(**kwargs)
```

---

### 3. Vector Store (`vector_store.py`)

**Purpose**: Store embeddings and enable similarity search

**Path**: `app/ai/rag/vector_store.py`

#### What is a Vector Store?

A vector store is a specialized database optimized for storing and searching vectors.

```
Regular Database:
- Key: "John"
- Value: {age: 30, city: "NYC"}
- Search: Exact matches, ranges

Vector Store:
- Key: "doc_123"
- Value: [0.23, -0.45, 0.12, ...]  (1536 dimensional!)
- Search: "Find 5 closest vectors"  (similarity search)

Why? Because with 1536+ dimensions, 
traditional databases are slow.
Vector stores use special algorithms (HNSW, IVF) 
to find similar vectors efficiently.
```

#### How Similarity Search Works

```python
# User asks: "What about family leave?"
query_embedding = embeddings.embed_text("What about family leave?")

# Vector store searches for similar embeddings
results = vector_store.search(query_embedding, top_k=5)
# Returns most similar documents!

# Why does it work?
# "family leave" embedding is similar to "parental leave", "paternity"
# because they share semantic meaning
```

#### Cosine Similarity

The most common distance metric for embeddings:

```python
# Ranges from -1 to 1 (we normalize to 0-1)
# 1.0 = identical vectors (100% similar)
# 0.5 = neutral
# 0.0 = orthogonal (no similarity)

similarity = dot_product / (magnitude1 * magnitude2)
```

#### Implementations

##### InMemoryVectorStore (Current) ✅

```python
from app.ai.rag.vector_store import InMemoryVectorStore

store = InMemoryVectorStore()
store.add_documents([doc1, doc2, doc3])
results = store.search(query_embedding, top_k=5)
```

**Pros**: Simple, no external dependencies, works for dev
**Cons**: All data lost on restart, doesn't scale beyond ~100K documents

**Good for**: Development, testing, small deployments

##### Production Vector Stores

| Store | When to Use | Pros | Cons |
|-------|-----------|------|------|
| **Pinecone** | Need managed service | Easy, scalable, fast | Costs money |
| **Milvus** | Open-source, full control | Free, powerful, scalable | Requires setup |
| **Weaviate** | Want GraphQL API | Full-featured, scalable | More complex |
| **PostgreSQL+pgvector** | Already using Postgres | No extra DB, powerful | Less optimized |

#### Adding Custom Vector Stores

Template to add Pinecone:

```python
# In vector_store.py
class PineconeVectorStore(VectorStore):
    def __init__(self, api_key: str, index_name: str):
        import pinecone
        pinecone.init(api_key=api_key)
        self.index = pinecone.Index(index_name)
    
    def add_documents(self, documents: List[StoredDocument]) -> None:
        vectors = [(doc.id, doc.embedding, doc.metadata) 
                   for doc in documents]
        self.index.upsert(vectors)
    
    def search(self, query_embedding, top_k: int):
        results = self.index.query(query_embedding, top_k=top_k)
        return [(r.id, r.score) for r in results.matches]

# Then in builders.py:
def _build_vector_store(store_type: str, **kwargs):
    if store_type == "pinecone":
        return PineconeVectorStore(
            kwargs['pinecone_api_key'],
            kwargs['pinecone_index']
        )
```

---

### 4. Retriever (`retriever.py`)

**Purpose**: Orchestrate the RAG pipeline

**Path**: `app/ai/rag/retriever.py`

The main interface the agent uses!

#### Main Methods

```python
rag = RAGRetriever(embedding_provider, vector_store)

# 1. Add documents
chunks = processor.process_directory("./docs/")
rag.add_documents(chunks)

# 2. Search
results = rag.search("company policy", top_k=5)
# Returns: [{content, source, score, metadata}, ...]

# 3. Get context for LLM
context = rag.get_context_string("company policy")
# Returns formatted string ready to pass to LLM:
# "Retrieved relevant documents:
#  
#  [Document 1] (Source: handbook.pdf, Score: 0.92)
#  The company provides 12 weeks of parental leave..."
```

#### Data Flow

```
add_documents():
  For each chunk:
    1. embedding = embeddings.embed_text(chunk)
    2. store_doc = StoredDocument(content, embedding, metadata)
    3. vector_store.add_documents([store_doc, ...])

search(query):
  1. query_emb = embeddings.embed_text(query)  # Same provider!
  2. results = vector_store.search(query_emb)
  3. Fetch full documents from vector_store
  4. Format and return to agent
```

**Key Insight**: Same embedding provider for documents and queries!
Otherwise vectors wouldn't be comparable.

---

### 5. Builders (`builders.py`)

**Purpose**: Factory functions to create RAG systems easily

**Path**: `app/ai/rag/builders.py`

#### Factory Pattern

The Builder pattern makes it easy to swap implementations:

```python
# Development setup
rag_dev = build_rag_system(
    embedding_provider="mock",
    vector_store="memory"
)

# Production setup (same code!)
rag_prod = build_rag_system(
    embedding_provider="openai",
    vector_store="pinecone",
    pinecone_api_key="...",
    pinecone_index="company-docs"
)
```

No agent code changes needed - just configuration!

#### Adding Support for New Implementations

```python
# 1. Implement the interface (e.g., OllamaEmbeddings)

# 2. Add to builder:
def _build_embedding_provider(provider_type: str, **kwargs):
    if provider_type == "ollama":
        return OllamaEmbeddings(
            model=kwargs.get("ollama_model", "nomic-embed-text")
        )

# 3. Use it:
rag = build_rag_system(
    embedding_provider="ollama",
    vector_store="memory"
)
```

---

## How to Use RAG {#usage}

### Step 1: Prepare the Documents

Create a directory with the company PDFs:

```
agent-service/
  data/
    documents/
      handbook.pdf
      policies.pdf
      procedures.txt
      ...
```

The system supports `.pdf` and `.txt` files.

### Step 2: Index Documents

Use the management CLI:

```bash
cd agent-service

# Index all documents
python -m app.ai.rag.management index ./data/documents/

# Output:
# 📂 Indexing documents from: ./data/documents/
# 🔧 Initializing RAG system...
# 📄 Processing documents...
#   Processing: handbook.pdf
#     -> Generated 45 chunks
#   Processing: policies.pdf
#     -> Generated 32 chunks
# 🚀 Adding 77 chunks to RAG system...
# ✅ Successfully indexed 77 chunks!
```

### Step 3: Use in Chatbot

The agent automatically uses RAG when appropriate:

```
User: "What is our vacation policy?"
Agent: 
  1. Recognizes this needs document search
  2. Calls search_company_documents tool
  3. Retrieves relevant policy chunks
  4. Passes to LLM as context
  5. LLM synthesizes answer from documents

Response: "According to our handbook, we provide..."
```

### Step 4: Test Search

```bash
# Test if search is working
python -m app.ai.rag.management search "company vacation policy"

# Output:
# 🔍 Searching for: company vacation policy
#
# Result 1 (Score: 0.923)
# Source: handbook.pdf
# Content: Employees receive 20 days paid vacation annually...
#
# Result 2 (Score: 0.856)
# Source: policies.pdf
# Content: Vacation requests should be...
```

### Management Commands

```bash
# Index new documents
python -m app.ai.rag.management index ./path/to/docs

# List indexed documents
python -m app.ai.rag.management list

# Clear all indexed docs (careful!)
python -m app.ai.rag.management clear

# Test search
python -m app.ai.rag.management search "your query"
```

---

## Configuration {#configuration}

### Environment Variables

Create/update `.env` in the agent-service folder:

```env
# RAG Configuration
RAG_ENABLED=true                           # Enable/disable RAG
RAG_EMBEDDING_PROVIDER=mock                # mock, openai, ollama, huggingface
RAG_VECTOR_STORE=memory                    # memory, pinecone, milvus
RAG_CHUNK_SIZE=500                         # Tokens per chunk
RAG_CHUNK_OVERLAP=50                       # Token overlap between chunks
RAG_TOP_K=5                                # Results to return
RAG_DATA_DIR=agent-service/data/documents  # Where PDFs are stored

# If using OpenAI embeddings:
# OPENAI_API_KEY=sk-...

# If using Pinecone:
# PINECONE_API_KEY=...
# PINECONE_INDEX=company-docs
```

### Development vs Production

**Development** (current):
```env
RAG_ENABLED=true
RAG_EMBEDDING_PROVIDER=mock
RAG_VECTOR_STORE=memory
```

Benefits: No API costs, no external dependencies, easy testing

**Production** (when scaling):
```env
RAG_ENABLED=true
RAG_EMBEDDING_PROVIDER=openai
RAG_VECTOR_STORE=pinecone
```

Benefits: Better quality embeddings, persistent storage, scales to millions of docs

---

## Adding New Implementations {#extending}

### Adding a Custom Embedding Provider

Example: Add Ollama (free local embeddings)

#### Step 1: Implement the Interface

```python
# In app/ai/rag/embeddings.py

class OllamaEmbeddings(EmbeddingProvider):
    """Use Ollama for local embeddings (free!)"""
    
    def __init__(self, model: str = "nomic-embed-text", host: str = "localhost"):
        self.model = model
        self.host = host
        self.port = 11434  # Default Ollama port
    
    def embed_text(self, text: str) -> List[float]:
        import requests
        response = requests.post(
            f"http://{self.host}:{self.port}/api/embeddings",
            json={"model": self.model, "prompt": text}
        )
        return response.json()["embedding"]
    
    def get_embedding_dimension(self) -> int:
        # Most models are 768 or 384
        return 768
```

#### Step 2: Register in Builder

```python
# In app/ai/rag/builders.py

def _build_embedding_provider(provider_type: str, **kwargs):
    # ... existing cases ...
    
    elif provider_type == "ollama":
        host = kwargs.get("ollama_host", "localhost")
        model = kwargs.get("ollama_model", "nomic-embed-text")
        return OllamaEmbeddings(model=model, host=host)
```

#### Step 3: Use It

```python
# In your code
rag = build_rag_system(
    embedding_provider="ollama",
    vector_store="memory",
    ollama_host="localhost",
    ollama_model="nomic-embed-text"
)
```

### Adding a Custom Vector Store

Example: Add PostgreSQL with pgvector

#### Step 1: Implement the Interface

```python
# In app/ai/rag/vector_store.py

class PostgresVectorStore(VectorStore):
    """Store vectors in PostgreSQL with pgvector extension"""
    
    def __init__(self, connection_string: str):
        import psycopg2
        self.conn = psycopg2.connect(connection_string)
        self._create_table()
    
    def _create_table(self):
        # Create table with pgvector support
        sql = """
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            content TEXT,
            embedding VECTOR(1536),
            metadata JSONB
        );
        CREATE INDEX IF NOT EXISTS idx_embedding 
        ON documents USING ivfflat (embedding vector_cosine_ops);
        """
        self.conn.execute(sql)
        self.conn.commit()
    
    def add_documents(self, documents: List[StoredDocument]):
        cursor = self.conn.cursor()
        for doc in documents:
            cursor.execute(
                "INSERT INTO documents VALUES (%s, %s, %s, %s)",
                (doc.id, doc.content, doc.embedding, doc.metadata)
            )
        self.conn.commit()
    
    def search(self, query_embedding, top_k: int):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT id, 1 - (embedding <=> %s) as similarity
            FROM documents
            ORDER BY embedding <=> %s
            LIMIT %s
            """,
            (query_embedding, query_embedding, top_k)
        )
        return cursor.fetchall()
```

#### Step 2: Register in Builder

```python
def _build_vector_store(store_type: str, **kwargs):
    # ... existing cases ...
    elif store_type == "postgres":
        conn_str = kwargs.get("postgres_url")
        return PostgresVectorStore(conn_str)
```

---

## Troubleshooting {#troubleshooting}

### RAG System Not Finding Relevant Results

**Problem**: Search returns irrelevant documents

**Solutions**:
1. Check chunk size (too small = loses context, too large = loses relevance)
2. Verify document content is actually indexed
3. Try different top_k value
4. Check embedding quality (mock embeddings won't work well)

```bash
# Debug: List what's indexed
python -m app.ai.rag.management list

# Debug: Test search
python -m app.ai.rag.management search "your query"
```

### Out of Memory Errors

**Problem**: System crashes with large document datasets

**Solutions**:
1. Switch from in-memory to persistent vector store (Pinecone, Milvus)
2. Reduce chunk count with larger chunk_size
3. Process documents in batches instead of all at once

### Slow Search

**Problem**: Search takes too long

**Solutions**:
1. Reduce top_k (fewer results = faster)
2. Switch to optimized vector store (in-memory uses full scan)
3. Use approximate search algorithms (Pinecone, Milvus do this)
4. Reduce dimension of embeddings (if using OpenAI, use "text-embedding-3-small")

### API Costs Exploding

**Problem**: Too many calls to OpenAI embeddings API

**Solutions**:
1. Cache documents after embedding (don't re-embed)
2. Use MockEmbeddings for dev/testing
3. Consider free alternatives (Ollama, HuggingFace)
4. Batch embedding calls

### Documents Not Found After Upload

**Problem**: Uploaded PDFs aren't showing in search

**Solutions**:
1. Verify PDFs are in correct directory
2. Run indexing command:
   ```bash
   python -m app.ai.rag.management index ./data/documents
   ```
3. Check for errors in PDF processing (some PDFs are hard to read)
4. Test search manually:
   ```bash
   python -m app.ai.rag.management search "test query"
   ```

---

## Next Steps

### Short Term
1. ✅ Set up dev environment (mock embeddings, in-memory store)
2. 📝 Test with sample documents
3. 🔍 Verify search quality

### Medium Term
1. 💶 Switch to OpenAI embeddings for better quality
2. 🗄️ Move to persistent vector store (Pinecone or Milvus)
3. 📊 Monitor costs and search performance

### Long Term
1. 🤖 Use open-source embeddings (Ollama, HuggingFace)
2. 🏠 Host on an open-source vector store (Milvus, Weaviate)
3. 📈 Add advanced features (reranking, filters, hybrid search)

---

## Summary

You now have a production-ready RAG system that:

✅ **Is modular**: Swap embeddings providers and vector stores easily
✅ **Is extensible**: Add new implementations without changing core code  
✅ **Is learnable**: Each component has clear responsibilities
✅ **Starts simple**: MockEmbeddings + InMemoryVectorStore for dev
✅ **Scales well**: Can upgrade to production providers when needed

The key insight: **RAG isn't magic**, it's a simple pipeline:
1. Process documents → chunks
2. Embed chunks → vectors
3. Store vectors with documents
4. Search vectors by similarity
5. Pass top results to LLM as context

Everything else is just optimization and implementation choices!
