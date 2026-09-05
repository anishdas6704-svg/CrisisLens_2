"""
CrisisLens - Google Gemini AI Service
Handles:
1. Entity extraction from free-text crisis updates
2. Change detection (compare old vs new state)
3. Conflict detection (contradicting information)
"""
import json
import time
from typing import Optional
# pyrefly: ignore [missing-import]
import google.generativeai as genai
# pyrefly: ignore [missing-import]
from loguru import logger

from app.core.config import settings


# ─── Gemini client setup ────────────────────────────────────────────────────
_model = None


def _get_model():
    """Lazy-initialize the Gemini model; raises clearly if API key is missing."""
    global _model
    if _model is None:
        if not settings.GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured. Set it in your .env file."
            )
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _model = genai.GenerativeModel("gemini-1.5-pro-latest")
    return _model


# ─── Prompts ─────────────────────────────────────────────────────────────────

EXTRACTION_PROMPT = """You are an AI assistant for a crisis management system called CrisisLens.

Your job: Extract structured information from a raw crisis update text.

Return ONLY a valid JSON object with these exact fields:
{{
  "entity_name": "string — the main entity mentioned (road, shelter, resource, etc.)",
  "entity_type": "one of: road, shelter, resource, evacuation_zone, personnel, hospital, utility, other",
  "new_status": "one of: open, closed, available, unavailable, operational, damaged, unknown",
  "location": "string or null — location if mentioned",
  "reason": "string or null — reason for status change if mentioned",
  "capacity": "integer or null — capacity number if mentioned",
  "occupancy": "integer or null — current occupancy if mentioned",
  "additional_info": "string or null — any other relevant extracted info",
  "confidence": "float 0.0-1.0 — your confidence in this extraction"
}}

Crisis context: {crisis_name} ({crisis_type})

Raw update text:
\"\"\"{raw_text}\"\"\"

Respond with ONLY the JSON object. No markdown. No explanation."""

CHANGE_DETECTION_PROMPT = """You are an AI assistant for a crisis management system called CrisisLens.

Compare the PREVIOUS state and NEW state of an entity and determine if a meaningful change occurred.

Entity: {entity_name}
Previous state: {previous_state}
New state: {new_state}

Return ONLY a valid JSON object:
{{
  "change_detected": true or false,
  "change_summary": "string — brief description of what changed, or null if no change",
  "is_significant": true or false,
  "change_type": "one of: status_change, location_change, capacity_change, no_change"
}}

Respond with ONLY the JSON object. No markdown. No explanation."""

CONFLICT_DETECTION_PROMPT = """You are an AI assistant for a crisis management system called CrisisLens.

Determine if the NEW information conflicts with the EXISTING state.

Entity: {entity_name}
Existing state: {existing_state}
New report: {new_report}

Return ONLY a valid JSON object:
{{
  "conflict_detected": true or false,
  "conflict_detail": "string — describe the conflict if detected, or null",
  "recommended_action": "one of: accept_new, keep_existing, flag_for_review"
}}

Respond with ONLY the JSON object. No markdown. No explanation."""


# ─── Helper ──────────────────────────────────────────────────────────────────

def _parse_json_response(text: str) -> dict:
    """Strip markdown code fences if present, then parse JSON."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1])
    return json.loads(text)


async def _call_gemini(prompt: str) -> tuple[str, int]:
    """Call Gemini and return (response_text, elapsed_ms)."""
    start = time.monotonic()
    response = await _get_model().generate_content_async(prompt)
    elapsed_ms = int((time.monotonic() - start) * 1000)
    return response.text, elapsed_ms


# ─── Public API ──────────────────────────────────────────────────────────────

async def extract_entity_info(
    raw_text: str,
    crisis_name: str,
    crisis_type: str,
) -> dict:
    """
    Extract structured entity information from a raw crisis update.

    Returns:
        dict with keys: entity_name, entity_type, new_status, location,
                        reason, capacity, occupancy, additional_info,
                        confidence, gemini_model, processing_time_ms
    """
    prompt = EXTRACTION_PROMPT.format(
        crisis_name=crisis_name,
        crisis_type=crisis_type,
        raw_text=raw_text,
    )
    try:
        text, elapsed_ms = await _call_gemini(prompt)
        result = _parse_json_response(text)
        result["gemini_model"] = "gemini-1.5-pro-latest"
        result["processing_time_ms"] = elapsed_ms
        logger.info(f"Gemini extraction: {result['entity_name']} | {elapsed_ms}ms")
        return result
    except Exception as e:
        logger.error(f"Gemini extraction failed: {e}")
        return {
            "entity_name": None,
            "entity_type": "other",
            "new_status": "unknown",
            "location": None,
            "reason": None,
            "capacity": None,
            "occupancy": None,
            "additional_info": str(e),
            "confidence": 0.0,
            "gemini_model": "gemini-1.5-pro-latest",
            "processing_time_ms": 0,
        }


async def detect_change(
    entity_name: str,
    previous_state: Optional[str],
    new_state: str,
) -> dict:
    """
    Compare previous and new entity states. Returns change analysis dict.
    """
    if not previous_state:
        return {
            "change_detected": True,
            "change_summary": "First recorded state for this entity.",
            "is_significant": True,
            "change_type": "status_change",
        }

    prompt = CHANGE_DETECTION_PROMPT.format(
        entity_name=entity_name,
        previous_state=previous_state,
        new_state=new_state,
    )
    try:
        text, _ = await _call_gemini(prompt)
        result = _parse_json_response(text)
        logger.info(f"Change detection for '{entity_name}': {result['change_detected']}")
        return result
    except Exception as e:
        logger.error(f"Change detection failed: {e}")
        return {
            "change_detected": True,
            "change_summary": f"Could not analyze change: {e}",
            "is_significant": False,
            "change_type": "status_change",
        }


async def detect_conflict(
    entity_name: str,
    existing_state: str,
    new_report: str,
) -> dict:
    """
    Detect if new information contradicts existing entity state.
    Returns conflict analysis dict.
    """
    prompt = CONFLICT_DETECTION_PROMPT.format(
        entity_name=entity_name,
        existing_state=existing_state,
        new_report=new_report,
    )
    try:
        text, _ = await _call_gemini(prompt)
        result = _parse_json_response(text)
        if result.get("conflict_detected"):
            logger.warning(f"Conflict detected for '{entity_name}': {result.get('conflict_detail')}")
        return result
    except Exception as e:
        logger.error(f"Conflict detection failed: {e}")
        return {
            "conflict_detected": False,
            "conflict_detail": None,
            "recommended_action": "flag_for_review",
        }
