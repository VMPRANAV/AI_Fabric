import httpx
from typing import Any, Dict, List, Optional
from app.core.config import settings
from app.services.mcp.gateway.errors import AuthenticationError, RateLimitError, GitHubAPIError

class GitHubClient:
    BASE_URL = "https://api.github.com"

    def __init__(self):
        token = settings.GITHUB_TOKEN
        if not token:
            raise AuthenticationError()
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AI-Fabric-MCP-Client"
        }
        self.client = httpx.AsyncClient(base_url=self.BASE_URL, headers=self.headers, timeout=10)

    async def _handle_response(self, response: httpx.Response) -> Any:
        if response.status_code == 401:
            raise AuthenticationError("Invalid or missing GitHub token.")
        if response.status_code == 403 and "rate limit" in response.text.lower():
            raise RateLimitError()
        if response.status_code >= 400:
            raise GitHubAPIError(f"GitHub API error {response.status_code}: {response.text}")
        return response.json()

    async def list_path(self, owner: str, repo: str, path: str = "", branch: str = "main") -> List[Dict[str, Any]]:
        url = f"/repos/{owner}/{repo}/contents/{path}" if path else f"/repos/{owner}/{repo}/contents"
        params = {"ref": branch}
        resp = await self.client.get(url, params=params)
        data = await self._handle_response(resp)
        return data if isinstance(data, list) else [data]

    async def get_file_content(self, owner: str, repo: str, path: str, branch: str = "main") -> Dict[str, Any]:
        url = f"/repos/{owner}/{repo}/contents/{path}"
        params = {"ref": branch}
        resp = await self.client.get(url, params=params)
        return await self._handle_response(resp)

    async def search_code(self, owner: str, repo: str, query: str, path: Optional[str] = None, branch: Optional[str] = None) -> Dict[str, Any]:
        q = f"{query} repo:{owner}/{repo}"
        if path:
            q += f" path:{path}"
        if branch:
            q += f" branch:{branch}"
        params = {"q": q, "per_page": 10}
        resp = await self.client.get("/search/code", params=params)
        return await self._handle_response(resp)

    async def get_repo_structure(self, owner: str, repo: str, branch: str = "main", max_items: int = 200) -> Dict[str, Any]:
        url = f"/repos/{owner}/{repo}/git/trees/{branch}"
        params = {"recursive": "1"}
        resp = await self.client.get(url, params=params)
        data = await self._handle_response(resp)
        tree = data.get("tree", [])[:max_items]
        return {"tree": tree}

    async def close(self):
        await self.client.aclose()
