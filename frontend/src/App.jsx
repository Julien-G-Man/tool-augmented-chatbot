import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

function shouldRenderMarkdown(text) {
  if (!text) {
    return false;
  }

  return /(^|\n)\s*([-*+]\s|\d+\.\s)|(^|\n)#{1,6}\s|\|.+\||\*\*[^*]+\*\*|`[^`]+`/.test(text);
}

const CONVERSATION_STORAGE_KEY = "company-db-chat-conversation-id";
const INITIAL_ASSISTANT_MESSAGE = {
  role: "assistant",
  text: "Hi. Ask me about your company data.",
};

function createConversationId() {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }

  return `conv-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
}

export default function App() {
  const [query, setQuery] = useState("");
  const [conversationId, setConversationId] = useState(() => {
    const existingId = localStorage.getItem(CONVERSATION_STORAGE_KEY);

    if (existingId) {
      return existingId;
    }

    const newId = createConversationId();

    localStorage.setItem(CONVERSATION_STORAGE_KEY, newId);
    return newId;
  });
  const [messages, setMessages] = useState([INITIAL_ASSISTANT_MESSAGE]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const chatWindowRef = useRef(null);
  const messageRefs = useRef([]);
  const pendingUserIndexRef = useRef(null);

  useEffect(() => {
    const pendingUserIndex = pendingUserIndexRef.current;
    const latestMessage = messages[messages.length - 1];

    if (pendingUserIndex === null || loading || latestMessage?.role !== "assistant") {
      return;
    }

    const chatWindow = chatWindowRef.current;
    const userMessage = messageRefs.current[pendingUserIndex];

    if (chatWindow && userMessage) {
      chatWindow.scrollTo({
        top: Math.max(userMessage.offsetTop - 8, 0),
        behavior: "smooth",
      });
    }

    pendingUserIndexRef.current = null;
  }, [messages, loading]);

  async function startNewChat() {
    if (loading) {
      return;
    }

    setError("");

    try {
      const response = await fetch(
        `/chat/clear-context?conversation_id=${encodeURIComponent(conversationId)}`,
        { method: "POST" }
      );

      if (!response.ok) {
        throw new Error(`Failed to clear context: ${response.status}`);
      }
    } catch (err) {
      setError("Could not clear server memory for the previous chat, but a new chat was started.");
      console.error(err);
    }

    const newConversationId = createConversationId();
    localStorage.setItem(CONVERSATION_STORAGE_KEY, newConversationId);
    setConversationId(newConversationId);
    setMessages([INITIAL_ASSISTANT_MESSAGE]);
    setQuery("");
    pendingUserIndexRef.current = null;
    messageRefs.current = [];
  }

  async function sendMessage(event) {
    event.preventDefault();
    const trimmed = query.trim();
    if (!trimmed || loading) {
      return;
    }

    setError("");
    setLoading(true);
    pendingUserIndexRef.current = messages.length;
    setMessages((prev) => [...prev, { role: "user", text: trimmed }]);
    setQuery("");

    try {
      const response = await fetch(
        `/chat?query=${encodeURIComponent(trimmed)}&conversation_id=${encodeURIComponent(conversationId)}`,
        {
        method: "POST",
        }
      );

      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }

      const data = await response.json();
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: data.response || "No response returned." },
      ]);
    } catch (err) {
      setError("Could not reach the backend. Make sure FastAPI is running on port 8000.");
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: "I could not fetch data right now. Please check the backend server.",
        },
      ]);
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="page">
      <section className="card">
        <header className="header">
          <div className="titleRow">
            <h1>Company DB Chatbot</h1>
            <span className={`statusTag ${loading ? "busy" : "idle"}`}>
              {loading ? "Thinking" : "Ready"}
            </span>
          </div>
          <p>Ask natural questions about your SQL Server company data.</p>
        </header>

        <div className="chatWindow" aria-live="polite" ref={chatWindowRef}>
          {messages.map((message, index) => (
            <article
              key={`${message.role}-${index}`}
              className={`bubble ${message.role}`}
              ref={(element) => {
                messageRefs.current[index] = element;
              }}
            >
              <span className="role">{message.role === "user" ? "You" : "Assistant"}</span>
              {message.role === "assistant" && shouldRenderMarkdown(message.text) ? (
                <div className="markdown">
                  <ReactMarkdown remarkPlugins={[remarkGfm]} skipHtml>
                    {message.text}
                  </ReactMarkdown>
                </div>
              ) : (
                <p className="plainText">{message.text}</p>
              )}
            </article>
          ))}
        </div>

        <div className="metaRow">
          <span>{messages.length - 1} messages</span>
          <div className="metaActions">
            <span>Backend: localhost:8000</span>
            <button
              type="button"
              className="ghostButton"
              onClick={startNewChat}
              disabled={loading}
            >
              New Chat
            </button>
          </div>
        </div>

        <form className="composer" onSubmit={sendMessage}>
          <input
            type="text"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Ask about a project or employee..."
            disabled={loading}
          />
          <button type="submit" disabled={loading || !query.trim()}>
            {loading ? "Sending..." : "Send"}
          </button>
        </form>

        {error ? <p className="error">{error}</p> : null}

        <p className="hint">Try: "List all departments" or "Who leads ProductX?"</p>
      </section>
    </main>
  );
}
