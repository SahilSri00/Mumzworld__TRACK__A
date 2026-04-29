"""
Utility helpers: language detection, JSON extraction from LLM output.
"""

import json
import re
from langdetect import detect, LangDetectException


def detect_language(text: str) -> str:
    """
    Detect whether the input is English or Arabic.
    Returns 'en' or 'ar'. Defaults to 'en' on failure.
    """
    try:
        lang = detect(text)
        # langdetect returns ISO 639-1 codes; map Arabic variants to 'ar'
        if lang.startswith("ar"):
            return "ar"
        return "en"
    except LangDetectException:
        return "en"


def extract_json_from_response(raw: str) -> dict:
    """
    Extract a JSON object from the LLM's response.

    Handles common issues:
    - Markdown code fences (```json ... ```)
    - Leading/trailing whitespace or text
    - BOM characters
    """
    # Strip BOM and whitespace
    cleaned = raw.strip().lstrip("\ufeff")

    # Remove markdown code fences if present
    # Matches ```json ... ``` or ``` ... ```
    fence_pattern = r"```(?:json)?\s*\n?(.*?)\n?\s*```"
    fence_match = re.search(fence_pattern, cleaned, re.DOTALL)
    if fence_match:
        cleaned = fence_match.group(1).strip()

    # Try direct parse first
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Try to find the first { ... } block (greedy from first { to last })
    brace_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if brace_match:
        try:
            return json.loads(brace_match.group(0))
        except json.JSONDecodeError:
            pass

    # Nothing worked — raise with context
    raise ValueError(
        f"Could not extract valid JSON from LLM response. "
        f"First 200 chars: {raw[:200]}"
    )


def truncate_message(message: str, max_chars: int = 2000) -> str:
    """
    Truncate very long messages to stay within token budgets.
    Preserves the beginning and end, which usually contain the most info.
    """
    if len(message) <= max_chars:
        return message

    half = max_chars // 2
    return (
        message[:half]
        + "\n\n[... message truncated for processing ...]\n\n"
        + message[-half:]
    )
