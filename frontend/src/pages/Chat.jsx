import { useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";


import ChatMessage from "../components/ChatMessage";
import api, { getErrorMessage } from "../services/api";

function Chat() {
  const { documentId } = useParams();

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const bottomRef = useRef(null);

  // Load saved chat history when the page opens
  useEffect(() => {
    setLoadingHistory(true);

    api
      .get(`/chat/history/${documentId}`)
      .then((res) => setMessages(res.data))
      .catch((err) =>
        setMessages([
          { role: "assistant", content: getErrorMessage(err), sources: [] },
        ])
      )
      .finally(() => setLoadingHistory(false));
  }, [documentId]);

  // Scroll to the newest message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, sending]);

  const handleSend = async (e) => {
    e.preventDefault();

    const question = input.trim();
    if (!question || sending) return;

    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setInput("");
    setSending(true);

    try {
      const { data } = await api.post(
        "/chat/ask",
        { document_id: documentId, question },
        { timeout: 120000 } // never wait forever
      );

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.answer, sources: data.sources },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: getErrorMessage(err), sources: [] },
      ]);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="page chat-page">
    

      <div className="chat-container">
        <div className="chat-header">
          <Link to="/dashboard">← All documents</Link>
        </div>

        <div className="chat-messages">
          {loadingHistory ? (
            <p className="muted">Loading chat...</p>
          ) : messages.length === 0 ? (
            <p className="muted">Ask anything about this PDF to get started.</p>
          ) : (
            messages.map((m, i) => <ChatMessage key={i} message={m} />)
          )}

          {sending && <p className="muted">ResearchAI is thinking...</p>}
          <div ref={bottomRef} />
        </div>

        <form className="chat-input" onSubmit={handleSend}>
          <input
            type="text"
            placeholder="Ask a question about this PDF..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            maxLength={4000}
            disabled={sending}
          />
          <button type="submit" disabled={sending || !input.trim()}>
            Send
          </button>
        </form>
      </div>
    </div>
  );
}

export default Chat;
