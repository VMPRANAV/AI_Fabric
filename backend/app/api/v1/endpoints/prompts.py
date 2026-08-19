from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.schemas.prompt import (
    PromptValidateRequest,
    PromptValidationResponse,
    PromptProcessRequest,
    PromptProcessResponse,
    TemplateMetadata,
    TemplateDetailResponse
)
from app.services.prompt_gateway.service import prompt_gateway_service

router = APIRouter(prefix="/prompts", tags=["Prompt Gateway"])

@router.post("/validate", response_model=PromptValidationResponse, summary="Validate & Evaluate Prompt Safety")
async def validate_prompt(req: PromptValidateRequest):
    """
    Validates input prompt formatting, character constraints, and evaluates
    first-stage guardrails for prompt injection or policy violations.
    """
    return prompt_gateway_service.validate(
        text=req.query,
        min_length=req.min_length,
        max_length=req.max_length
    )

@router.post("/process", response_model=PromptProcessResponse, summary="Process & Render Prompt Template")
async def process_prompt(req: PromptProcessRequest):
    """
    Full first-layer Prompt Gateway execution:
    Validates input, evaluates safety, fetches the selected template version,
    and safely injects parameters.
    """
    try:
        return prompt_gateway_service.process(req)
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prompt processing error: {str(e)}")

@router.get("/templates", response_model=List[TemplateMetadata], summary="List Available Prompt Templates")
async def list_templates():
    """
    Discovers and lists all available template categories, simple versions (v1, v2, v3),
    and expected placeholders from the file-based repository.
    """
    return prompt_gateway_service.list_templates()

@router.get("/templates/{category}", response_model=TemplateDetailResponse, summary="Get Specific Template Content")
async def get_template_details(
    category: str,
    version: str = Query(default="v1", description="Template version (e.g. 'v1', 'v2', 'v3')")
):
    """
    Retrieves the raw content and required placeholders for a specific template category and version.
    """
    try:
        content, placeholders = prompt_gateway_service.get_template(category, version)
        return TemplateDetailResponse(
            category=category,
            version=version,
            raw_template=content,
            placeholders=placeholders
        )
    except FileNotFoundError as fe:
        raise HTTPException(status_code=404, detail=str(fe))
