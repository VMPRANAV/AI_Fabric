import re
from typing import Tuple, Dict

# Task type index mappings
TASK_TYPE_MAP: Dict[str, int] = {
    "sql_analysis_optimization": 0,
    "repo_architecture": 1,
    "code_generation": 2,
    "general_reasoning": 3
}

# Tool type index mappings
TOOL_TYPE_MAP: Dict[str, int] = {
    "none": 0,
    "github_mcp": 1,
    "database_mcp": 2
}

# Keyword regex patterns for deterministic rule-based matching
SQL_KEYWORDS = re.compile(r"\b(sql|query|explain|index|join|select|insert|update|delete|table|schema|database|postgres|mysql|sqlite)\b", re.IGNORECASE)
REPO_KEYWORDS = re.compile(r"\b(repo|repository|github|file structure|directory|modules|architecture|codebase|commit|branch|pr|dependencies|package\.json)\b", re.IGNORECASE)
CODE_KEYWORDS = re.compile(r"\b(write|create|implement|function|class|script|api|endpoint|code|python|typescript|javascript|react|html|css)\b", re.IGNORECASE)

def classify_task_and_tool(query_text: str, category_hint: str = None) -> Tuple[str, int, bool, str, int]:
    """
    Deterministic rule-based task classification and tool requirement detection.
    
    Returns:
        (task_type, task_type_idx, tool_required, tool_type, tool_type_idx)
    """
    text = query_text.lower()
    
    # Honor category hint if provided by Prompt Gateway
    if category_hint:
        if "sql" in category_hint:
            return "sql_analysis_optimization", 0, True, "github_mcp", 1
        elif "repo" in category_hint:
            return "repo_architecture", 1, True, "github_mcp", 1

    sql_match = bool(SQL_KEYWORDS.search(text))
    repo_match = bool(REPO_KEYWORDS.search(text))
    code_match = bool(CODE_KEYWORDS.search(text))
    
    if sql_match and ("optimize" in text or "slow" in text or "explain" in text or repo_match):
        task_type = "sql_analysis_optimization"
        task_idx = 0
        tool_required = True
        tool_type = "github_mcp" if repo_match or "github" in text else "database_mcp"
        tool_idx = TOOL_TYPE_MAP[tool_type]
    elif repo_match or "github" in text or "repository" in text:
        task_type = "repo_architecture"
        task_idx = 1
        tool_required = True
        tool_type = "github_mcp"
        tool_idx = 1
    elif sql_match:
        task_type = "sql_analysis_optimization"
        task_idx = 0
        tool_required = True
        tool_type = "database_mcp"
        tool_idx = 2
    elif code_match and ("write" in text or "generate" in text or "implement" in text):
        task_type = "code_generation"
        task_idx = 2
        tool_required = False
        tool_type = "none"
        tool_idx = 0
    else:
        task_type = "general_reasoning"
        task_idx = 3
        tool_required = False
        tool_type = "none"
        tool_idx = 0

    return task_type, task_idx, tool_required, tool_type, tool_idx
