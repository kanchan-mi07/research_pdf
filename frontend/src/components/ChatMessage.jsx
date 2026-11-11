import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

function ChatMessage({ message }) {
  const isUser = message.role === "user";

  return (
    <div className={`message ${message.role}`}>
      <strong>{isUser ? "You" : "ResearchAI"}</strong>

      {isUser ? (
        // User messages stay plain text
        <p>{message.content}</p>
      ) : (
        // AI messages are rendered as Markdown
        <div className="markdown">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {message.content}
          </ReactMarkdown>
        </div>
      )}

      {message.sources?.length > 0 && (
        <div className="sources">
          <strong>Sources:</strong>

          {message.sources.map((source, index) => (
            <span key={index}>
              Page {source.page ?? source.page_number ?? "N/A"}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

export default ChatMessage;
