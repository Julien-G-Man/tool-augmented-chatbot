# Tool-Augmented Chatbot (Agent Service)

This agent service exposes API endpoints and chatbot tool functions to query a SQL Server database (`CompanyDB`) designed in SSMS.

It is built as a learning project to connect an LLM assistant to real relational data through controlled function calls.

**NEW**: Now with **RAG (Retrieval-Augmented Generation)** - search and retrieve company documents!

## What It Does

- Exposes a FastAPI backend.
- Connects to a SQL Server database (`CompanyDB`) using SQLAlchemy + ODBC.
- Lets a chatbot call predefined tools/functions to query real CompanyDB tables.
- **Searches company PDF documents** using RAG - embeddings + vector search.
- Persists chat history in local SQLite and reuses the last 5 messages as context.
- Returns natural-language answers based on tool results and retrieved documents.

## Backend Flow

1. `POST /chat` receives a user query (and optional conversation ID).
2. `app/ai/agent.py` sends the query to the model.
3. The model can call declared tools from `app/ai/tools.py`:
   - **Database tools**: Query your SQL database
   - **RAG tools**: Search company documents
4. Tool handlers execute queries or retrieve documents.
5. The final response is stored in SQLite chat history and returned to the frontend.

## Database Coverage

The backend now matches the schema in `app/sql/CompanyDB.sql` and queries these tables:

- `Department`
- `Employee`
- `Project`
- `Works_on`
- `Dependent`

## RAG (Document Search) Coverage

The backend now includes RAG capabilities:

- Search company PDFs and documents
- Semantic search using embeddings
- Persistent document indexing

**Quick Start**: See [docs/RAG_QUICKSTART.md](./docs/RAG_QUICKSTART.md)

**Full Documentation**: See [docs/RAG.md](./docs/RAG.md)

**Implementation Details**: See [docs/IMPLEMENTATION_SUMMARY.md](./docs/IMPLEMENTATION_SUMMARY.md)

## Project Layout (Backend)

- `app/main.py`: FastAPI app entrypoint
- `app/core/config.py`: environment-driven settings (single source of truth)
- `app/core/database.py`: SQLAlchemy engine/session setup
- `app/api/routes.py`: HTTP routes
- `app/api/db_queries.py`: raw SQL query functions
- `app/ai/agent.py`: model call + tool execution loop
- `app/ai/tools.py`: tool schema exposed to model
- `app/sql/CompanyDB.sql`: SSMS database schema script

## Example Capabilities

- List all departments.
- List all projects.
- List all employees.
- Get employees by project name.
- Get a project's lead.
- Get dependents for an employee SSN.

## Run Locally

1. Install dependencies:
	- `pip install -r requirements.txt`
2. Create `.env` from `.env.example` and set your real values.
3. Set `DATABASE_URL` in `.env` to match your SQL Server auth mode (SQL login or trusted connection).
4. Keep configuration in `app/core/config.py` as the single source of truth.
5. Start the API:
	- `python run.py`
6. Verify database connectivity:
	- Open `http://127.0.0.1:8000/db/health`

## API Endpoints

- `GET /health`
- `GET /db/health`
- `POST /chat?query=...&conversation_id=...`
- `GET /departments`
- `GET /projects`
- `GET /employees`
- `GET /employees/by-project?project_name=...`
- `GET /project/lead?project_name=...`
- `GET /dependents/by-employee?employee_ssn=...`

## Chatbot Tools

The chatbot can call backend tools for:

- listing departments
- listing projects
- listing employees
- getting employees by project
- getting project lead
- getting dependents by employee

## Note

This is a learning project and not production-ready yet.

