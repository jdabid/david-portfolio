const skills = [
  { category: "Backend", items: ["Python", "FastAPI", "SQLAlchemy", "Celery", "PostgreSQL"] },
  { category: "DevOps", items: ["Docker", "Kubernetes", "Helm", "GitHub Actions", "Terraform"] },
  { category: "Frontend", items: ["React", "TypeScript", "Tailwind CSS", "Vite"] },
  { category: "Tools", items: ["Redis", "RabbitMQ", "Prometheus", "Grafana", "Nginx"] },
];

export default function About() {
  return (
    <section className="max-w-6xl mx-auto px-4 py-24">
      <h2 className="text-3xl font-bold text-white mb-8">About Me</h2>
      <div className="grid md:grid-cols-2 gap-12">
        <div className="space-y-4 text-gray-400">
          <p>
            I'm a Python Developer and DevOps Engineer focused on building reliable,
            scalable systems. I specialize in event-driven architectures, CQRS patterns,
            and cloud-native deployments.
          </p>
          <p>
            This portfolio itself is a technical showcase — built with FastAPI, React,
            Docker, Kubernetes, Helm, and a full CI/CD pipeline.
          </p>
        </div>
        <div className="grid grid-cols-2 gap-4">
          {skills.map((group) => (
            <div key={group.category}>
              <h3 className="text-primary-500 font-mono text-sm mb-2">
                {group.category}
              </h3>
              <ul className="space-y-1 text-gray-400 text-sm">
                {group.items.map((item) => (
                  <li key={item} className="flex items-center gap-2">
                    <span className="text-primary-500">&#9656;</span> {item}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
