import time
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("mcp_gateway")

class MCPTelemetry:
    @staticmethod
    def record_execution(
        request_id: Optional[str],
        server: str,
        tool: str,
        repository: Optional[str],
        start_time: float,
        end_time: float,
        success: bool,
        error_type: Optional[str] = None,
        response_size: int = 0
    ) -> Dict[str, Any]:
        execution_time_ms = round((end_time - start_time) * 1000, 2)
        telemetry_data = {
            "request_id": request_id,
            "server": server,
            "tool": tool,
            "repository": repository,
            "execution_time_ms": execution_time_ms,
            "success": success,
            "error_type": error_type,
            "response_size_bytes": response_size,
            "timestamp": time.time()
        }

        # Safe logging without tokens/auth/sensitive code
        logger.info(
            f"[MCP Telemetry] Server={server} Tool={tool} Repo={repository} "
            f"Success={success} Latency={execution_time_ms}ms Size={response_size}B Error={error_type}"
        )
        return telemetry_data

mcp_telemetry = MCPTelemetry()
