# Tool-Augmented Chatbot

This repository contains a full-stack learning project that connects a chatbot to a SQL Server database designed in SSMS (SQL Server Management Studio) .

The goal is to explore how function/tool-calling can let an AI assistant fetch real database data safely through backend functions instead of guessing.

## Repository Structure

- `backend/`: FastAPI API, SQL Server integration, chatbot orchestration, and SQL queries
- `frontend/`: Simple react chat interface for interacting with the backend

## How It Works (High Level)

1. The user types a question in the React UI.
2. The frontend sends it to the backend `/chat` endpoint.
3. The backend model decides whether to call a database tool function.
4. Tool functions execute SQL queries against `CompanyDB`.
5. The backend returns a clean answer to the frontend.

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
