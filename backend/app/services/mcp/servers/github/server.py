from app.services.mcp.servers.github.client import GitHubClient

class GitHubMCPServer:
    """Live GitHub MCP Server exposing the four allowed tools."""

    def __init__(self):
        self.client = GitHubClient()

    async def list_files(self, args: dict) -> dict:
        return await self.client.list_path(
            owner=args["owner"], repo=args["repo"], path=args.get("path", ""), branch=args.get("branch", "main")
        )

    async def get_file(self, args: dict) -> dict:
        return await self.client.get_file_content(
            owner=args["owner"], repo=args["repo"], path=args["path"], branch=args.get("branch", "main")
        )

    async def search_code(self, args: dict) -> dict:
        return await self.client.search_code(
            owner=args["owner"],
            repo=args["repo"],
            query=args["query"],
            path=args.get("path"),
            branch=args.get("branch"),
        )

    async def get_repo_structure(self, args: dict) -> dict:
        return await self.client.get_repo_structure(
            owner=args["owner"], repo=args["repo"], branch=args.get("branch", "main")
        )

    async def close(self):
        await self.client.close()
