from typing import Dict, Any

class MCPError(Exception):
    def __init__(self, error_type: str, message: str, status_code: int = 400):
        super().__init__(message)
        self.error_type = error_type
        self.message = message
        self.status_code = status_code

class AuthenticationError(MCPError):
    def __init__(self, message: str = "GitHub authentication failed or missing token."):
        super().__init__("authentication_error", message, 401)

class RepositoryNotAllowedError(MCPError):
    def __init__(self, message: str = "Repository is not allowlisted."):
        super().__init__("repository_not_allowed", message, 403)

class RepositoryNotFoundError(MCPError):
    def __init__(self, message: str = "Repository not found."):
        super().__init__("repository_not_found", message, 404)

class PermissionDeniedError(MCPError):
    def __init__(self, message: str = "Permission denied for target repository."):
        super().__init__("permission_denied", message, 403)

class ToolNotFoundError(MCPError):
    def __init__(self, message: str = "Requested MCP tool is not found or not registered."):
        super().__init__("tool_not_found", message, 404)

class InvalidInputError(MCPError):
    def __init__(self, message: str = "Invalid tool arguments or input schema violation."):
        super().__init__("invalid_input", message, 400)

class TimeoutError(MCPError):
    def __init__(self, message: str = "MCP tool execution timed out."):
        super().__init__("timeout", message, 504)

class RateLimitError(MCPError):
    def __init__(self, message: str = "GitHub API rate limit exceeded."):
        super().__init__("rate_limit", message, 429)

class GitHubAPIError(MCPError):
    def __init__(self, message: str = "GitHub API returned an error."):
        super().__init__("github_api_error", message, 502)

class InternalError(MCPError):
    def __init__(self, message: str = "Internal MCP Gateway error occurred."):
        super().__init__("internal_error", message, 500)

def normalize_error(error_type: str, message: str, server: str = "github_mcp", tool: str = "unknown", execution_time_ms: float = 0.0) -> Dict[str, Any]:
    return {
        "success": False,
        "server": server,
        "tool": tool,
        "execution_time_ms": round(execution_time_ms, 2),
        "result": {},
        "metadata": {},
        "error_type": error_type,
        "message": message
    }
