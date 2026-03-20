from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router
from app.ai.agent import chat_with_ai
from app.core.chat_history import clear_conversation

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.post("/chat")
def chat(query: str, conversation_id: str = "default"):
    response = chat_with_ai(query, conversation_id=conversation_id)
    return {"response": response}


@app.post("/chat/clear-context")
def clear_chat_context(conversation_id: str = "default"):
    deleted_count = clear_conversation(conversation_id)
    return {"status": "cleared", "conversation_id": conversation_id, "deleted": deleted_count}

@app.get("/health")
def health():
    return {"status": "OK"}