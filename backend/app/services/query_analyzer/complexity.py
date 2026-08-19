import re
from typing import Dict, Tuple

def compute_complexity_and_reasoning(query_text: str, task_type: str) -> Tuple[float, Dict[str, float], str, int]:
    """
    Computes a deterministic, explainable complexity score in [0.0, 1.0] and
    determines the reasoning requirement level.
    
    Returns:
        (complexity_score, complexity_factors, reasoning_required, reasoning_idx)
    """
    text = query_text.strip()
    text_lower = text.lower()
    
    # 1. Length Factor (Normalized up to 500 characters)
    length_factor = min(1.0, len(text) / 500.0)
    
    # 2. SQL Complexity Signal
    sql_keywords = ["join", "group by", "order by", "having", "union", "partition", "explain", "analyze", "index", "subquery"]
    sql_matches = sum(1 for kw in sql_keywords if kw in text_lower)
    sql_factor = min(1.0, sql_matches / 4.0)
    
    # 3. Structural & Code Density Signal
    code_block_count = text.count("```")
    has_json_or_sql = bool(re.search(r"[{}\[\];]", text))
    structural_factor = min(1.0, (code_block_count * 0.4) + (0.3 if has_json_or_sql else 0.0) + (0.3 if "\n" in text else 0.0))
    
    # 4. Reasoning Depth Signal
    reasoning_triggers = ["optimize", "identify", "explain", "why", "bottleneck", "architecture", "deconstruct", "improvement", "strategy"]
    reasoning_matches = sum(1 for kw in reasoning_triggers if kw in text_lower)
    reasoning_factor = min(1.0, reasoning_matches / 3.0)
    
    # Base task weights
    task_base_weight = {
        "sql_analysis_optimization": 0.45,
        "repo_architecture": 0.40,
        "code_generation": 0.25,
        "general_reasoning": 0.15
    }.get(task_type, 0.20)
    
    raw_score = task_base_weight + (0.15 * length_factor) + (0.25 * sql_factor) + (0.10 * structural_factor) + (0.20 * reasoning_factor)
    
    # Strictly clamp to [0.0, 1.0]
    complexity = round(min(1.0, max(0.0, raw_score)), 3)
    
    factors = {
        "task_base_weight": round(task_base_weight, 3),
        "length_factor": round(length_factor, 3),
        "sql_factor": round(sql_factor, 3),
        "structural_factor": round(structural_factor, 3),
        "reasoning_factor": round(reasoning_factor, 3),
    }
    
    # Determine reasoning level
    if complexity >= 0.70:
        reasoning_level = "high"
        reasoning_idx = 2
    elif complexity >= 0.35:
        reasoning_level = "medium"
        reasoning_idx = 1
    else:
        reasoning_level = "low"
        reasoning_idx = 0
        
    return complexity, factors, reasoning_level, reasoning_idx
