import re
from typing import Dict, List, Tuple

PLACEHOLDER_REGEX = re.compile(r"\{([a-zA-Z0-9_]+)\}")

class SafeTemplateRenderer:
    """
    Safely substitutes named variables into prompt templates without using eval()
    or arbitrary code execution.
    """

    @staticmethod
    def extract_placeholders(template_text: str) -> List[str]:
        """Extracts unique placeholder variable names defined as {var_name}."""
        return list(dict.fromkeys(PLACEHOLDER_REGEX.findall(template_text)))

    @classmethod
    def render(
        cls,
        template_text: str,
        variables: Dict[str, str],
        strict: bool = False,
        default_fallback: str = "[None]"
    ) -> Tuple[str, Dict[str, str], List[str]]:
        """
        Renders template by replacing {var} with variable values.

        Returns:
            rendered_text: The populated template string
            variables_used: Dict of variable keys that were replaced
            missing_variables: List of required placeholders that had no provided value
        """
        required_placeholders = cls.extract_placeholders(template_text)
        missing: List[str] = []
        used: Dict[str, str] = {}

        for ph in required_placeholders:
            if ph in variables and variables[ph] is not None:
                used[ph] = str(variables[ph])
            else:
                missing.append(ph)

        if strict and missing:
            raise ValueError(f"Missing required template variables: {', '.join(missing)}")

        def replace_match(match: re.Match) -> str:
            key = match.group(1)
            if key in used:
                return used[key]
            return default_fallback

        rendered = PLACEHOLDER_REGEX.sub(replace_match, template_text)
        return rendered, used, missing
