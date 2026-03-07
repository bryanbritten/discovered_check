# DiscoveredCheck

Chess analytics built for human insight — no engine required.

DiscoveredCheck is a full-stack web application that helps chess players below 2000 ELO understand their games through pattern-based analysis. It focuses on the decisions humans actually make rather than engine evaluations: how you manage time, what tactical patterns you miss, and how your results vary by color, time control, and opening.

## Features

- **Overall statistics** — win rates by color, time control, and opening
- **Missed tactics** — geometry-based detection of forks, pins, and skewers without a chess engine
- **Time analysis** — move time distribution and whether thinking longer correlates with better moves
- **Lichess sync** — import games directly from Lichess with cursor-based pagination
- **PGN import** — upload PGN files for offline or cross-platform analysis
- **Persistent sessions** — log in once; re-authentication only required when your Lichess token expires (typically after one year)

## Tech Stack

**Backend**
- Python 3.13 + Django 5 + Django REST Framework
- Poetry for dependency management
- djangorestframework-simplejwt for short-lived JWT access tokens
- python-chess for PGN parsing and board geometry analysis
- PostgreSQL

**Frontend**
- Vite + React + TypeScript
- Tailwind CSS
- TanStack Query for server state
- Recharts for data visualization
- Axios with a 401-interceptor for transparent token refresh

**Authentication**
- Lichess OAuth 2.0 with PKCE
- JWTs stored in memory only (never localStorage or cookies)
- Long-lived `dc_session` httpOnly cookie for persistent sessions across page loads

## Project Structure

```
DiscoveredCheck/
├── backend/
│   ├── apps/
│   │   ├── users/          # Auth, Lichess OAuth, persistent sessions
│   │   ├── games/          # Game and Move models
│   │   ├── analytics/      # TacticsOpportunity, GameAnalysis models
│   │   └── imports/        # PGN parsing, Lichess sync, tactics detection
│   └── config/             # Django settings (base/dev/prod)
├── frontend/
│   └── src/
│       ├── contexts/        # AuthContext (session rehydration on load)
│       ├── pages/           # LoginPage, OAuthCallback, Dashboard, analytics pages
│       └── services/        # api.ts, auth.ts, tokenStore.ts
└── .github/
    ├── workflows/           # GitHub Actions (CI, PR auto-responder)
    └── scripts/             # claude_pr_responder.py
```

## Authentication Flow

1. User clicks "Continue with Lichess" on the login page
2. App checks for a valid `dc_session` cookie first — if found, issues new JWTs silently
3. If no valid session, initiates Lichess OAuth 2.0 with PKCE
4. On successful OAuth exchange, a `dc_session` cookie is set (httpOnly, 1-year lifetime)
5. JWTs (1-hour access, 30-day refresh) live in memory only and are lost on page refresh
6. Every page load rehydrates the session from the cookie without touching Lichess
7. Logout clears in-memory tokens and user state; the cookie is preserved so the next login is silent

## Getting Started

### Prerequisites

- Python 3.13+ (via pyenv recommended)
- Node.js 20+
- PostgreSQL
- A Lichess OAuth application (register at lichess.org/account/oauth/app)

### Backend

```bash
cd backend
poetry install
cp .env.example .env   # fill in DB credentials and Lichess client details
poetry run python manage.py migrate
poetry run python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env   # set VITE_LICHESS_CLIENT_ID and VITE_OAUTH_REDIRECT_URI
npm run dev
```

## AI Usage

This project was built with significant AI assistance from Claude (Anthropic). The AI was used throughout development as a collaborative engineering partner, not just for boilerplate generation.

**Architecture and design**
The session persistence system — using an httpOnly `dc_session` cookie alongside in-memory JWTs — was designed collaboratively. The two-tier approach (short-lived tokens in memory, long-lived cookie on the server) emerged from a conversation about the tradeoffs between security and user experience.

**Bug diagnosis and fixing**
Several non-obvious bugs were identified and fixed with AI help:
- An infinite page reload caused by the 401 interceptor calling `session/resume/` when that endpoint itself returned 401 — fixed by adding an `AUTH_ENDPOINTS` exclusion list
- An auto-sign-in bug where `LoginPage` was calling `resumeSession()` on mount via `useEffect`, causing the user to be signed back in immediately after logout — fixed by moving the call to the button's click handler

**Tactics detection**
The geometry-based fork, pin, and skewer detector (`backend/apps/imports/tactics_detector.py`) was written with AI assistance. The approach — using `board.attacks()` and ray tracing through python-chess rather than an engine — was chosen specifically to avoid the infrastructure cost of running Stockfish.

**GitHub Actions automation**
The PR auto-responder (`.github/workflows/claude-pr-responder.yml` and `.github/scripts/claude_pr_responder.py`) was written with AI assistance. It uses the Anthropic API to respond to pull request comments with project-aware context. The workflow handles edge cases like preventing response loops (by checking for a `<!-- claude-auto-response -->` marker) and skipping bot comments.

**Code review and iteration**
Throughout the project, AI was used to review implementation choices, catch security issues (such as a Lichess client ID that was briefly hardcoded as a fallback in source code), and iterate on the session management design as requirements evolved.

The development approach was conversational: describing goals and constraints, reviewing generated code carefully, and pushing back when solutions were over-engineered or missed the intent.
