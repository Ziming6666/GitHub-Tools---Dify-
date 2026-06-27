from collections.abc import Generator
from typing import Any

import httpx
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

GITHUB_API = "https://api.github.com"


class SearchReposTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        query = tool_parameters.get("query", "")
        sort = tool_parameters.get("sort", "stars")
        limit = min(int(tool_parameters.get("limit", 5)), 20)

        token = self.runtime.credentials.get("github_token")
        headers = {"Accept": "application/vnd.github.v3+json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        params = {"q": query, "sort": sort, "per_page": limit, "order": "desc"}

        resp = httpx.get(
            f"{GITHUB_API}/search/repositories",
            headers=headers,
            params=params,
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()

        results = []
        for repo in data.get("items", []):
            results.append({
                "name": repo["full_name"],
                "description": repo.get("description") or "(No description)",
                "stars": repo["stargazers_count"],
                "forks": repo["forks_count"],
                "language": repo.get("language") or "N/A",
                "url": repo["html_url"],
                "topics": repo.get("topics", []),
                "updated_at": repo.get("updated_at", ""),
            })

        summary = f"Found {data.get('total_count', 0)} repositories. Showing top {len(results)}:\n\n"
        for i, r in enumerate(results, 1):
            summary += (
                f"{i}. [{r['name']}]({r['url']})\n"
                f"   ⭐ {r['stars']}  🍴 {r['forks']}  🔤 {r['language']}\n"
                f"   {r['description']}\n\n"
            )

        yield self.create_json_message({
            "total_count": data.get("total_count", 0),
            "results": results,
            "summary": summary,
        })
