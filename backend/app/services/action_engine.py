"""Action Engine — Generate action plans from extracted court judgment data."""

import logging
from datetime import datetime, timedelta
from app.services.llm_service import call_llm, parse_llm_json
from app.config import settings

logger = logging.getLogger(__name__)

# Standard legal deadlines (days)
STANDARD_DEADLINES = {
    "appeal": 30,
    "special_leave_petition": 90,
    "review_petition": 30,
    "compliance_report": 15,
    "implementation": 180,
}

def generate_action_plan(extracted_data: dict, segments: dict) -> dict:
    """Generate an action plan based on extracted judgment data."""
    if settings.is_ai_available:
        return _generate_with_llm(extracted_data, segments)
    logger.warning("AI services unavailable, returning empty action plan.")
    return {}

def _generate_with_llm(extracted_data: dict, segments: dict) -> dict:
    # Use final judgment for context instead of full text to be more focused
    context_text = segments.get("final_judgment", "")
    if len(context_text) < 50:
         context_text = segments.get("body", "")[-4000:]

    system_prompt = """You are a government compliance advisor AI. Analyze court judgments and generate actionable plans for government officials. Return valid JSON."""

    # Simplify the extracted_data for the prompt
    simplified_data = {
        "case": extracted_data.get("case_title", {}).get("value", "N/A"),
        "directives": [d.get("value", "") for d in extracted_data.get("key_directives", [])],
        "deadlines": [d.get("value", {}) for d in extracted_data.get("deadlines", [])]
    }

    prompt = f"""Based on this court judgment and extracted data, generate an action plan for government officials.

EXTRACTED DATA:
- Case: {simplified_data['case']}
- Directives: {simplified_data['directives']}
- Deadlines: {simplified_data['deadlines']}

JUDGMENT CONTEXT (excerpt):
{context_text}

Generate JSON:
{{
    "action_required": "compliance|appeal|review|implementation",
    "reasoning": "Why this action is needed (2-3 sentences)",
    "deadline": "Specific deadline date or timeframe",
    "responsible_department": "Which government department should act",
    "priority": "high|medium|low",
    "confidence_score": 0.0-1.0,
    "risk_score": 0.0-1.0,
    "source_text": "Key text from judgment supporting this action"
}}"""

    try:
        response = call_llm(prompt, system_prompt, temperature=0.2)
        result = parse_llm_json(response)
        
        if isinstance(result, list) and len(result) > 0:
            result = result[0]
            
        if result and isinstance(result, dict):
            # Calculate auto deadlines
            date_str = extracted_data.get("date_of_order", {}).get("value", "")
            result["auto_deadlines"] = _calculate_auto_deadlines(date_str)
            return result
        else:
            raise ValueError(f"LLM returned unexpected format: {type(result)}")
    except Exception as e:
        logger.error(f"Action plan generation failed: {e}")
        raise ValueError(f"Failed to generate action plan: {e}")

def _calculate_auto_deadlines(date_str: str) -> list:
    """Auto-calculate standard legal deadlines."""
    deadlines = []
    if not date_str:
        return deadlines

    try:
        for fmt in ["%d %B %Y", "%d/%m/%Y", "%d-%m-%Y", "%B %d, %Y", "%Y-%m-%d"]:
            try:
                order_date = datetime.strptime(date_str, fmt)
                break
            except ValueError:
                continue
        else:
            order_date = datetime.now()

        for deadline_type, days in STANDARD_DEADLINES.items():
            calc_date = order_date + timedelta(days=days)
            deadlines.append({
                "type": deadline_type,
                "days": days,
                "calculated_date": calc_date.strftime("%Y-%m-%d"),
                "source": f"Standard {days}-day period for {deadline_type}",
            })
    except Exception as e:
        logger.warning(f"Auto-deadline calculation failed: {e}")

    return deadlines
