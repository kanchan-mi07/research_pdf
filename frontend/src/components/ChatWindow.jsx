import { useState } from "react";
import { askQuestion } from "../services/api";
import ChatMessage from "./ChatMessage";

function ChatWindow({ document }) {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleAsk = async (e) => {
    e.preventDefault();

    if (!question.trim() || loading) return;

    const currentQuestion = question.trim();

    setMessages((prev) => [
      ...prev,
      { role: "user", content: currentQuestion },
    ]);

    setQuestion("");
    setLoading(true);

    try {
      const result = await askQuestion(document.id, currentQuestion);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: result.answer || "No answer received.",
          sources: result.sources || [],
        },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            error.response?.data?.detail ||
            "Something went wrong. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="chat-section">
      <div className="chat-header">
        <div>
          <h2>Ask your PDF</h2>
          <p>Document: {document.name}</p>
        </div>
        <span className="ai-badge">AI Powered</span>
      </div>

      <div className="messages">
        {messages.length === 0 && (
          <div className="welcome-message">
            <h3>What would you like to know?</h3>
            <p>Ask questions about your uploaded research document.</p>
          </div>
        )}

        {messages.map((message, index) => (
          <ChatMessage key={index} message={message} />
        ))}

        {loading && (
          <div className="message assistant">
            <strong>ResearchAI</strong>
            <p>Thinking...</p>
          </div>
        )}
      </div>

      <form className="chat-input" onSubmit={handleAsk}>
        <input
          type="text"
          placeholder="Ask something about your PDF..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          disabled={loading}
        />

        <button type="submit" disabled={loading || !question.trim()}>
          {loading ? "..." : "Send"}
        </button>
      </form>
    </section>
  );
}

export default ChatWindow;
