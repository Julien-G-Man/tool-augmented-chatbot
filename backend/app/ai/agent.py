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

client = OpenAI(
    api_key=settings.NVIDIA_OPENAI_API_KEY,
    base_url=settings.NVIDIA_OPENAI_BASE_URL,
)


def parse_tool_arguments(raw_arguments):
    if isinstance(raw_arguments, dict):
        return raw_arguments
    if isinstance(raw_arguments, str):
        try:
            return json.loads(raw_arguments)
        except json.JSONDecodeError:
            return {}
    return {}

def handle_tool_call(name, arguments):
    db = SessionLocal()
    try:
        if name == "list_departments":
            return list_departments(db)
        if name == "list_projects":
            return list_projects(db)
        if name == "list_employees":
            return list_employees(db)
        if name == "get_employees_by_project":
            return get_employees_by_project(db, **arguments)
        if name == "get_project_lead":
            return get_project_lead(db, **arguments)
        if name == "get_dependents_by_employee":
            return get_dependents_by_employee(db, **arguments)
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

    if message.tool_calls:
        tool_call = message.tool_calls[0]
        arguments = parse_tool_arguments(tool_call.function.arguments)
        result = handle_tool_call(tool_call.function.name, arguments)

        second_response = client.chat.completions.create(
            model=settings.NVIDIA_OPENAI_MODEL,
            messages=messages + [
                message,
                {"role": "tool", "tool_call_id": tool_call.id, "content": str(result)}
            ]
        )

        final_content = second_response.choices[0].message.content or "I could not generate a response."
        save_message(conversation_id, "user", user_query)
        save_message(conversation_id, "assistant", final_content)
        return final_content

    final_content = message.content or "I could not generate a response."
    save_message(conversation_id, "user", user_query)
    save_message(conversation_id, "assistant", final_content)
    return final_content