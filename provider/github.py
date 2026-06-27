from typing import Any

import httpx
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class GitHubProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        token = credentials.get("github_token")
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        try:
            resp = httpx.get(
                "https://api.github.com/",
                headers=headers,
                timeout=10,
            )
            if resp.status_code == 403:
                raise ToolProviderCredentialValidationError(
                    "API rate limit exceeded or token invalid"
                )
            if resp.status_code == 401:
                raise ToolProviderCredentialValidationError("Token is invalid")
        except httpx.RequestError as e:
            raise ToolProviderCredentialValidationError(
                f"Failed to connect to GitHub API: {str(e)}"
            ) from e
