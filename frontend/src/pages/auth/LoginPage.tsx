import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import { initiateOAuth, resumeSession, storeTokens } from "../../services/auth";

export default function LoginPage() {
  const { user, setUser } = useAuth();
  const navigate = useNavigate();

  // Redirect if already authenticated (e.g. AuthContext rehydrated on fresh load)
  useEffect(() => {
    if (user) navigate("/dashboard", { replace: true });
  }, [user, navigate]);

  // After a soft logout the session cookie is still valid. Try to resume it
  // silently so the user never has to touch the Lichess OAuth flow again.
  useEffect(() => {
    if (user) return;
    resumeSession().then((result) => {
      if (result) {
        storeTokens(result.tokens);
        setUser(result.user);
      }
    });
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-chess-dark px-4">
      {/* Board-pattern background accent */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden opacity-5">
        <div
          className="h-full w-full"
          style={{
            backgroundImage:
              "repeating-conic-gradient(#e2b96f 0% 25%, transparent 0% 50%)",
            backgroundSize: "80px 80px",
          }}
        />
      </div>

      <div className="relative z-10 w-full max-w-md space-y-8 text-center">
        {/* Logo */}
        <div>
          <span className="text-7xl" role="img" aria-label="chess knight">
            ♞
          </span>
          <h1 className="mt-4 text-4xl font-bold tracking-tight text-chess-accent">
            DiscoveredCheck
          </h1>
          <p className="mt-2 text-lg text-gray-400">
            Chess analytics built for human insight
          </p>
        </div>

        {/* Feature highlights */}
        <ul className="space-y-3 text-left text-sm text-gray-400">
          {[
            "Win rates by color, time control & opening",
            "Missed tactics — forks, pins, and skewers",
            "Time analysis: does thinking longer help you?",
            "Sync directly from Lichess or upload PGN files",
          ].map((f) => (
            <li key={f} className="flex items-center gap-3">
              <span className="text-chess-accent">✓</span>
              {f}
            </li>
          ))}
        </ul>

        {/* Login button */}
        <button
          onClick={initiateOAuth}
          className="group relative w-full overflow-hidden rounded-xl bg-chess-accent px-6 py-4 font-semibold text-chess-dark shadow-lg transition-all hover:bg-chess-accent-dark focus:outline-none focus:ring-2 focus:ring-chess-accent focus:ring-offset-2 focus:ring-offset-chess-dark"
        >
          <span className="flex items-center justify-center gap-3">
            {/* Lichess logo approximation */}
            <svg className="h-6 w-6" viewBox="0 0 50 50" fill="currentColor">
              <path d="M38.956.5c-3.53.418-6.452 2.322-8.246 5.243l-5.33 8.564C11.11 14.931 1.78 23.926 1.78 35.25 1.78 43.818 8.453 50 17.724 50c6.614 0 12.02-3.38 15.02-8.505l1.523.001c3.426 0 6.154-2.576 6.435-5.931l.024-.3c.02-.234.09-3.594.09-3.594V14.823c0-4.265-3.37-7.786-7.628-7.972V5.743C33.189 2.69 36.066.77 38.956.5zm-4.665 12.268c2.087 0 3.783 1.696 3.783 3.785 0 2.088-1.696 3.784-3.783 3.784-2.087 0-3.783-1.696-3.783-3.784 0-2.09 1.696-3.785 3.783-3.785zM17.724 22.5c6.84 0 12.276 5.597 12.276 12.75S24.564 48 17.724 48C10.884 48 5.5 42.403 5.5 35.25S10.884 22.5 17.724 22.5z" />
            </svg>
            Continue with Lichess
          </span>
        </button>

        <p className="text-xs text-gray-600">
          We only request read access to your preferences. Your games are
          fetched directly from the Lichess API.
        </p>
      </div>
    </div>
  );
}
