"""
Core parsing logic: takes a mom's message, calls Grok API via OpenAI SDK,
validates the response against our Pydantic schema, and returns structured output.
"""

import asyncio
import logging
from openai import AsyncOpenAI

from src.config import (
    GROK_API_KEY,
    GROQ_BASE_URL,
    PRIMARY_MODEL,
    FALLBACK_MODEL,
    TEMPERATURE,
    MAX_TOKENS,
    CONFIDENCE_THRESHOLD,
)
from src.models import ParseResponse
from src.prompts import SYSTEM_PROMPT, FEW_SHOT_EXAMPLES
from src.utils import detect_language, extract_json_from_response, truncate_message

logger = logging.getLogger(__name__)

# Initialize the OpenAI client pointing to Groq
if GROK_API_KEY:
    client = AsyncOpenAI(api_key=GROK_API_KEY, base_url=GROQ_BASE_URL)
else:
    client = None

def _build_messages(user_message: str) -> list[dict]:
    """
    Build the OpenAI/xAI-style messages array from our few-shot examples + user message.
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for ex in FEW_SHOT_EXAMPLES:
        messages.append({"role": ex["role"], "content": ex["content"]})
        
    messages.append({"role": "user", "content": user_message})
    return messages


async def call_grok(user_message: str, model_name: str) -> str:
    """
    Call the Grok API with system instruction + few-shot examples + user message.
    Returns the raw text content from the response.
    """
    messages = _build_messages(user_message)
    
    response = await client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        response_format={"type": "json_object"}
    )

    return response.choices[0].message.content


async def parse_mom_message(message: str, language_hint: str | None = None) -> ParseResponse:
    """
    Parse a mom's informal message into structured shopping data.

    Steps:
    1. Truncate if too long
    2. Detect language (or use hint)
    3. Call primary model (fallback on failure)
    4. Extract JSON from response
    5. Validate against Pydantic schema
    6. Apply confidence thresholds
    7. Return structured ParseResponse
    """
    # Step 1: Truncate extremely long messages
    processed_message = truncate_message(message)

    # Step 2: Detect language for logging
    detected_lang = language_hint or detect_language(processed_message)
    logger.info(f"Detected language: {detected_lang}")

    # Step 3: Call LLM with fallback
    raw_response = None
    used_model = PRIMARY_MODEL

    if not client:
        logger.error("Grok client not initialized. Check GROK_API_KEY.")
        return ParseResponse(
            detected_language=detected_lang,
            original_message=message,
            summary="API key missing. Unable to process message.",
            shopping_items=[],
            calendar_events=[],
            overall_confidence=0.0,
            uncertainty_notes=["Grok API key is missing. Please set GROK_API_KEY."],
            is_out_of_scope=False,
            out_of_scope_reason=None,
        )

    for model_name in [PRIMARY_MODEL, FALLBACK_MODEL]:
        try:
            logger.info(f"Calling model: {model_name}")
            raw_response = await call_grok(processed_message, model_name)
            used_model = model_name
            break
        except Exception as e:
            logger.warning(f"Model {model_name} failed: {e}")
            continue

    if raw_response is None:
        return ParseResponse(
            detected_language=detected_lang,
            original_message=message,
            summary="Unable to process this message at the moment. Please try again.",
            shopping_items=[],
            calendar_events=[],
            overall_confidence=0.0,
            uncertainty_notes=["Both AI models are currently unavailable. Please try again later."],
            is_out_of_scope=False,
            out_of_scope_reason=None,
        )

    logger.info(f"Got response from {used_model} ({len(raw_response)} chars)")

    # Step 4: Extract JSON
    try:
        parsed_json = extract_json_from_response(raw_response)
    except ValueError as e:
        logger.error(f"JSON extraction failed: {e}")
        return ParseResponse(
            detected_language=detected_lang,
            original_message=message,
            summary="The AI response could not be parsed. Please try rephrasing.",
            shopping_items=[],
            calendar_events=[],
            overall_confidence=0.0,
            uncertainty_notes=["Failed to parse AI response into valid JSON"],
            is_out_of_scope=False,
            out_of_scope_reason=None,
        )

    # Step 5: Validate against Pydantic schema
    try:
        result = ParseResponse.model_validate(parsed_json)
    except Exception as e:
        logger.error(f"Schema validation failed: {e}")
        return ParseResponse(
            detected_language=detected_lang,
            original_message=message,
            summary="The AI response did not match the expected format. Please try again.",
            shopping_items=[],
            calendar_events=[],
            overall_confidence=0.0,
            uncertainty_notes=[f"AI response failed schema validation: {str(e)[:200]}"],
            is_out_of_scope=False,
            out_of_scope_reason=None,
        )

    # Step 6: Apply confidence thresholds — flag uncertain items
    for item in result.shopping_items:
        if item.confidence < CONFIDENCE_THRESHOLD and not item.uncertainty_reason:
            item.uncertainty_reason = "Low confidence extraction — details may be inaccurate"

    for event in result.calendar_events:
        if event.confidence < CONFIDENCE_THRESHOLD and not event.uncertainty_reason:
            event.uncertainty_reason = "Low confidence — date or event details may be inaccurate"

    # Ensure original_message is set correctly
    result.original_message = message

    return result
