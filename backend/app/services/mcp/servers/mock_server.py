import os
from pathlib import Path
from typing import Dict, List

# Deterministic mock repository structure used for tests and offline mode
# Directory layout (relative to this file):
# mock_repository/
#   README.md
#   backend/
#     app.py
#     database.py
#     queries.py   (contains an inefficient SQL query)
#   frontend/
#     src/
#       App.tsx

BASE_DIR = Path(__file__).resolve().parent
MOCK_ROOT = BASE_DIR / "mock_repository"

class MockGitHubMCPServer:
    """Mock implementation of the GitHub MCP server. All methods operate on the
    static local fixture under ``mock_repository``. No network calls are made.
    """

    def __init__(self):
        if not MOCK_ROOT.exists():
            raise FileNotFoundError(f"Mock repository not found at {MOCK_ROOT}")

    def _abs_path(self, *parts: str) -> Path:
        return MOCK_ROOT.joinpath(*parts)

    async def list_files(self, args: dict) -> dict:
        path = args.get("path", "")
        abs_path = self._abs_path(path)
        if not abs_path.is_dir():
            return []
        items = []
        for entry in abs_path.iterdir():
            if entry.is_dir():
                items.append({"name": entry.name, "type": "directory", "path": str(Path(path) / entry.name)})
            else:
                items.append({"name": entry.name, "type": "file", "path": str(Path(path) / entry.name)})
        return items

    async def get_file(self, args: dict) -> dict:
        path = args["path"]
        abs_path = self._abs_path(path)
        if not abs_path.is_file():
            raise FileNotFoundError("File not found in mock repository")
        # Enforce a modest max size (e.g., 1 MB) – the mock files are tiny.
        content_bytes = abs_path.read_bytes()
        if len(content_bytes) > 1_000_000:
            raise ValueError("File size exceeds allowed maximum")
        return {
            "content": content_bytes.decode("utf-8", errors="replace"),
            "encoding": "utf-8",
        }

    async def search_code(self, args: dict) -> dict:
        query = args["query"].lower()
        path_prefix = args.get("path")
        matches = []
        # Walk the mock tree and greedily search for the query string.
        for root, _, files in os.walk(MOCK_ROOT):
            rel_root = os.path.relpath(root, MOCK_ROOT)
            if path_prefix and not rel_root.startswith(path_prefix):
                continue
            for fname in files:
                fpath = Path(root) / fname
                text = fpath.read_text(errors="ignore").lower()
                if query in text:
                    # Find first line containing the query for snippet.
                    line_no = 1
                    snippet = ""
                    for line in text.splitlines():
                        if query in line:
                            line_no = line_no
                            snippet = line.strip()
                            break
                        line_no += 1
                    matches.append({"path": str(Path(rel_root) / fname), "line": line_no, "snippet": snippet})
        # Limit matches to a reasonable number.
        return {"matches": matches[:20]}

    async def get_repo_structure(self, args: dict) -> dict:
        # Produce a simple flat list of directories (max depth 2) for demo.
        structure = []
        for root, dirs, _ in os.walk(MOCK_ROOT):
            rel = os.path.relpath(root, MOCK_ROOT)
            if rel == ".":
                continue
            # Add directory path with trailing slash
            structure.append(rel + "/")
            # Avoid deep recursion for mock simplicity
            if rel.count(os.sep) >= 2:
                continue
        return {"structure": sorted(structure)[:50]}
