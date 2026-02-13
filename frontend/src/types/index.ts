export interface Skill {
  id: string;
  name: string;
  category: string;
  level: number;
}

export interface SkillGroup {
  category: string;
  items: Skill[];
}

export interface Experience {
  id: string;
  company: string;
  role: string;
  description: string;
  start_date: string;
  end_date: string;
}

export interface Education {
  id: string;
  institution: string;
  degree: string;
  field: string;
  start_date: string;
  end_date: string;
}

export interface Profile {
  id: string;
  full_name: string;
  headline: string;
  summary: string;
  email: string;
  location: string;
  github_url: string;
  linkedin_url: string;
  avatar_url: string;
  skills: Skill[];
  experiences: Experience[];
  educations: Education[];
}

export interface Project {
  id: string;
  title: string;
  slug: string;
  description: string;
  tags: string[];
  image_url: string;
  featured: boolean;
}

export interface ProjectDetail extends Project {
  long_description: string;
  github_url: string;
  live_url: string;
}

export interface ContactMessage {
  name: string;
  email: string;
  subject: string;
  message: string;
}

export interface ApiResponse<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}
