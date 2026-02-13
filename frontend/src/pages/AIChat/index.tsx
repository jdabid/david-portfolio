import { useState, useRef, useEffect } from "react";
import { useChat } from "../../hooks/useChat";

export default function AIChat() {
  const { messages, sendMessage, isStreaming, error } = useChat();
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;
    sendMessage(input.trim());
    setInput("");
  };

  return (
    <section className="max-w-3xl mx-auto px-4 py-12 flex flex-col h-[calc(100vh-8rem)]">
      <div className="mb-4">
        <h2 className="text-2xl font-bold text-white">AI Assistant</h2>
        <p className="text-gray-500 text-sm">
          Ask me anything about David's skills, experience, or projects.
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-2">
        {messages.length === 0 && (
          <div className="text-center py-16 space-y-4">
            <p className="text-gray-500">Start a conversation</p>
            <div className="flex flex-wrap justify-center gap-2">
              {[
                "What are David's main skills?",
                "Tell me about his experience",
                "What projects has he built?",
                "What DevOps tools does he use?",
              ].map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => sendMessage(suggestion)}
                  className="text-xs px-3 py-2 border border-white/10 rounded-lg text-gray-400 hover:border-primary-500/50 hover:text-primary-500 transition-colors"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[80%] rounded-lg px-4 py-3 ${
                msg.role === "user"
                  ? "bg-primary-600 text-white"
                  : "bg-dark-800 text-gray-300 border border-white/10"
              }`}
            >
              <p className="whitespace-pre-wrap text-sm">{msg.content}</p>
              {msg.role === "assistant" && !msg.content && isStreaming && (
                <span className="inline-block w-2 h-4 bg-primary-500 animate-pulse" />
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Error */}
      {error && (
        <p className="text-red-400 text-sm mb-2">{error}</p>
      )}

      {/* Input */}
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about David's skills, experience, projects..."
          disabled={isStreaming}
          className="flex-1 px-4 py-3 bg-dark-800 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:border-primary-500 focus:outline-none transition-colors disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={isStreaming || !input.trim()}
          className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isStreaming ? "..." : "Send"}
        </button>
      </form>
    </section>
  );
}
