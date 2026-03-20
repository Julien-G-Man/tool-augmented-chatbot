# Tool-Augmented Chatbot

A full-stack learning project that demonstrates **LLM tool/function-calling** by connecting a chatbot to a real SQL Server database.

Instead of hallucinating answers, the AI assistant queries actual database tables through controlled backend functions, then summarises the results in natural language.

## What It Does

- **Answers natural-language questions** about employees, departments, projects, and dependents stored in a SQL Server database (`CompanyDB`).
- **Uses LLM tool-calling** so the model decides when and which database function to invoke rather than generating data from thin air.
- **Maintains conversation context** across multiple turns (last 5 messages kept in SQLite).
- **Renders rich responses** — the React UI supports Markdown tables and lists in assistant replies.

## Architecture

```
User (React UI)
      │  POST /chat
      ▼
FastAPI Backend
      │  calls model with tool schemas (DB + RAG)
      ▼
LLM (OpenAI-compatible — configured via NVIDIA_OPENAI_* in .env)
      │  returns tool_call
      ▼
Tool Handler (agent.py)
      │  executes SQL query or document retrieval
      ▼
Data Sources
  ├─ SQL Server (CompanyDB) -> returns rows
  └─ RAG Store (indexed PDF chunks) -> returns relevant context
      ▼
LLM (final answer generation)
      │  natural-language response
      ▼
User (React UI)
```

## Available Tools

The chatbot can call database and RAG tools:

| Tool | Description |
| --- | --- |
| `list_departments` | Return all departments |
| `list_projects` | Return all projects |
| `list_employees` | Return all employees |
| `get_employees_by_project` | Filter employees by project name |
| `get_project_lead` | Look up the lead of a given project |
| `get_dependents_by_employee` | Get dependents for an employee SSN |
| `search_company_documents` | Search indexed company PDFs/documents via RAG |
| `list_indexed_documents` | List indexed document sources and chunk counts |

## RAG Update

- PDFs and text documents can be indexed from `agent-service/data/documents/`.
- Indexed chunks are persisted in `agent-service/data/rag_store.json`.
- The assistant can now retrieve document context before answering.
- RAG docs are in `agent-service/docs/`:
      - `agent-service/docs/RAG_QUICKSTART.md`
      - `agent-service/docs/RAG.md`

## Repository Structure

- `agent-service/`: FastAPI API, SQL Server integration, chatbot orchestration, RAG indexing/retrieval, and SQL queries
- `web-client/`: React chat interface for interacting with the agent-service

Note: Folder positions are unchanged. The names `agent-service` and `web-client` are naming conventions for role clarity.

## Quick Start

1. Agent service setup and run instructions:
	See `agent-service/README.md`
2. Web client setup and run instructions:
	See `web-client/README.md`
3. RAG setup and indexing instructions:
      See `agent-service/docs/RAG_QUICKSTART.md`

## Demo Script

Use these prompts during a live demo to quickly show end-to-end functionality.

| Prompt | Expected Output |
| --- | --- |
| "List all departments." | A structured list of departments with department number, name, and manager info when available. |
| "Who is the lead of the ProductX project?" | A direct answer with project name, department, and lead name (or a clear no-result message if project is missing). |
| "Show employees working on ProductX with hours." | A clean table/list showing employee names and their assigned hours for that project. |

Demo tips:

- Run `GET /db/health` before starting the chat demo to confirm DB connectivity.
- Ask one broad question first (list), then one targeted question (lead), then one join-style question (employees + hours).
- If no rows are returned, the assistant should say so clearly and suggest a nearby valid query.

## Tech Stack

- Agent Service: FastAPI, SQLAlchemy, pyodbc, OpenAI-compatible SDK, pypdf (RAG parsing)
- Database: Local Microsoft SQL Server (SSMS + raw SQL schema)
- Web Client: React + Vite

## Notes

- This is a coursework/learning project.
- Configuration is environment-based (`.env`) and centralized in agent-service config.
