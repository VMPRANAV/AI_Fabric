from typing import Dict, Any, Tuple
from pydantic import ValidationError
from app.core.config import settings
from app.services.mcp.gateway.errors import (
    RepositoryNotAllowedError,
    ToolNotFoundError,
    InvalidInputError,
)
from app.schemas.mcp import (
    ListFilesRequest,
    GetFileRequest,
    SearchCodeRequest,
    GetRepoStructureRequest,
)

TOOL_SCHEMA_MAP = {
    "list_files": ListFilesRequest,
    "get_file": GetFileRequest,
    "search_code": SearchCodeRequest,
    "get_repo_structure": GetRepoStructureRequest,
}

class MCPValidator:
    @staticmethod
    def validate_repository_allowlist(owner: str, repo: str) -> str:
        full_repo = f"{owner.strip()}/{repo.strip()}".lower()
        if settings.GITHUB_ALLOW_ALL:
            return full_repo

        allowed_raw = settings.GITHUB_ALLOWED_REPOS or ""
        allowed_list = [r.strip().lower() for r in allowed_raw.split(",") if r.strip()]
        
        if full_repo not in allowed_list:
            raise RepositoryNotAllowedError(f"Repository '{full_repo}' is not in the allowlist.")
        return full_repo

    @staticmethod
    def validate_tool_allowlist(server_id: str, tool_name: str) -> str:
        full_tool_key = f"{server_id}.{tool_name}"
        allowed_tools = settings.ALLOWED_MCP_TOOLS or []
        if full_tool_key not in allowed_tools:
            raise ToolNotFoundError(f"Tool '{full_tool_key}' is not in the allowed MCP tools list.")
        return full_tool_key

    @staticmethod
    def validate_tool_input(tool_name: str, arguments: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        schema_class = TOOL_SCHEMA_MAP.get(tool_name)
        if not schema_class:
            raise ToolNotFoundError(f"Tool '{tool_name}' schema is not defined.")

        try:
            validated_obj = schema_class(**arguments)
            validated_dict = validated_obj.model_dump()
        except ValidationError as ve:
            errors = [f"{e['loc']}: {e['msg']}" for e in ve.errors()]
            raise InvalidInputError(f"Tool input validation failed: {'; '.join(errors)}")
        except ValueError as ve:
            raise InvalidInputError(str(ve))

        # Check owner and repo allowlist
        owner = validated_dict.get("owner", "")
        repo = validated_dict.get("repo", "")
        if owner and repo:
            full_repo = MCPValidator.validate_repository_allowlist(owner, repo)
        else:
            full_repo = ""

        # Additional path traversal verification
        path = validated_dict.get("path")
        if path and (".." in str(path) or str(path).startswith("/")):
            raise InvalidInputError("Path traversal strictly forbidden.")

        return validated_dict, full_repo

mcp_validator = MCPValidator()
