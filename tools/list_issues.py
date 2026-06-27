from collections.abc import Generator
from typing import Any

import httpx
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

GITHUB_API = "https://api.github.com"


class ListIssuesTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        repo = tool_parameters.get("repo", "").strip().strip("/")
        state = tool_parameters.get("state", "open")
        labels = tool_parameters.get("labels", "").strip()
        limit = min(int(tool_parameters.get("limit", 10)), 50)

        if "/" not in repo:
            yield self.create_json_message({
                "error": 'Invalid repo format. Use "owner/repo", e.g. "langgenius/dify"',
            })
            return

        token = self.runtime.credentials.get("github_token")
        headers = {"Accept": "application/vnd.github.v3+json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        params = {"state": state, "per_page": limit, "sort": "updated", "direction": "desc"}
        if labels:
            params["labels"] = labels

        try:
            resp = httpx.get(
                f"{GITHUB_API}/repos/{repo}/issues",
                headers=headers,
                params=params,
                timeout=15,
            )
            resp.raise_for_status()
            issues = resp.json()

            results = []
            for issue in issues:
                if "pull_request" in issue:
                    continue  # skip PRs
                results.append({
                    "number": issue["number"],
                    "title": issue["title"],
                    "state": issue["state"],
                    "labels": [l["name"] for l in issue.get("labels", [])],
                    "comments": issue["comments"],
                    "created_at": issue["created_at"],
                    "updated_at": issue["updated_at"],
                    "url": issue["html_url"],
                    "author": issue["user"]["login"],
                })

            summary = f"Repository: {repo}\n"
            summary += f"Found {len(results)} issues (state: {state}):\n\n"
            for i, iss in enumerate(results, 1):
                labels_str = ", ".join(iss["labels"]) if iss["labels"] else ""
                summary += (
                    f"{i}. [#{iss['number']}] {iss['title']}\n"
                    f"   State: {iss['state']}  💬 {iss['comments']}  👤 {iss['author']}\n"
                )
                if labels_str:
                    summary += f"   Labels: {labels_str}\n"
                summary += "\n"

            yield self.create_json_message({
                "total": len(results),
                "issues": results,
                "summary": summary,
            })

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                yield self.create_json_message({
                    "error": f"Repository '{repo}' not found",
                })
            else:
                yield self.create_json_message({
                    "error": f"GitHub API error: {e.response.status_code}",
                })
