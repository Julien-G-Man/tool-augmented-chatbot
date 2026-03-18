import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

function shouldRenderMarkdown(text) {
  if (!text) {
    return false;
  }

  return /(^|\n)\s*([-*+]\s|\d+\.\s)|(^|\n)#{1,6}\s|\|.+\||\*\*[^*]+\*\*|`[^`]+`/.test(text);
}

export default function App() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: "Hi. Ask me about your company data.",
    },
  ]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function sendMessage(event) {
    event.preventDefault();
    const trimmed = query.trim();
    if (!trimmed || loading) {
      return;
    }

    setError("");
    setLoading(true);
    setMessages((prev) => [...prev, { role: "user", text: trimmed }]);
    setQuery("");

    try {
      const response = await fetch(`/chat?query=${encodeURIComponent(trimmed)}`, {
        method: "POST",
      });

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
          <h1>Company DB Chatbot</h1>
          <p>Simple React interface for your function-calling backend</p>
        </header>

        <div className="chatWindow" aria-live="polite">
          {messages.map((message, index) => (
            <article key={`${message.role}-${index}`} className={`bubble ${message.role}`}>
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
      </section>
    </main>
  );
}
