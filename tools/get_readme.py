from collections.abc import Generator
from typing import Any

import httpx
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

GITHUB_API = "https://api.github.com"


class GetReadmeTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        repo = tool_parameters.get("repo", "").strip().strip("/")
        if "/" not in repo:
            yield self.create_json_message({
                "error": 'Invalid repo format. Use "owner/repo", e.g. "langgenius/dify"',
            })
            return

        token = self.runtime.credentials.get("github_token")
        headers = {"Accept": "application/vnd.github.v3.raw"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        try:
            resp = httpx.get(
                f"{GITHUB_API}/repos/{repo}/readme",
                headers=headers,
                timeout=15,
            )
            resp.raise_for_status()
            markdown = resp.text

            # Also get repo info for context
            headers["Accept"] = "application/vnd.github.v3+json"
            info_resp = httpx.get(
                f"{GITHUB_API}/repos/{repo}",
                headers=headers,
                timeout=10,
            )
            repo_info = {}
            if info_resp.is_success:
                d = info_resp.json()
                repo_info = {
                    "description": d.get("description", ""),
                    "stars": d["stargazers_count"],
                    "language": d.get("language", ""),
                    "topics": d.get("topics", []),
                    "license": d.get("license", {}).get("spdx_id", "") if d.get("license") else "",
                }

            # Truncate very long README
            max_len = 15000
            truncated = len(markdown) > max_len
            content = markdown[:max_len]

            yield self.create_json_message({
                "repo": repo,
                "content": content,
                "truncated": truncated,
                "length": len(markdown),
                "repo_info": repo_info,
            })

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                yield self.create_json_message({
                    "error": f"Repository '{repo}' not found or has no README",
                })
            else:
                yield self.create_json_message({
                    "error": f"GitHub API error: {e.response.status_code}",
                })
