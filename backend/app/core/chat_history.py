import sqlite3
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[2]
CHAT_HISTORY_DB = BACKEND_ROOT / "chat_history.sqlite3"


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(CHAT_HISTORY_DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_chat_history_db() -> None:
    with _get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_chat_messages_conversation_id_id
            ON chat_messages (conversation_id, id)
            """
        )


def save_message(conversation_id: str, role: str, content: str) -> None:
    if role not in {"user", "assistant"}:
        return

    if not content:
        return

    with _get_connection() as conn:
        conn.execute(
            """
            INSERT INTO chat_messages (conversation_id, role, content)
            VALUES (?, ?, ?)
            """,
            (conversation_id, role, content),
        )


def get_recent_messages(conversation_id: str, limit: int = 5) -> list[dict]:
    with _get_connection() as conn:
        rows = conn.execute(
            """
            SELECT role, content
            FROM chat_messages
            WHERE conversation_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (conversation_id, limit),
        ).fetchall()

    # Return oldest -> newest so model reads context in natural order.
    ordered_rows = reversed(rows)
    return [{"role": row["role"], "content": row["content"]} for row in ordered_rows]


def clear_conversation(conversation_id: str) -> int:
    with _get_connection() as conn:
        cursor = conn.execute(
            """
            DELETE FROM chat_messages
            WHERE conversation_id = ?
            """,
            (conversation_id,),
        )
        return cursor.rowcount


init_chat_history_db()