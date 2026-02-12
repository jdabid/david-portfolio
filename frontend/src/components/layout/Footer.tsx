export default function Footer() {
  return (
    <footer className="border-t border-white/10 py-6">
      <div className="max-w-6xl mx-auto px-4 text-center text-gray-500 text-sm">
        <p>&copy; {new Date().getFullYear()} David Castro. Built with React + FastAPI + Docker + K8s</p>
      </div>
    </footer>
  );
}
