import { Link, useLocation } from "react-router-dom";

const links = [
  { to: "/", label: "Home" },
  { to: "/about", label: "About" },
  { to: "/projects", label: "Projects" },
];

export default function Navbar() {
  const location = useLocation();

  return (
    <nav className="sticky top-0 z-50 bg-dark-900/80 backdrop-blur-md border-b border-white/10">
      <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
        <Link to="/" className="text-xl font-bold text-primary-500">
          DC
        </Link>
        <ul className="flex gap-6">
          {links.map((link) => (
            <li key={link.to}>
              <Link
                to={link.to}
                className={`text-sm transition-colors ${
                  location.pathname === link.to
                    ? "text-primary-500"
                    : "text-gray-400 hover:text-white"
                }`}
              >
                {link.label}
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </nav>
  );
}
