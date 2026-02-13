import { useApi } from "../../hooks/useApi";
import { getProfile, getSkills } from "../../services/api";

const fallbackSkills = [
  { category: "Backend", items: ["Python", "FastAPI", "SQLAlchemy", "Celery", "PostgreSQL"] },
  { category: "DevOps", items: ["Docker", "Kubernetes", "Helm", "GitHub Actions", "Terraform"] },
  { category: "Frontend", items: ["React", "TypeScript", "Tailwind CSS", "Vite"] },
  { category: "Tools", items: ["Redis", "RabbitMQ", "Prometheus", "Grafana", "Nginx"] },
];

export default function About() {
  const { data: profile } = useApi(getProfile, []);
  const { data: skillGroups } = useApi(getSkills, []);

  const displaySkills = skillGroups ?? fallbackSkills;

  return (
    <section className="max-w-6xl mx-auto px-4 py-24">
      <h2 className="text-3xl font-bold text-white mb-8">About Me</h2>
      <div className="grid md:grid-cols-2 gap-12">
        <div className="space-y-4 text-gray-400">
          <p>
            {profile?.summary ||
              "I'm a Python Developer and DevOps Engineer focused on building reliable, scalable systems. I specialize in event-driven architectures, CQRS patterns, and cloud-native deployments."}
          </p>
          <p>
            This portfolio itself is a technical showcase — built with FastAPI, React,
            Docker, Kubernetes, Helm, and a full CI/CD pipeline.
          </p>
          {profile && (
            <div className="flex gap-4 mt-4">
              {profile.github_url && (
                <a
                  href={profile.github_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary-500 hover:text-primary-400 transition-colors"
                >
                  GitHub
                </a>
              )}
              {profile.linkedin_url && (
                <a
                  href={profile.linkedin_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary-500 hover:text-primary-400 transition-colors"
                >
                  LinkedIn
                </a>
              )}
            </div>
          )}
        </div>
        <div className="grid grid-cols-2 gap-4">
          {displaySkills.map((group) => (
            <div key={group.category}>
              <h3 className="text-primary-500 font-mono text-sm mb-2">
                {group.category}
              </h3>
              <ul className="space-y-1 text-gray-400 text-sm">
                {(group.items as any[]).map((item) => {
                  const name = typeof item === "string" ? item : item.name;
                  return (
                    <li key={name} className="flex items-center gap-2">
                      <span className="text-primary-500">&#9656;</span> {name}
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </div>
      </div>

      {/* Experience Timeline */}
      {profile?.experiences && profile.experiences.length > 0 && (
        <div className="mt-16">
          <h3 className="text-2xl font-bold text-white mb-8">Experience</h3>
          <div className="space-y-6 border-l-2 border-primary-500/30 pl-6">
            {profile.experiences.map((exp) => (
              <div key={exp.id} className="relative">
                <div className="absolute -left-[31px] w-4 h-4 bg-primary-500 rounded-full" />
                <p className="text-primary-500 font-mono text-xs">
                  {exp.start_date} — {exp.end_date}
                </p>
                <h4 className="text-white font-semibold">{exp.role}</h4>
                <p className="text-gray-400 text-sm">{exp.company}</p>
                {exp.description && (
                  <p className="text-gray-500 text-sm mt-1">{exp.description}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
