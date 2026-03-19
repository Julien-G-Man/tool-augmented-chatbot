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
      │  calls model with tool schemas
      ▼
LLM (OpenAI-compatible — configured via NVIDIA_OPENAI_* in .env)
      │  returns tool_call
      ▼
Tool Handler (agent.py)
      │  executes SQL
      ▼
SQL Server (CompanyDB)
      │  returns rows
      ▼
LLM (final answer generation)
      │  natural-language response
      ▼
User (React UI)
```

## Available Tools

The chatbot can call six predefined database functions:

| Tool | Description |
| --- | --- |
| `list_departments` | Return all departments |
| `list_projects` | Return all projects |
| `list_employees` | Return all employees |
| `get_employees_by_project` | Filter employees by project name |
| `get_project_lead` | Look up the lead of a given project |
| `get_dependents_by_employee` | Get dependents for an employee SSN |

## Repository Structure

- `backend/`: FastAPI API, SQL Server integration, chatbot orchestration, and SQL queries
- `frontend/`: Simple React chat interface for interacting with the backend

## Quick Start

1. Backend setup and run instructions:
	See `backend/README.md`
2. Frontend setup and run instructions:
	See `frontend/README.md`

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

- Backend: FastAPI, SQLAlchemy, pyodbc, OpenAI-compatible SDK
- Database: Local Microsoft SQL Server (SSMS + raw SQL schema)
- Frontend: React + Vite

## Notes

- This is a coursework/learning project.
- Configuration is environment-based (`.env`) and centralized in backend config.
