# Frontend (React)

Simple React chat interface for the Tool-Augmented Chatbot backend.

## What It Does

- Provides a clean chat UI for sending questions to the backend.
- Calls backend `POST /chat` and displays assistant responses.
- Renders intentional Markdown from assistant messages (bold text, lists, tables).
- Falls back to plain text rendering for normal responses.

## How It Works

1. User submits a query in the input box.
2. Frontend sends `POST /chat?query=...`.
3. Agent service returns `{ "response": "..." }`.
4. UI renders assistant output with Markdown support when appropriate.

## Run

1. Install dependencies:
   `npm install`

2. Start the frontend:
   `npm run dev`

3. Open:
   `http://localhost:5173`

## Build

- `npm run build`
- `npm run preview`

## Notes

- Keep agent-service running on `http://127.0.0.1:8000`.
- Vite proxy forwards `/chat` and `/health` requests to agent-service port 8000.
