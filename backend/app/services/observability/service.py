"""Observability service for Milestone 7.
Provides a thin instrumentation layer that records per‑request traces.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.observability import ExecutionTrace
from .sanitizer import sanitize_stage_data

class ObservabilityService:
    """Collects stage telemetry and persists ExecutionTrace records.

    This service is deliberately side‑effect free for the core pipeline –
    it only records data.
    """

    def __init__(self) -> None:
        # In‑memory store keyed by request_id
        self._active: Dict[str, Dict[str, Any]] = {}

    async def start_trace(
        self,
        request_id: str,
        strategy: Optional[str] = None,
        task_type: Optional[str] = None,
        prompt_version: Optional[str] = None,
    ) -> None:
        """Initialize a new trace entry.

        Called immediately after a request_id is generated.
        """
        self._active[request_id] = {
            "request_id": request_id,
            "strategy": strategy,
            "task_type": task_type,
            "prompt_version": prompt_version,
            "start_timestamp": datetime.utcnow(),
            "stages": [],
        }

    async def record_stage(
        self,
        request_id: str,
        stage: str,
        payload: Dict[str, Any],
        status: str = "completed",
    ) -> None:
        """Append a stage record.

        ``payload`` is sanitized before storage.
        """
        trace = self._active.get(request_id)
        if not trace:
            # If start_trace was not called (should not happen), initialise lazily.
            await self.start_trace(request_id)
            trace = self._active[request_id]
        sanitized = sanitize_stage_data(payload)
        trace["stages"].append(
            {
                "stage": stage,
                "status": status,
                "details": sanitized,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
        )

    async def record_error(self, request_id: str, exc: Exception) -> None:
        trace = self._active.get(request_id)
        if trace:
            trace["error"] = str(exc)

    async def finalize_trace(
        self,
        request_id: str,
        status: str = "completed",
        db: AsyncSession | None = None,
    ) -> None:
        """Compute aggregates and persist the ExecutionTrace.
        ``db`` can be injected (the current request's session) – if omitted we create a new one.
        """
        trace = self._active.pop(request_id, None)
        if not trace:
            return
        end_ts = datetime.utcnow()
        # Compute totals from stages when available
        total_latency_ms: Optional[float] = None
        input_tokens = output_tokens = total_tokens = None
        cost_usd = None
        tool_success = model_success = None
        reward = quality_score = None
        state_vector = None
        # Simple aggregation: use last stage (Model Gateway) for token/cost info if present
        for st in trace["stages"]:
            if st["stage"] == "Model Gateway" and st["status"] == "completed":
                details = st["details"]
                input_tokens = details.get("input_tokens") or details.get("tokens")
                output_tokens = details.get("output_tokens")
                total_tokens = details.get("total_tokens") or details.get("tokens")
                cost_usd = details.get("cost_usd")
                model_success = details.get("success")
                # latency captured elsewhere; use the stage timestamp diff later
            if st["stage"] == "Observability & Feedback" and st["status"] == "completed":
                details = st["details"]
                reward = details.get("reward")
                quality_score = details.get("quality_score")
        # compute total latency as difference between first and last stage timestamps
        if trace["stages"]:
            first = datetime.fromisoformat(trace["stages"][0]["timestamp"].replace("Z", "+00:00"))
            last = datetime.fromisoformat(trace["stages"][-1]["timestamp"].replace("Z", "+00:00"))
            total_latency_ms = (last - first).total_seconds() * 1000
        # Populate the ORM model
        orm = ExecutionTrace(
            request_id=trace["request_id"],
            strategy=trace.get("strategy"),
            task_type=trace.get("task_type"),
            selected_model=trace.get("selected_model"),
            prompt_version=trace.get("prompt_version"),
            start_timestamp=trace.get("start_timestamp"),
            end_timestamp=end_ts,
            total_latency_ms=total_latency_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            cost_usd=cost_usd,
            tool_success=tool_success,
            model_success=model_success,
            quality_score=quality_score,
            reward=reward,
            state_vector=state_vector,
            error=trace.get("error"),
            stages=trace["stages"],
        )
        # Persist
        if db is None:
            # create a temporary session
            async with get_db() as session:
                session.add(orm)
                await session.commit()
        else:
            db.add(orm)
            await db.commit()

# Export a singleton for easy import
observability_service = ObservabilityService()
