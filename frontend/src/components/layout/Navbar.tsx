import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";

const navItems = [
  { label: "Dashboard", to: "/dashboard" },
  { label: "Overview", to: "/analytics/overview" },
  { label: "Tactics", to: "/analytics/tactics" },
  { label: "Time Analysis", to: "/analytics/time" },
];

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  return (
    <nav className="border-b border-white/10 bg-chess-darker px-6 py-3">
      <div className="mx-auto flex max-w-7xl items-center justify-between">
        {/* Logo */}
        <Link
          to="/dashboard"
          className="flex items-center gap-2 text-chess-accent font-bold text-lg tracking-tight"
        >
          <span className="text-2xl">♞</span>
          <span>DiscoveredCheck</span>
        </Link>

        {/* Nav links */}
        <div className="hidden items-center gap-1 md:flex">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-chess-accent/20 text-chess-accent"
                    : "text-gray-300 hover:bg-white/5 hover:text-white"
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </div>

        {/* User menu */}
        <div className="flex items-center gap-3">
          <span className="text-sm text-gray-400">
            {user?.lichess_username}
          </span>
          <button
            onClick={handleLogout}
            className="rounded-md border border-white/10 px-3 py-1.5 text-sm text-gray-300 hover:border-white/20 hover:text-white transition-colors"
          >
            Sign out
          </button>
        </div>
      </div>
    </nav>
  );
}
