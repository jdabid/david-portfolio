const projects = [
  {
    title: "Portfolio CV App",
    description: "Full-stack portfolio with FastAPI, React, CQRS, Docker, K8s, and AI chat.",
    tags: ["Python", "React", "Docker", "K8s"],
  },
];

export default function Projects() {
  return (
    <section className="max-w-6xl mx-auto px-4 py-24">
      <h2 className="text-3xl font-bold text-white mb-8">Projects</h2>
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {projects.map((project) => (
          <div
            key={project.title}
            className="border border-white/10 rounded-lg p-6 hover:border-primary-500/50 transition-colors"
          >
            <h3 className="text-white font-semibold text-lg mb-2">{project.title}</h3>
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
    </section>
  );
}
