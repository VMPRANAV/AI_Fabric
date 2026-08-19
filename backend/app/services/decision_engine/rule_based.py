from typing import List, Tuple
from app.schemas.analyzer import QueryAnalysisResponse
from app.schemas.decision import RoutingDecision
from app.core.config import settings

class RuleBasedDecisionEngine:
    """
    Decision Engine (Layer 3) — Rule-Based Baseline Policy.
    Consumes Query Analyzer (Layer 2) output and state vector to produce a deterministic,
    explainable RoutingDecision without executing LLM calls or MCP tools.
    """

    @staticmethod
    def resolve_model_for_profile(profile: str) -> str:
        """Resolves configured model identifier from environment settings."""
        if profile == "reasoning":
            return settings.AI_MODEL_REASONING
        elif profile == "fast":
            return settings.AI_MODEL_FAST
        elif profile == "mock":
            return settings.AI_MODEL_MOCK
        else:
            return settings.AI_MODEL_BALANCED

    @classmethod
    def select_prompt_version(cls, complexity: float) -> str:
        """
        Deterministic prompt version selection rules based on query complexity.
        Independent from model profile selection.
        """
        if complexity < 0.50:
            return "v1"
        elif complexity < 0.75:
            return "v2"
        else:
            return "v3"

    @classmethod
    def select_prompt_category(cls, task_type: str) -> str:
        """Maps task classification label to template category."""
        if "sql" in task_type:
            return "sql_analysis"
        elif "repo" in task_type:
            return "repo_analysis"
        else:
            return "general_assistant"

    def route(self, analysis: QueryAnalysisResponse, request_id: str = None) -> RoutingDecision:
        """
        Executes Rule-Based routing logic based on strict priority rules.
        """
        complexity = analysis.complexity
        reasoning_req = analysis.reasoning_required.lower()
        latency_target = analysis.latency_target.lower()
        budget = analysis.budget.lower()

        reasons: List[str] = []

        # Priority 1: High Reasoning / High Complexity
        if complexity >= 0.70 or reasoning_req == "high":
            profile = "reasoning"
            if complexity >= 0.70:
                reasons.append(f"complexity={complexity:.2f} >= 0.70")
            if reasoning_req == "high":
                reasons.append(f"reasoning_required={reasoning_req}")
        # Priority 2: Fast Latency Requirement
        elif latency_target == "fast" and complexity < 0.60:
            profile = "fast"
            reasons.append(f"latency_target=fast AND complexity={complexity:.2f} < 0.60")
        # Priority 3: Low Budget Constraint
        elif budget == "low" and complexity < 0.70:
            profile = "fast"
            reasons.append(f"budget=low AND complexity={complexity:.2f} < 0.70")
        # Priority 4: Balanced Default
        else:
            profile = "balanced"
            reasons.append(f"default balanced routing applied (complexity={complexity:.2f})")

        selected_model = self.resolve_model_for_profile(profile)
        prompt_category = self.select_prompt_category(analysis.task_type)
        prompt_version = self.select_prompt_version(complexity)

        return RoutingDecision(
            request_id=request_id,
            selected_model=selected_model,
            model_profile=profile,
            prompt_category=prompt_category,
            prompt_version=prompt_version,
            tool_required=analysis.tool_required,
            tool_type=analysis.tool_type,
            decision_source="rule_based",
            decision_reason=reasons,
            state_vector=analysis.state_vector
        )

rule_based_decision_engine = RuleBasedDecisionEngine()
