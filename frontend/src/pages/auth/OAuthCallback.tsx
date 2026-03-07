import { useEffect, useRef } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import { exchangeOAuthCode, storeTokens } from "../../services/auth";
import LoadingSpinner from "../../components/common/LoadingSpinner";

export default function OAuthCallback() {
  const [searchParams] = useSearchParams();
  const { setUser } = useAuth();
  const navigate = useNavigate();
  const attempted = useRef(false);

  useEffect(() => {
    if (attempted.current) return;
    attempted.current = true;

    const code = searchParams.get("code");
    const state = searchParams.get("state");
    const error = searchParams.get("error");

    if (error || !code || !state) {
      console.error("OAuth error:", error ?? "Missing code or state");
      navigate("/login?error=oauth_failed", { replace: true });
      return;
    }

    exchangeOAuthCode(code, state)
      .then(({ tokens, user }) => {
        storeTokens(tokens);
        setUser(user);
        navigate("/dashboard", { replace: true });
      })
      .catch((err) => {
        console.error("Token exchange failed:", err);
        navigate("/login?error=exchange_failed", { replace: true });
      });
  }, [searchParams, setUser, navigate]);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-chess-dark">
      <LoadingSpinner size="lg" />
      <p className="mt-4 text-gray-400">Signing you in with Lichess…</p>
    </div>
  );
}
