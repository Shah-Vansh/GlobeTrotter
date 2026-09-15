/**
 * lib/chatApi.js
 * Talks to the GlobeTrotter MCP chatbot (FastAPI on :8001 by default).
 * Uses the same JWT access token as the main app (tokenStorage).
 */
import { tokenStorage } from "../configs/api";

const CHATBOT_BASE =
  import.meta.env.VITE_CHATBOT_URL || "http://127.0.0.1:8001";

/**
 * Send a chat message to the MCP agent.
 * @param {string} message
 * @param {string|null} conversationId
 * @returns {Promise<object>} ChatResponse payload
 */
export async function sendChatMessage(message, conversationId = null) {
  const token = tokenStorage.getAccessToken();
  const headers = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const body = { message };
  if (conversationId) {
    body.conversation_id = conversationId;
  }

  const res = await fetch(`${CHATBOT_BASE}/api/chat`, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    const detail = data?.detail;
    const errMsg =
      (typeof detail === "object" && detail?.error) ||
      detail ||
      data?.error ||
      `Chat request failed (${res.status})`;
    const error = new Error(
      typeof errMsg === "string" ? errMsg : JSON.stringify(errMsg)
    );
    error.payload = data;
    throw error;
  }

  return data;
}

export function getChatbotBaseUrl() {
  return CHATBOT_BASE;
}
