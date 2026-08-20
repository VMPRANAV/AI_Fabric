"""Observability API endpoints.
Provides read‑only access to execution traces and a summary.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.observability import ExecutionTrace
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class StageSchema(BaseModel):
    stage: str
    status: str
    details: dict
    timestamp: str

class ExecutionTraceSchema(BaseModel):
    request_id: str
    strategy: Optional[str]
    task_type: Optional[str]
    selected_model: Optional[str]
    prompt_version: Optional[str]
    start_timestamp: str
    end_timestamp: Optional[str]
    total_latency_ms: Optional[float]
    input_tokens: Optional[float]
    output_tokens: Optional[float]
    total_tokens: Optional[float]
    cost_usd: Optional[float]
    tool_success: Optional[bool]
    model_success: Optional[bool]
    quality_score: Optional[float]
    reward: Optional[float]
    state_vector: Optional[dict]
    error: Optional[str]
    stages: List[StageSchema]

    class Config:
        from_attributes = True

@router.get("/observability/traces", response_model=List[ExecutionTraceSchema], summary="List execution traces")
async def list_traces(limit: int = 20, offset: int = 0, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        ExecutionTrace.__table__.select().limit(limit).offset(offset)
    )
    rows = result.fetchall()
    return [ExecutionTraceSchema.from_orm(row) for row in rows]

@router.get("/observability/trace/{request_id}", response_model=ExecutionTraceSchema, summary="Get single trace")
async def get_trace(request_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        ExecutionTrace.__table__.select().where(ExecutionTrace.request_id == request_id)
    )
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Trace not found")
    return ExecutionTraceSchema.from_orm(row)
