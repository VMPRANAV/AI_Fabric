from typing import Dict, Any, List, Optional
from app.schemas.mcp import MCPServerInfo, MCPToolInfo

class MCPServerRegistry:
    def __init__(self):
        self._servers: Dict[str, Dict[str, Any]] = {}
        self._register_default_servers()

    def _register_default_servers(self):
        self.register_server(
            server_id="github_mcp",
            name="GitHub MCP Server",
            server_type="github",
            status="healthy",
            tools=[
                "list_files",
                "get_file",
                "search_code",
                "get_repo_structure"
            ]
        )

    def register_server(
        self,
        server_id: str,
        name: str,
        server_type: str,
        status: str = "healthy",
        tools: List[str] = None
    ):
        self._servers[server_id] = {
            "server_id": server_id,
            "name": name,
            "type": server_type,
            "status": status,
            "tools": tools or []
        }

    def get_server(self, server_id: str) -> Optional[Dict[str, Any]]:
        return self._servers.get(server_id)

    def list_servers(self) -> List[MCPServerInfo]:
        return [
            MCPServerInfo(
                server_id=s["server_id"],
                name=s["name"],
                type=s["type"],
                status=s["status"],
                tools=s["tools"]
            )
            for s in self._servers.values()
        ]

mcp_server_registry = MCPServerRegistry()
