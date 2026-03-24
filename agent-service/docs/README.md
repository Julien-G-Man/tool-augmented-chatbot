# Agent Service Documentation

Documentation for the agent service system.

## Quick Navigation

### Getting Started
- **[RAG_QUICKSTART.md](./RAG_QUICKSTART.md)** - Get RAG running in 5 minutes

### Deep Dives
- **[RAG.md](./RAG.md)** - Complete RAG documentation (architecture, components, troubleshooting)
- **[IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)** - What was built and how to learn from it

## What's Here

The agent service includes:

1. **LLM Agent** with tool-calling capabilities
   - Connects to SQL Server database
   - Executes predefined tools based on user queries
   - Returns natural language responses

2. **RAG (Retrieval-Augmented Generation)** System
   - Semantic search over company documents (PDFs)
   - Embeddings and vector similarity
   - Pluggable architecture for easy upgrades

3. **Chat History** with context awareness
   - SQLite-based persistence
   - Last 5 messages used as context

## Architecture

```
User Query
    ↓
FastAPI Endpoint (/chat)
    ↓
LLM Agent
    ├─→ Database Tools (query CompanyDB)
    └─→ RAG Tools (search documents)
    ↓
Tool Execution
    ↓
Response → Chat History → User
```

## Key Technologies

- **FastAPI** - Web framework
- **SQLAlchemy** - ORM for database
- **OpenAI API** - LLM calls
- **SQLite** - Chat history
- **Custom RAG** - Document retrieval

## Configuration

Settings are environment-based. See `.env.example` for template.

## For Developers

Start with [RAG_QUICKSTART.md](./RAG_QUICKSTART.md) to understand the RAG system, then dig into [RAG.md](./RAG.md) for details on architecture and extensibility.

Each component was designed with learning in mind - see [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md) for the educational journey.
