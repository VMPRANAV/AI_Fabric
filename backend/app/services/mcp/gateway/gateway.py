import time
import asyncio
from typing import Dict, Any, Optional

from app.core.config import settings
from app.services.mcp.gateway.validator import mcp_validator
from app.services.mcp.gateway.errors import (
    RepositoryNotAllowedError,
    ToolNotFoundError,
    InvalidInputError,
    TimeoutError,
    InternalError,
)
from app.services.mcp.gateway.telemetry import mcp_telemetry
from app.services.mcp.gateway.registry import mcp_server_registry
from app.models import MCPToolExecutionRecord
from app.schemas.mcp import MCPExecuteRequest, NormalizedToolResult

# Import server implementations
from app.services.mcp.servers.github.server import GitHubMCPServer
from app.services.mcp.servers.mock_server import MockGitHubMCPServer

class MCPGatewayService:
    """Core MCP Gateway.

    - Validates server, tool, repository allowlist, and input schema.
    - Accepts an optional pre‑selected ``tool_name`` (for future PPO) – if provided, it skips deterministic selection.
    - Executes the tool on the appropriate provider (live GitHub or deterministic mock).
    - Normalizes result into ``NormalizedToolResult``.
    - Records telemetry and persists an ``MCPToolExecutionRecord``.
    """

    def __init__(self):
        # Server instances – lazily instantiated when first used.
        self._live_server: Optional[GitHubMCPServer] = None
        self._mock_server: Optional[MockGitHubMCPServer] = None

    def _get_server(self, server_id: str):
        if server_id != "github_mcp":
            raise ToolNotFoundError(f"Server '{server_id}' is not supported.")
        if settings.MCP_PROVIDER == "github":
            if not self._live_server:
                self._live_server = GitHubMCPServer()
            return self._live_server
        else:
            if not self._mock_server:
                self._mock_server = MockGitHubMCPServer()
            return self._mock_server

    async def execute(
        self,
        request: MCPExecuteRequest,
        request_id: Optional[str] = None,
        preselected_tool: Optional[str] = None,
    ) -> NormalizedToolResult:
        """Execute an MCP tool.

        Parameters
        ----------
        request: MCPExecuteRequest – validated by FastAPI (contains server, tool, arguments).
        request_id: optional – DB request identifier for telemetry.
        preselected_tool: optional – tool name supplied by a future PPO Decision Engine.
        """
        server_id = request.server
        tool_name = preselected_tool or request.tool

        # 1️⃣ Validate server registration
        server_info = mcp_server_registry.get_server(server_id)
        if not server_info:
            raise ToolNotFoundError(f"MCP server '{server_id}' is not registered.")

        # 2️⃣ Validate tool allowlist (both server & tool)
        mcp_validator.validate_tool_allowlist(server_id, tool_name)

        # 3️⃣ Validate input payload against the tool's Pydantic schema & repo allowlist
        validated_args, repo_full = mcp_validator.validate_tool_input(tool_name, request.arguments)

        # 4️⃣ Dispatch to the concrete server implementation
        server_impl = self._get_server(server_id)
        exec_coro = getattr(server_impl, tool_name)(validated_args)

        start = time.time()
        try:
            raw_result = await asyncio.wait_for(exec_coro, timeout=settings.MCP_TOOL_TIMEOUT_SECONDS)
            success = True
            error_type = None
        except asyncio.TimeoutError:
            success = False
            raw_result = {}
            error_type = "timeout"
        except Exception as exc:
            # Convert any raised custom MCPError into a normalized response.
            success = False
            raw_result = {}
            error_type = getattr(exc, "error_type", "internal_error")
        end = time.time()

        # 5️⃣ Normalization into common schema
        normalized = NormalizedToolResult(
            success=success,
            server=server_id,
            tool=tool_name,
            execution_time_ms=round((end - start) * 1000, 2),
            result=raw_result if success else {},
            metadata={"repository": repo_full} if repo_full else {},
            error_type=error_type,
        )

        # 6️⃣ Telemetry & DB persistence (ignore DB errors for now)
        telemetry = mcp_telemetry.record_execution(
            request_id=request_id,
            server=server_id,
            tool=tool_name,
            repository=repo_full,
            start_time=start,
            end_time=end,
            success=success,
            error_type=error_type,
            response_size=len(str(raw_result).encode()),
        )
        try:
            record = MCPToolExecutionRecord(
                request_id=request_id,
                server_name=server_id,
                tool_name=tool_name,
                repository=repo_full,
                execution_time_ms=telemetry["execution_time_ms"],
                success=success,
                error_type=error_type,
            )
            # The DB session is injected via FastAPI Depends in the endpoint; here we only create the object.
            # The endpoint will add it to the session.
        except Exception:
            # Fail‑safe – we never raise DB errors from the gateway.
            pass

        return normalized

# Instantiate a singleton for FastAPI DI
mcp_gateway_service = MCPGatewayService()
