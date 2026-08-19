import re
import unicodedata
from typing import List, Tuple, Literal
from app.schemas.prompt import PromptValidationResponse

# Guardrail pattern definitions
HIGH_RISK_PATTERNS = [
    (r"ignore\s+(all\s+)?(previous|prior)\s+(instructions|directives|prompts)", "Attempted instruction override / prompt injection"),
    (r"(you\s+are\s+now\s+.*(unrestricted|dan|developer|god)\s+mode|\bdan\s+mode\b)", "Attempted jailbreak persona activation"),
    (r"reveal\s+(your\s+)?(system\s+prompt|hidden\s+instructions|master\s+keys)", "Attempted system prompt extraction"),
    (r"system\s*:\s*override", "Attempted system role spoofing"),
    (r"disregard\s+(all\s+)?safety\s+(rules|protocols|filters)", "Attempted safety guardrail bypass"),
]

SUSPICIOUS_PATTERNS = [
    (r"base64\s+decode\s+and\s+execute", "Suspicious obfuscated payload execution pattern"),
    (r"sudo\s+rm\s+-rf\s+/", "Potentially destructive root filesystem command"),
    (r"drop\s+database\s+[a-zA-Z0-9_]+", "Potentially destructive database drop statement"),
]

def normalize_prompt_text(text: str) -> str:
    """
    Normalizes prompt text:
    - Applies Unicode NFKC normalization
    - Strips non-printable ASCII control characters (preserving newline, tab, carriage return)
    - Normalizes excessive whitespace and consecutive blank lines
    """
    if not text:
        return ""
    
    # Unicode NFKC normalization
    normalized = unicodedata.normalize("NFKC", text)
    
    # Strip invisible/unprintable control characters except \n, \r, \t
    normalized = "".join(ch for ch in normalized if ch in ("\n", "\r", "\t") or (ord(ch) >= 32 and ord(ch) != 127))
    
    # Normalize multiple blank lines to a single blank line
    normalized = re.sub(r"\n\s*\n\s*\n+", "\n\n", normalized)
    
    # Trim leading/trailing whitespace
    return normalized.strip()

def validate_and_check_safety(
    text: str,
    min_length: int = 3,
    max_length: int = 10000
) -> PromptValidationResponse:
    """
    Executes first-stage Prompt Gateway validation and guardrail checks.
    """
    normalized = normalize_prompt_text(text)
    violations: List[str] = []
    is_valid = True
    risk_level: Literal["low", "medium", "high"] = "low"
    
    char_count = len(normalized)
    
    # Bounds validation
    if char_count < min_length:
        is_valid = False
        violations.append(f"Prompt length ({char_count} chars) is below the minimum required ({min_length} chars).")
    
    if char_count > max_length:
        is_valid = False
        violations.append(f"Prompt length ({char_count} chars) exceeds the maximum allowed limit ({max_length} chars).")
        risk_level = "medium"

    # High-Risk Guardrail Checks
    for pattern, reason in HIGH_RISK_PATTERNS:
        if re.search(pattern, normalized, re.IGNORECASE):
            violations.append(reason)
            risk_level = "high"

    # Suspicious / Medium-Risk Checks
    for pattern, reason in SUSPICIOUS_PATTERNS:
        if re.search(pattern, normalized, re.IGNORECASE):
            violations.append(reason)
            if risk_level != "high":
                risk_level = "medium"

    is_safe = (risk_level != "high")

    return PromptValidationResponse(
        is_valid=is_valid,
        is_safe=is_safe,
        risk_level=risk_level,
        violations=violations,
        normalized_query=normalized,
        character_count=char_count
    )
