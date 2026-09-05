import json
import re
import logging
from typing import Dict, Any, List, Optional
from app.config import settings

logger = logging.getLogger(__name__)

# Configure Gemini if key available
gemini_model = None
if settings.GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel("gemini-1.5-flash")
        logger.info("Gemini AI model configured successfully.")
    except Exception as e:
        logger.warning(f"Failed to initialize Gemini AI: {e}")

# Heuristic patterns
ENTITY_PATTERNS = [
    (r"(highway\s*\d+|nh[-\s]*\d+|vip\s*road|bridge|flyover|railway\s*station|metro\s*line|airport)", "infrastructure"),
    (r"(flood|waterlogging|water\s*level|submerged|overflow|inundat\w+)", "flood"),
    (r"(fire|wildfire|blaze|flames|smoke)", "wildfire"),
    (r"(earthquake|quake|tremor|aftershock|collapse)", "earthquake"),
    (r"(shelter|relief\s*camp|stadium|evacuation\s*center)", "shelter"),
    (r"(rescue|ndrf|sdrf|helicopter|boat|team\s*alpha|crew|dispatched|mobilized)", "rescue"),
    (r"(power|blackout|grid|electricity|transformer|line)", "infrastructure"),
    (r"(hospital|medical|casualt\w+|injur\w+|ambulance)", "rescue"),
]

CHANGE_KEYWORDS = [
    "now", "closed", "blocked", "opened", "restored", "collapsed", "evacuated",
    "dispatched", "rising", "dropped", "danger", "exceeded", "alert", "cut off", "damaged"
]

SEVERITY_KEYWORDS = {
    "critical": ["collapsed", "casualt", "trapped", "danger mark", "evacuate immediately", "destroyed", "severe flood"],
    "high": ["closed", "submerged", "rising rapidly", "helicopter rescue", "outage", "disrupted", "blocked"],
    "medium": ["waterlogging", "delay", "warning", "mobilized", "relief camp"],
    "low": ["operational", "reopened", "monitoring", "cleared", "normal"],
    "info": ["status update", "notice", "scheduled"]
}

def analyze_update_heuristic(raw_text: str, source: str, history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    text_lower = raw_text.lower()
    
    # 1. Detect Entity Type
    detected_type = "other"
    for pattern, etype in ENTITY_PATTERNS:
        if re.search(pattern, text_lower):
            detected_type = etype
            break
            
    # 2. Detect Named Entity
    entity_name = "Crisis Sector"
    # Match specific names like "Highway 12", "VIP Road", "Salt Lake Stadium", "NDRF Team"
    name_match = re.search(r"\b(Highway\s*\d+|NH[-\s]*\d+|VIP Road|[A-Z][a-zA-Z\s]+(?:Road|Bridge|Stadium|Camp|Sector\s*\d+|Airport|Station|Hospital|Team))\b", raw_text)
    if name_match:
        entity_name = name_match.group(1).strip()
    elif detected_type == "flood":
        entity_name = "Flood Zone Area"
    elif detected_type == "infrastructure":
        entity_name = "Key Transport Corridor"
    elif detected_type == "shelter":
        entity_name = "Emergency Relief Shelter"
    elif detected_type == "rescue":
        entity_name = "Rapid Response Unit"

    # 3. Assess Severity
    severity = "medium"
    for sev, keywords in SEVERITY_KEYWORDS.items():
        if any(k in text_lower for k in keywords):
            severity = sev
            break

    # 4. Detect State Change
    change_detected = any(k in text_lower for k in CHANGE_KEYWORDS) or len(raw_text) > 40

    # 5. Detect Conflict with History
    conflict_detected = False
    conflict_details = None
    if history:
        for prev in history[:5]:
            prev_text = prev.get("raw_text", "").lower()
            if entity_name.lower() in prev_text or detected_type in prev_text:
                if ("open" in prev_text and "closed" in text_lower) or ("closed" in prev_text and "open" in text_lower):
                    conflict_detected = True
                    conflict_details = f"Contradiction with previous report: '{prev.get('raw_text', '')[:40]}...'"
                    break

    # 6. Confidence calculation
    base_conf = 0.86
    if source in ["sensor", "agency", "radio"]:
        base_conf += 0.08
    if len(raw_text) > 30:
        base_conf += 0.04
    confidence = min(0.99, max(0.65, round(base_conf, 2)))

    return {
        "entity_type": detected_type,
        "entity_name": entity_name,
        "severity": severity,
        "confidence": confidence,
        "change_detected": change_detected,
        "conflict": {
            "detected": conflict_detected,
            "details": conflict_details
        },
        "action_recommended": f"Deploy resources and monitor status of {entity_name}."
    }

async def process_crisis_text(raw_text: str, source: str, history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Process crisis text using Gemini AI if configured, otherwise fallback to smart heuristic engine.
    """
    if gemini_model:
        prompt = f"""
You are the AI Analysis Engine for CrisisLens Emergency Command Center.
Analyze the following crisis report update and return a strictly valid JSON response:
Report text: "{raw_text}"
Source: "{source}"

Return strictly a JSON object with this exact structure:
{{
  "entity_type": "flood" | "wildfire" | "earthquake" | "infrastructure" | "shelter" | "rescue" | "other",
  "entity_name": "<specific location/entity name or null>",
  "severity": "critical" | "high" | "medium" | "low" | "info",
  "confidence": <float between 0.70 and 0.99>,
  "change_detected": <true or false>,
  "conflict_detected": <true or false>,
  "conflict_details": "<details or null>",
  "action_recommended": "<concise actionable advice>"
}}
"""
        try:
            response = gemini_model.generate_content(prompt)
            clean_json = response.text.strip()
            if clean_json.startswith("```json"):
                clean_json = clean_json[7:]
            if clean_json.endswith("```"):
                clean_json = clean_json[:-3]
            parsed = json.loads(clean_json.strip())
            return {
                "entity_type": parsed.get("entity_type", "other"),
                "entity_name": parsed.get("entity_name") or "Key Entity",
                "severity": parsed.get("severity", "medium"),
                "confidence": float(parsed.get("confidence", 0.94)),
                "change_detected": bool(parsed.get("change_detected", True)),
                "conflict": {
                    "detected": bool(parsed.get("conflict_detected", False)),
                    "details": parsed.get("conflict_details")
                },
                "action_recommended": parsed.get("action_recommended", "Continue active monitoring.")
            }
        except Exception as e:
            logger.warning(f"Gemini API processing failed, falling back to heuristic: {e}")

    # Heuristic processing fallback
    return analyze_update_heuristic(raw_text, source, history)
