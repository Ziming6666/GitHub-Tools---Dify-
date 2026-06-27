from collections.abc import Generator
from typing import Any

import httpx
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

GITHUB_API = "https://api.github.com"


class GetRepoInfoTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        repo = tool_parameters.get("repo", "").strip().strip("/")
        if "/" not in repo:
            yield self.create_json_message({
                "error": 'Invalid repo format. Use "owner/repo", e.g. "langgenius/dify"',
            })
            return

        token = self.runtime.credentials.get("github_token")
        headers = {"Accept": "application/vnd.github.v3+json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        try:
            resp = httpx.get(
                f"{GITHUB_API}/repos/{repo}",
                headers=headers,
                timeout=15,
            )
            resp.raise_for_status()
            d = resp.json()

            info = {
                "name": d["full_name"],
                "description": d.get("description") or "(No description)",
                "stars": d["stargazers_count"],
                "forks": d["forks_count"],
                "open_issues": d["open_issues_count"],
                "language": d.get("language") or "N/A",
                "topics": d.get("topics", []),
                "license": d.get("license", {}).get("spdx_id", "") if d.get("license") else "N/A",
                "homepage": d.get("homepage", ""),
                "created_at": d["created_at"],
                "updated_at": d["updated_at"],
                "pushed_at": d["pushed_at"],
                "size_kb": d["size"],
                "default_branch": d["default_branch"],
                "url": d["html_url"],
                "is_archived": d.get("archived", False),
                "is_fork": d["fork"],
                "watchers": d["subscribers_count"],
            }

            # Get recent commits
            commits_resp = httpx.get(
                f"{GITHUB_API}/repos/{repo}/commits",
                headers=headers,
                params={"per_page": 3},
                timeout=10,
            )
            recent_commits = []
            if commits_resp.is_success:
                for c in commits_resp.json():
                    recent_commits.append({
                        "message": c["commit"]["message"].split("\n")[0],
                        "author": c["commit"]["author"]["name"],
                        "date": c["commit"]["author"]["date"],
                        "url": c["html_url"],
                    })

            info["recent_commits"] = recent_commits

            summary = (
                f"## {info['name']}\n\n"
                f"{info['description']}\n\n"
                f"⭐ **{info['stars']:,}** stars  🍴 **{info['forks']:,}** forks  "
                f"👀 **{info['watchers']:,}** watchers\n"
                f"🔤 Language: {info['language']}\n"
                f"📝 License: {info['license']}\n"
                f"🐛 Open Issues: {info['open_issues']}\n"
                f"🌐 Homepage: {info['homepage'] or 'N/A'}\n"
                f"📦 Size: {info['size_kb']} KB\n"
                f"🌿 Default Branch: {info['default_branch']}\n"
                f"📅 Created: {info['created_at'][:10]}\n"
                f"🔄 Last Push: {info['pushed_at'][:10]}\n"
                f"🏷️ Topics: {', '.join(info['topics']) if info['topics'] else 'N/A'}\n"
                f"🔗 URL: {info['url']}\n"
            )

            if info["is_archived"]:
                summary += "\n⚠️ **This repository is archived and read-only.**\n"

            if recent_commits:
                summary += "\n### Recent Commits\n"
                for c in recent_commits:
                    summary += f"- [{c['date'][:10]}] {c['message']} — {c['author']}\n"

            yield self.create_json_message({
                "info": info,
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
