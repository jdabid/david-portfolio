import type {
  Profile, Project, ProjectDetail, SkillGroup,
  ContactMessage, ChatResponse, DashboardData,
} from "../types";

const API_BASE = import.meta.env.VITE_API_URL || "/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

// Profile
export const getProfile = () => request<Profile>("/profile");
export const getSkills = () => request<SkillGroup[]>("/profile/skills");

// Projects
export const getProjects = (tag?: string) => {
  const params = tag ? `?tag=${encodeURIComponent(tag)}` : "";
  return request<Project[]>(`/projects${params}`);
};
export const getProjectDetail = (slug: string) =>
  request<ProjectDetail>(`/projects/${slug}`);

// Contact
export const sendContactMessage = (data: ContactMessage) =>
  request<{ id: string; status: string; detail: string }>("/contact", {
    method: "POST",
    body: JSON.stringify(data),
  });

// AI Chat (REST — non-streaming)
export const sendChatMessage = (message: string, sessionId?: string) =>
  request<ChatResponse>("/chat", {
    method: "POST",
    body: JSON.stringify({ message, session_id: sessionId }),
  });

// AI Chat (WebSocket URL)
export const getChatWsUrl = () => {
  const base = API_BASE.replace(/^http/, "ws");
  return `${base}/chat/ws`;
};

// Analytics
export const trackVisit = (path: string) =>
  fetch(`${API_BASE}/analytics/track`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ path, visitor_id: getVisitorId() }),
    keepalive: true,
  });

export const getDashboard = (days = 30) =>
  request<DashboardData>(`/analytics/dashboard?days=${days}`);

// Health
export const fetchHealth = () => request<{ status: string }>("/health");

// Visitor ID — persistent per browser
function getVisitorId(): string {
  let id = localStorage.getItem("visitor_id");
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem("visitor_id", id);
  }
  return id;
}
