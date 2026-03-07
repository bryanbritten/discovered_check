#!/usr/bin/env python3
"""
Respond to PR comments automatically using the Claude API.

Triggered by GitHub Actions on pull_request_review_comment and issue_comment events.
Skips responses that contain the auto-response marker to prevent reply loops.
"""

import json
import os
import sys

import anthropic
import requests

# Hidden HTML comment appended to every automated reply to prevent response loops.
MARKER = "<!-- claude-auto-response -->"

REPO_CONTEXT = """
DiscoveredCheck is a human-centered chess analytics web app targeting players below 2000 ELO.

Tech stack:
- Backend: Django 5 + Django REST Framework, Poetry, Python 3.13
- Frontend: Vite + React + TypeScript, Tailwind CSS, Recharts, TanStack Query
- Auth: Lichess OAuth 2.0 with PKCE (no username/password)

Apps:
- users: Custom User model, LichessToken, OAuth exchange view
- games: Game (UUID PK, source, color, result, time control, PGN) + Move (per-ply clock/time data)
- analytics: TacticsOpportunity (fork/pin/skewer via board geometry, no engine),
             MoveTimeCategory, GameAnalysis with overview/tactics/time APIs
- imports: PGNImport, LichessSync, pgn_parser.py, tactics_detector.py, lichess_client.py

Key design decisions:
- Tactics detected purely from piece geometry (python-chess), no engine required
- Time categories: instant (<2s), quick (2-10s), normal (10-30s), considered (30-60s), long_think (>60s)
- Lichess sync uses cursor-based pagination via since_timestamp
""".strip()


def get_headers(token: str) -> dict:
    return {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}


def get_pr_context(repo: str, pr_number: int, token: str) -> dict:
    headers = get_headers(token)

    pr = requests.get(
        f"https://api.github.com/repos/{repo}/pulls/{pr_number}",
        headers=headers,
        timeout=10,
    ).json()

    diff_resp = requests.get(
        f"https://api.github.com/repos/{repo}/pulls/{pr_number}",
        headers={**headers, "Accept": "application/vnd.github.v3.diff"},
        timeout=10,
    )
    diff = diff_resp.text[:6000] if diff_resp.ok else ""

    return {
        "title": pr.get("title", ""),
        "body": pr.get("body", ""),
        "diff": diff,
    }


def post_review_comment_reply(repo: str, comment_id: int, pr_number: int, body: str, token: str) -> bool:
    resp = requests.post(
        f"https://api.github.com/repos/{repo}/pulls/{pr_number}/comments/{comment_id}/replies",
        headers=get_headers(token),
        json={"body": body},
        timeout=10,
    )
    return resp.ok


def post_issue_comment(repo: str, issue_number: int, body: str, token: str) -> bool:
    resp = requests.post(
        f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments",
        headers=get_headers(token),
        json={"body": body},
        timeout=10,
    )
    return resp.ok


def build_system_prompt(pr_number: int, pr_ctx: dict, commenter: str, file_path: str, diff_hunk: str) -> str:
    parts = [
        f"You are an AI coding assistant reviewing PR #{pr_number} in the DiscoveredCheck repository.",
        "",
        REPO_CONTEXT,
        "",
        f"PR title: {pr_ctx['title']}",
        f"PR description:\n{pr_ctx['body'] or '(none)'}",
    ]

    if file_path:
        parts.append(f"\nFile being commented on: {file_path}")
    if diff_hunk:
        parts.append(f"\nCode context (diff hunk):\n```\n{diff_hunk}\n```")
    if pr_ctx["diff"]:
        parts.append(f"\nFull PR diff (truncated to 6000 chars):\n```diff\n{pr_ctx['diff']}\n```")

    parts += [
        "",
        f"You are replying to a comment left by @{commenter}.",
        "Be helpful, direct, and concise. Do not be sycophantic. Use markdown where appropriate.",
    ]

    return "\n".join(parts)


def main() -> None:
    token = os.environ["GITHUB_TOKEN"]
    api_key = os.environ["ANTHROPIC_API_KEY"]
    repo = os.environ["GITHUB_REPOSITORY"]
    event_name = os.environ["GITHUB_EVENT_NAME"]
    event_path = os.environ["GITHUB_EVENT_PATH"]

    with open(event_path) as f:
        event = json.load(f)

    comment = event["comment"]
    comment_body: str = comment["body"]
    comment_id: int = comment["id"]
    commenter: str = comment["user"]["login"]

    # Prevent reply loops — skip any comment we already auto-generated.
    if MARKER in comment_body:
        print("Skipping: auto-response marker detected.")
        return

    # Skip comments from bots.
    if comment["user"]["type"] == "Bot":
        print(f"Skipping: commenter {commenter!r} is a bot.")
        return

    if event_name == "pull_request_review_comment":
        pr_number: int = event["pull_request"]["number"]
        diff_hunk: str = comment.get("diff_hunk", "")
        file_path: str = comment.get("path", "")
        is_review_comment = True
    else:
        # issue_comment — make sure it's on a PR, not a plain issue.
        if "pull_request" not in event.get("issue", {}):
            print("Skipping: issue_comment not on a pull request.")
            return
        pr_number = event["issue"]["number"]
        diff_hunk = ""
        file_path = ""
        is_review_comment = False

    pr_ctx = get_pr_context(repo, pr_number, token)

    system_prompt = build_system_prompt(pr_number, pr_ctx, commenter, file_path, diff_hunk)

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": comment_body}],
    )

    reply = message.content[0].text + f"\n\n{MARKER}"

    if is_review_comment:
        success = post_review_comment_reply(repo, comment_id, pr_number, reply, token)
    else:
        success = post_issue_comment(repo, pr_number, reply, token)

    if success:
        print("Reply posted successfully.")
    else:
        print("ERROR: Failed to post reply.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
