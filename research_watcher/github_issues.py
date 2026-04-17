from __future__ import annotations

import httpx

from .models import Alert

GITHUB_API = "https://api.github.com"


def _headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }


def upsert_alert_issue(repo: str, token: str, alert: Alert) -> None:
    if not repo or not token:
        return

    title = f"[research-alert] {alert.title}"
    with httpx.Client(timeout=20.0) as client:
        existing = client.get(
            f"{GITHUB_API}/repos/{repo}/issues",
            headers=_headers(token),
            params={"state": "open", "labels": "research-alert", "per_page": 100},
        )
        existing.raise_for_status()
        issues = existing.json()

        match = next((issue for issue in issues if issue.get("title") == title), None)
        body = f"Severity: **{alert.severity}**\n\n{alert.body}"

        if match:
            client.patch(
                f"{GITHUB_API}/repos/{repo}/issues/{match['number']}",
                headers=_headers(token),
                json={"body": body},
            ).raise_for_status()
        else:
            client.post(
                f"{GITHUB_API}/repos/{repo}/issues",
                headers=_headers(token),
                json={"title": title, "body": body, "labels": ["research-alert", alert.severity]},
            ).raise_for_status()
