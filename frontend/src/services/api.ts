import type { Profile, Project, ProjectDetail, SkillGroup, ContactMessage } from "../types";

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

// Health
export const fetchHealth = () => request<{ status: string }>("/health");
