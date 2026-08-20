class SyntheticMetricProvider:
    """Deterministic synthetic metric generator for PPO training.
    Returns values in a fixed range to keep experiments reproducible.
    """

    @staticmethod
    def evaluate(state_vector):
        # Simple deterministic formulas based on the state vector values
        # state_vector is a numpy array of six floats in [0,1]
        quality = float(state_vector.mean())  # average as quality (0-1)
        latency_ms = 200.0 * (1.0 - state_vector[3])  # higher latency when 4th dim low
        cost = 0.5 * (1.0 - state_vector[4])  # cost inversely related to 5th dim
        tool_success = state_vector[5] > 0.5  # boolean success flag
        return quality, latency_ms, cost, tool_success
