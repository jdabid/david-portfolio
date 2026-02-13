import { useState } from "react";
import { useApi } from "../../hooks/useApi";
import { getProjects } from "../../services/api";

const fallbackProjects = [
  {
    id: "1",
    title: "Portfolio CV App",
    slug: "portfolio-cv",
    description: "Full-stack portfolio with FastAPI, React, CQRS, Docker, K8s, and AI chat.",
    tags: ["Python", "React", "Docker", "K8s"],
    image_url: "",
    featured: true,
  },
];

export default function Projects() {
  const [activeTag, setActiveTag] = useState<string | undefined>(undefined);
  const { data: projects, loading } = useApi(() => getProjects(activeTag), [activeTag]);

  const displayProjects = projects ?? fallbackProjects;

  // Extract unique tags for filter
  const allTags = [...new Set(displayProjects.flatMap((p) => p.tags))];

  return (
    <section className="max-w-6xl mx-auto px-4 py-24">
      <h2 className="text-3xl font-bold text-white mb-8">Projects</h2>

      {/* Tag Filters */}
      <div className="flex flex-wrap gap-2 mb-8">
        <button
          onClick={() => setActiveTag(undefined)}
          className={`text-xs font-mono px-3 py-1 rounded border transition-colors ${
            !activeTag
              ? "bg-primary-500 text-white border-primary-500"
              : "text-gray-400 border-white/10 hover:border-primary-500/50"
          }`}
        >
          All
        </button>
        {allTags.map((tag) => (
          <button
            key={tag}
            onClick={() => setActiveTag(tag)}
            className={`text-xs font-mono px-3 py-1 rounded border transition-colors ${
              activeTag === tag
                ? "bg-primary-500 text-white border-primary-500"
                : "text-gray-400 border-white/10 hover:border-primary-500/50"
            }`}
          >
            {tag}
          </button>
        ))}
      </div>

      {/* Project Grid */}
      {loading ? (
        <div className="text-gray-500">Loading projects...</div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {displayProjects.map((project) => (
            <div
              key={project.id}
              className="border border-white/10 rounded-lg p-6 hover:border-primary-500/50 transition-colors group"
            >
              {project.featured && (
                <span className="text-xs font-mono text-yellow-400 mb-2 inline-block">
                  Featured
                </span>
              )}
              <h3 className="text-white font-semibold text-lg mb-2 group-hover:text-primary-500 transition-colors">
                {project.title}
              </h3>
              <p className="text-gray-400 text-sm mb-4">{project.description}</p>
              <div className="flex flex-wrap gap-2">
                {project.tags.map((tag) => (
                  <span
                    key={tag}
                    className="text-xs font-mono text-primary-500 bg-primary-500/10 px-2 py-1 rounded"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
