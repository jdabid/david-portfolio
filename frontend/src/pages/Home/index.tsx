import { Link } from "react-router-dom";
import { useApi } from "../../hooks/useApi";
import { getProfile } from "../../services/api";

export default function Home() {
  const { data: profile, loading } = useApi(getProfile, []);

  return (
    <section className="max-w-6xl mx-auto px-4 py-24">
      <div className="space-y-6">
        <p className="text-primary-500 font-mono text-sm">Hi, my name is</p>
        <h1 className="text-5xl md:text-7xl font-bold text-white">
          {loading ? "..." : profile?.full_name || "David Castro"}.
        </h1>
        <h2 className="text-3xl md:text-5xl font-bold text-gray-400">
          {loading ? "..." : profile?.headline || "Python Developer & DevOps Engineer"}.
        </h2>
        <p className="max-w-xl text-gray-400 text-lg">
          {profile?.summary ||
            "I build scalable backend systems, cloud-native infrastructure, and full-stack applications. Passionate about clean architecture, event-driven systems, and AI integration."}
        </p>
        <div className="flex gap-4 mt-4">
          <Link
            to="/projects"
            className="px-6 py-3 border border-primary-500 text-primary-500 rounded hover:bg-primary-500/10 transition-colors"
          >
            View My Work
          </Link>
          <Link
            to="/contact"
            className="px-6 py-3 bg-primary-600 text-white rounded hover:bg-primary-700 transition-colors"
          >
            Contact Me
          </Link>
        </div>
      </div>
    </section>
  );
}
