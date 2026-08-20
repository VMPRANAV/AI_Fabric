from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator

class ListFilesRequest(BaseModel):
    owner: str = Field(..., description="Repository owner/username")
    repo: str = Field(..., description="Repository name")
    path: str = Field(default="", description="Subdirectory path within repository")
    branch: str = Field(default="main", description="Branch name")

    @field_validator("owner", "repo")
    @classmethod
    def validate_names(cls, v: str) -> str:
        if not v or "/" in v or "\\" in v:
            raise ValueError("Invalid repository or owner name")
        return v.strip()

    @field_validator("path")
    @classmethod
    def validate_path(cls, v: str) -> str:
        if ".." in v or v.startswith("/"):
            raise ValueError("Path traversal forbidden")
        return v.strip()


class GetFileRequest(BaseModel):
    owner: str = Field(..., description="Repository owner/username")
    repo: str = Field(..., description="Repository name")
    path: str = Field(..., description="File path within repository")
    branch: str = Field(default="main", description="Branch name")

    @field_validator("owner", "repo")
    @classmethod
    def validate_names(cls, v: str) -> str:
        if not v or "/" in v or "\\" in v:
            raise ValueError("Invalid repository or owner name")
        return v.strip()

    @field_validator("path")
    @classmethod
    def validate_path(cls, v: str) -> str:
        if not v or ".." in v or v.startswith("/"):
            raise ValueError("Path traversal forbidden")
        return v.strip()


class SearchCodeRequest(BaseModel):
    owner: str = Field(..., description="Repository owner/username")
    repo: str = Field(..., description="Repository name")
    query: str = Field(..., description="Search query/pattern")
    path: Optional[str] = Field(default=None, description="Path prefix to filter search")
    branch: Optional[str] = Field(default=None, description="Branch name")

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        if not v or len(v.strip()) < 2:
            raise ValueError("Query string must be at least 2 characters long")
        return v.strip()

    @field_validator("path")
    @classmethod
    def validate_path(cls, v: Optional[str]) -> Optional[str]:
        if v and (".." in v or v.startswith("/")):
            raise ValueError("Path traversal forbidden")
        return v.strip() if v else v


class GetRepoStructureRequest(BaseModel):
    owner: str = Field(..., description="Repository owner/username")
    repo: str = Field(..., description="Repository name")

    @field_validator("owner", "repo")
    @classmethod
    def validate_names(cls, v: str) -> str:
        if not v or "/" in v or "\\" in v:
            raise ValueError("Invalid repository or owner name")
        return v.strip()


class MCPExecuteRequest(BaseModel):
    server: str = Field(..., description="MCP Server ID (e.g., github_mcp)")
    tool: str = Field(..., description="MCP Tool ID (e.g., search_code)")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Arguments for tool execution")


class NormalizedToolResult(BaseModel):
    success: bool
    server: str
    tool: str
    execution_time_ms: float
    result: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    error_type: Optional[str] = None
    message: Optional[str] = None


class MCPServerInfo(BaseModel):
    server_id: str
    name: str
    type: str
    status: str
    tools: List[str]


class MCPToolInfo(BaseModel):
    tool_id: str
    server_id: str
    name: str
    description: str
    allowlisted: bool
