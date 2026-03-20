# RAG Quick Start Guide

Get your RAG system running in 5 minutes!

## 1. Create Document Directory

```bash
# In agent-service folder
mkdir -p data/documents
```

## 2. Add Your PDFs

Copy your company PDFs/text files to `agent-service/data/documents/`:

```
agent-service/
  data/
    documents/
      handbook.pdf
      policies.pdf
      procedures.txt
```

## 3. Index Documents

```bash
cd agent-service

# Index all documents in the directory
python -m app.ai.rag.management index ./data/documents/
```

You should see:
```
📂 Indexing documents from: ./data/documents/
🔧 Initializing RAG system...
📄 Processing documents...
  Processing: handbook.pdf
    -> Generated 45 chunks
✅ Successfully indexed 45 chunks!
```

## 4. Test Search

```bash
# Try searching for something
python -m app.ai.rag.management search "company policy"
```

You should see results:
```
🔍 Searching for: company policy

Result 1 (Score: 0.923)
Source: handbook.pdf
Content: The company was founded in 2010...
```

## 5. Use in Chatbot

Now when users ask questions, the agent will automatically search your documents!

```
User: "What is our vacation policy?"
Agent: [Searches documents] → [Retrieves relevant sections] 
Agent Response: "According to our handbook, we provide..."
```

## Common Commands

```bash
# Index documents
python -m app.ai.rag.management index ./data/documents/

# List indexed docs
python -m app.ai.rag.management list

# Test search
python -m app.ai.rag.management search "your query"

# Clear all documents
python -m app.ai.rag.management clear
```

## If Results Look Like Gibberish

If search output contains PDF internals like `BT`, `ET`, or long hex-like strings, your store likely has chunks indexed with an older parser.

Run a clean reindex:

```bash
cd agent-service
python -m app.ai.rag.management clear
python -m app.ai.rag.management index ./data/documents/
python -m app.ai.rag.management search "engineer"
```

## Configuration

Edit `.env` file in agent-service folder:

```env
# Use mock embeddings (free, for development)
RAG_EMBEDDING_PROVIDER=mock
RAG_VECTOR_STORE=memory

# Or use OpenAI (better quality)
RAG_EMBEDDING_PROVIDER=openai
RAG_VECTOR_STORE=memory
OPENAI_API_KEY=sk-...
```

## Next: Read Full Documentation

See [RAG.md](./RAG.md) for detailed explanations of:
- How RAG works
- Each component
- How to add new implementations
- Troubleshooting

## Need Help?

See Troubleshooting section in [RAG.md](./RAG.md)
