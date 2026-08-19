import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from app.schemas.prompt import (
    PromptValidateRequest,
    PromptValidationResponse,
    PromptProcessRequest,
    PromptProcessResponse,
    TemplateMetadata,
    TemplateDetailResponse
)
from app.services.prompt_gateway.validator import validate_and_check_safety, normalize_prompt_text
from app.services.prompt_gateway.renderer import SafeTemplateRenderer
from app.core.logging import logger

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

class PromptGatewayService:
    """
    Central service for the Prompt Gateway (Layer 1).
    Encapsulates validation, normalization, guardrail safety, template versioning,
    and safe variable injection.
    """

    def __init__(self, templates_dir: Path = TEMPLATES_DIR):
        self.templates_dir = templates_dir

    def list_templates(self) -> List[TemplateMetadata]:
        """Discovers all available template categories and their versions from disk."""
        categories: List[TemplateMetadata] = []
        if not self.templates_dir.exists():
            return categories

        for cat_dir in sorted(self.templates_dir.iterdir()):
            if cat_dir.is_dir() and not cat_dir.name.startswith("."):
                versions: List[str] = []
                placeholders_by_version: Dict[str, List[str]] = {}
                for t_file in sorted(cat_dir.glob("*.txt")):
                    ver_name = t_file.stem
                    versions.append(ver_name)
                    content = t_file.read_text(encoding="utf-8")
                    placeholders_by_version[ver_name] = SafeTemplateRenderer.extract_placeholders(content)

                if versions:
                    categories.append(TemplateMetadata(
                        category=cat_dir.name,
                        available_versions=versions,
                        placeholders_by_version=placeholders_by_version
                    ))
        return categories

    def get_template(self, category: str, version: str = "v1") -> Tuple[str, List[str]]:
        """
        Loads raw template content and placeholder list from disk.
        Falls back to general_assistant/v1.txt if requested category is not found.
        """
        target_path = self.templates_dir / category / f"{version}.txt"
        if not target_path.exists():
            # Fallback
            logger.warning(f"Template {category}/{version}.txt not found. Falling back to general_assistant/v1.txt")
            target_path = self.templates_dir / "general_assistant" / "v1.txt"

        if not target_path.exists():
            raise FileNotFoundError(f"Template file not found at {target_path}")

        content = target_path.read_text(encoding="utf-8")
        placeholders = SafeTemplateRenderer.extract_placeholders(content)
        return content, placeholders

    def validate(self, text: str, min_length: int = 3, max_length: int = 10000) -> PromptValidationResponse:
        """Runs normalization and first-stage safety guardrail evaluation."""
        return validate_and_check_safety(text, min_length=min_length, max_length=max_length)

    def process(self, req: PromptProcessRequest) -> PromptProcessResponse:
        """
        Full Prompt Gateway execution pipeline:
        1. Validate & Normalize
        2. Evaluate Safety Guardrails
        3. Retrieve Template & Version
        4. Safely Inject Variables
        5. Render final structured prompt payload
        """
        # Step 1 & 2: Validate, Normalize & Check Safety
        safety = self.validate(req.query)

        cat = req.category or "general_assistant"
        ver = req.version or "v1"

        # Step 3: Retrieve Template
        template_text, placeholders = self.get_template(cat, ver)

        # Step 4: Prepare Variable Map (ensure 'query' is injected from normalized input)
        vars_map = dict(req.variables)
        vars_map["query"] = safety.normalized_query
        if "context" not in vars_map:
            vars_map["context"] = "None provided"

        # Step 5: Render
        rendered, used, missing = SafeTemplateRenderer.render(
            template_text=template_text,
            variables=vars_map,
            strict=req.strict_variables,
            default_fallback="[Not Provided]"
        )

        return PromptProcessResponse(
            original_query=req.query,
            normalized_query=safety.normalized_query,
            safety=safety,
            template_category=cat,
            version=ver,
            rendered_prompt=rendered,
            variables_used=used
        )

prompt_gateway_service = PromptGatewayService()
