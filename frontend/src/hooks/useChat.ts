import { useState, useCallback, useRef, useEffect } from "react";
import { getChatWsUrl } from "../services/api";
import type { ChatMessage } from "../types";

interface UseChatReturn {
  messages: ChatMessage[];
  sendMessage: (text: string) => void;
  isStreaming: boolean;
  sessionId: string | null;
  error: string | null;
}

/**
 * Hook for AI Chat with WebSocket streaming.
 * Manages connection lifecycle, message history, and streaming state.
 */
export function useChat(): UseChatReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const streamBufferRef = useRef("");

  useEffect(() => {
    const ws = new WebSocket(getChatWsUrl());
    wsRef.current = ws;

    ws.onopen = () => setError(null);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === "token") {
        streamBufferRef.current += data.content;
        // Update the last assistant message in-place for streaming effect
        setMessages((prev) => {
          const updated = [...prev];
          const lastIdx = updated.length - 1;
          if (lastIdx >= 0 && updated[lastIdx].role === "assistant") {
            updated[lastIdx] = {
              ...updated[lastIdx],
              content: streamBufferRef.current,
            };
          }
          return updated;
        });
      } else if (data.type === "done") {
        setIsStreaming(false);
        setSessionId(data.session_id);
        streamBufferRef.current = "";
      } else if (data.type === "error") {
        setError(data.content);
        setIsStreaming(false);
      }
    };

    ws.onerror = () => setError("Connection error. Please try again.");
    ws.onclose = () => setError(null);

    return () => {
      ws.close();
    };
  }, []);

  const sendMessage = useCallback(
    (text: string) => {
      if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
        setError("Not connected. Please refresh the page.");
        return;
      }
      setError(null);
      setIsStreaming(true);
      streamBufferRef.current = "";

      // Add user message
      const userMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: "user",
        content: text,
        created_at: new Date().toISOString(),
      };

      // Add placeholder for assistant response
      const assistantPlaceholder: ChatMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: "",
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, userMsg, assistantPlaceholder]);

      wsRef.current.send(
        JSON.stringify({ message: text, session_id: sessionId })
      );
    },
    [sessionId]
  );

  return { messages, sendMessage, isStreaming, sessionId, error };
}
