export default function Home() {
  return (
    <section className="max-w-6xl mx-auto px-4 py-24">
      <div className="space-y-6">
        <p className="text-primary-500 font-mono text-sm">Hi, my name is</p>
        <h1 className="text-5xl md:text-7xl font-bold text-white">
          David Castro.
        </h1>
        <h2 className="text-3xl md:text-5xl font-bold text-gray-400">
          Python Developer & DevOps Engineer.
        </h2>
        <p className="max-w-xl text-gray-400 text-lg">
          I build scalable backend systems, cloud-native infrastructure, and
          full-stack applications. Passionate about clean architecture, event-driven
          systems, and AI integration.
        </p>
        <a
          href="/projects"
          className="inline-block mt-4 px-6 py-3 border border-primary-500 text-primary-500 rounded hover:bg-primary-500/10 transition-colors"
        >
          View My Work
        </a>
      </div>
    </section>
  );
}
