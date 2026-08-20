from .rule_based import RuleBasedDecisionEngine, rule_based_decision_engine

# Attempt to import PPO components; if the optional dependency is not installed, fallback gracefully.
try:
    from .ppo import PPODecisionEngine, ppo_decision_engine
except ImportError:  # pragma: no cover
    PPODecisionEngine = None
    ppo_decision_engine = None

__all__ = [
    "RuleBasedDecisionEngine",
    "rule_based_decision_engine",
    "PPODecisionEngine",
    "ppo_decision_engine",
]
