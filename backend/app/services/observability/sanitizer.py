"""Utility to strip sensitive fields from telemetry dicts before persisting.
Removes any key that matches typical secret patterns.
"""
import re
from typing import Dict, Any

_SENSITIVE_PAT = re.compile(r"(?i)(api[_-]?key|pat|token|password|secret|authorization|auth)" )

def sanitize_stage_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Return a copy of *data* with any potentially sensitive keys removed.
    The check is case‑insensitive and looks for common secret substrings.
    """
    cleaned = {}
    for k, v in data.items():
        if isinstance(k, str) and _SENSITIVE_PAT.search(k):
            continue
        # If value itself is a dict, recurse
        if isinstance(v, dict):
            cleaned[k] = sanitize_stage_data(v)
        else:
            cleaned[k] = v
    return cleaned
