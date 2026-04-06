import json
from openai import OpenAI
from app.ai.tools import tools
from app.ai.prompts import SYSTEM_PROMPT
from app.api.db_queries import (
    get_dependents_by_employee,
    get_employees_by_project,
    get_project_lead,
    list_departments,
    list_employees,
    list_projects,
)
from app.core.database import SessionLocal
from app.core.config import settings
from app.core.chat_history import get_recent_messages, save_message
from app.ai.rag.builders import build_rag_system

client = OpenAI(
    api_key=settings.NVIDIA_OPENAI_API_KEY,
    base_url=settings.NVIDIA_OPENAI_BASE_URL,
)

# Initialize RAG system once at startup
_rag_retriever = None

def get_rag_retriever():
    """Get or initialize RAG retriever singleton."""
    global _rag_retriever
    if _rag_retriever is None and settings.RAG_ENABLED:
        try:
            _rag_retriever = build_rag_system(
                embedding_provider=settings.RAG_EMBEDDING_PROVIDER,
                vector_store=settings.RAG_VECTOR_STORE,
                persistence_path=str(settings.RAG_STORE_PATH),
            )
        except Exception as e:
            print(f"Warning: Could not initialize RAG system: {e}")
    return _rag_retriever


def parse_tool_arguments(raw_arguments):
    if isinstance(raw_arguments, dict):
        return raw_arguments
    if isinstance(raw_arguments, str):
        try:
            return json.loads(raw_arguments)
        except json.JSONDecodeError:
            return {}
    return {}


def _format_rag_context(results):
    if not results:
        return "No relevant documents found."

    context_parts = ["Retrieved relevant documents:\n"]
    for i, result in enumerate(results, 1):
        source_info = f" (Source: {result['source']}, Score: {result['score']:.2f})"
        context_parts.append(f"\n[Document {i}]{source_info}\n{result['content']}\n")
    return "".join(context_parts)


def handle_tool_call(name, arguments):
    db = SessionLocal()
    
    DATABASE_TOOLS = {
        "list_departments": list_departments,
        "list_projects": list_projects,
        "list_employees": list_employees,
        "get_employees_by_project": get_employees_by_project,
        "get_project_lead": get_project_lead,
        "get_dependents_by_employee": get_dependents_by_employee
    }
    
    try:
        # Database tools
        if name in DATABASE_TOOLS:
            function_to_call =  DATABASE_TOOLS.get(name)
            if name in ["list_departments", "list_projects", "list_employees"]:
                return function_to_call(db)
            else:
                return function_to_call(db, **arguments)
        

        # RAG tools
        if name == "search_company_documents":
            rag = get_rag_retriever()
            if rag is None:
                return {"error": "RAG system not initialized"}

            query = arguments.get("query", "")
            top_k = arguments.get("top_k", settings.RAG_TOP_K)

            print("=" * 72)
            print("[RAG] TOOL CALL: search_company_documents")
            print("-" * 72)
            print(f"[RAG] Query: {query}")
            print(f"[RAG] top_k: {top_k}")
            print("[RAG] Retrieval method: semantic vector similarity search")
            print(f"[RAG] Embedding provider: {settings.RAG_EMBEDDING_PROVIDER}")
            print(f"[RAG] Vector store: {settings.RAG_VECTOR_STORE}")

            results = rag.search(query, top_k=top_k)
            if not results:
                print("[RAG] Retrieved chunks: 0")
                print("=" * 72)
                return {"results": "No relevant documents found."}

            print(f"[RAG] Retrieved chunks: {len(results)}")
            for idx, result in enumerate(results, 1):
                metadata = result.get("metadata", {})
                chunk_index = metadata.get("chunk_index", "unknown")
                preview = result.get("content", "").replace("\n", " ")[:140]
                print(
                    f"[RAG] Chunk {idx}: source={result.get('source', 'unknown')}, "
                    f"chunk_index={chunk_index}, score={result.get('score', 0):.3f}"
                )
                print(f"[RAG] Preview {idx}: {preview}...")
            print("=" * 72)

            context = _format_rag_context(results)
            return {"results": context}

        if name == "list_indexed_documents":
            rag = get_rag_retriever()
            if rag is None:
                return {"error": "RAG system not initialized"}
            docs = rag.list_documents()
            return {"documents": docs}

        # Unknown tool
        return {"error": f"Unknown tool: {name}"}

    finally:
        db.close()

def chat_with_ai(user_query: str, conversation_id: str = "default"):
    if not settings.NVIDIA_OPENAI_API_KEY:
        return "Missing NVIDIA_OPENAI_API_KEY in .env"

    recent_context = get_recent_messages(conversation_id=conversation_id, limit=5)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *recent_context,
        {"role": "user", "content": user_query},
    ]

    response = client.chat.completions.create(
        model=settings.NVIDIA_OPENAI_MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    message = response.choices[0].message

    # Handle iterative/multiple tool calls until we get a final text response.
    max_tool_rounds = 6
    rounds = 0

    while message.tool_calls and rounds < max_tool_rounds:
        rounds += 1
        print("=" * 72)
        print(f"[AGENT] Tool round {rounds}/{max_tool_rounds}")
        print(f"[AGENT] Tool calls in this round: {len(message.tool_calls)}")
        messages.append(message.model_dump(exclude_none=True))

        for tool_call in message.tool_calls:
            arguments = parse_tool_arguments(tool_call.function.arguments)
            print(f"[AGENT] Executing tool: {tool_call.function.name}")
            print(f"[AGENT] Tool arguments: {arguments}")
            result = handle_tool_call(tool_call.function.name, arguments)
            print(f"[AGENT] Tool result keys: {list(result.keys()) if isinstance(result, dict) else 'non-dict result'}")
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result, ensure_ascii=False),
                }
            )

        follow_up = client.chat.completions.create(
            model=settings.NVIDIA_OPENAI_MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        message = follow_up.choices[0].message

    final_content = message.content
    if not final_content:
        final_content = "I couldn't produce a final response text. Please try again with a more specific question."

    save_message(conversation_id, "user", user_query)
    save_message(conversation_id, "assistant", final_content)
    return final_content