"""NLP Service — Extract structured information from court judgments using a hybrid pipeline."""

import re
import json
import logging
from app.services.llm_service import call_llm, parse_llm_json, chunk_text
from app.config import settings

logger = logging.getLogger(__name__)

DATE_PATTERNS = [
    r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b',
    r'\b(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})\b',
    r'\b(\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4})\b',
]

CASE_NUMBER_PATTERNS = [
    r'(?:W\.?P\.?\s*(?:\(C\))?\s*No\.?\s*\d+[/-]?\d*(?:\s*of\s*\d{4})?)',
    r'(?:Civil\s+Appeal\s+No\.?\s*\d+[/-]?\d*(?:\s*of\s*\d{4})?)',
    r'(?:(?:Case|Petition|Application)\s+No\.?\s*\d+[/-]?\d*(?:\s*of\s*\d{4})?)',
]

def extract_information(full_text: str, pages: list[dict], segments: dict) -> dict:
    """Hybrid pipeline for structured data extraction."""
    
    # Initialize structured result
    result = {
        "case_title": {"value": None, "source_text": "", "page_number": 0, "confidence": 0.0},
        "case_number": {"value": None, "source_text": "", "page_number": 0, "confidence": 0.0},
        "parties_involved": [],
        "date_of_order": {"value": None, "source_text": "", "page_number": 0, "confidence": 0.0},
        "judge_name": {"value": None, "source_text": "", "page_number": 0, "confidence": 0.0},
        "court_name": {"value": None, "source_text": "", "page_number": 0, "confidence": 0.0},
        "key_directives": [],
        "deadlines": [],
        "responsible_authority": {"value": None, "source_text": "", "page_number": 0, "confidence": 0.0},
    }

    # 1. Rule-based extraction
    _extract_with_regex(result, segments, pages)

    if not settings.is_ai_available:
        logger.warning("AI not available, returning only regex results.")
        return result

    # 2. Multi-Pass LLM Extraction
    # Pass A: Case Metadata from Header
    header_data = _llm_pass_metadata(segments.get("header", full_text[:4000]))
    _merge_llm_result(result, header_data, pages, default_confidence=0.85)

    # Pass B: Directives and Deadlines from Final Judgment
    fj_text = segments.get("final_judgment", "")
    if len(fj_text) < 50:
        fj_text = full_text[-4000:]
        
    directives_data = _llm_pass_directives(fj_text)
    _merge_llm_result(result, directives_data, pages, default_confidence=0.8)

    # 3. Final Confidence Scoring & Consolidation
    _calculate_final_confidence(result)

    return result

def _extract_with_regex(result: dict, segments: dict, pages: list[dict]):
    """Extract deterministic fields using regex on the header segment."""
    header_text = segments.get("header", "")
    
    # Extract Case Number
    for pattern in CASE_NUMBER_PATTERNS:
        match = re.search(pattern, header_text, re.IGNORECASE)
        if match:
            source = header_text[max(0, match.start()-40):match.end()+40].strip()
            result["case_number"] = {
                "value": match.group(0),
                "source_text": source,
                "page_number": _find_page(source, pages),
                "confidence": 0.95
            }
            break

    # Extract Date of Order (can be in header or final judgment)
    search_text = segments.get("final_judgment", "") + "\n" + header_text
    dates_found = []
    for pattern in DATE_PATTERNS:
        for match in re.finditer(pattern, search_text, re.IGNORECASE):
            source = search_text[max(0, match.start()-40):match.end()+40].strip()
            dates_found.append({
                "value": match.group(0),
                "source_text": source,
                "page_number": _find_page(source, pages)
            })

    if dates_found:
        # Usually the last date mentioned is the order date
        date_obj = dates_found[-1]
        date_obj["confidence"] = 0.8
        result["date_of_order"] = date_obj

def _llm_pass_metadata(text: str) -> dict:
    system_prompt = "You are a legal document analyzer. Extract case metadata. Return valid JSON."
    prompt = f"""Extract from this court judgment header:
1. case_title (e.g. 'A vs B')
2. case_number (only if not obvious)
3. parties_involved (list of dicts with 'name' and 'role' (e.g. Petitioner/Respondent))
4. date_of_order
5. judge_name
6. court_name

For EVERY field, provide the exact 'value' and the 'source_text' from the document that proves it.
Return JSON:
{{
  "case_title": {{"value": "...", "source_text": "..."}},
  "case_number": {{"value": "...", "source_text": "..."}},
  "parties_involved": [{{"value": {{"name": "...", "role": "..."}}, "source_text": "..."}}],
  "date_of_order": {{"value": "...", "source_text": "..."}},
  "judge_name": {{"value": "...", "source_text": "..."}},
  "court_name": {{"value": "...", "source_text": "..."}}
}}

TEXT:
{text}"""
    return parse_llm_json(call_llm(prompt, system_prompt, temperature=0.1))

def _llm_pass_directives(text: str) -> dict:
    system_prompt = "You are a legal document analyzer. Extract directives and deadlines. Return valid JSON."
    prompt = f"""Extract from this final judgment section:
1. key_directives (list of string values representing what the court ordered)
2. deadlines (list of dict values with 'description' and 'date')
3. responsible_authority (the government body or person responsible for executing the directives)

For EVERY field, provide the exact 'value' and the 'source_text' from the document that proves it. The source text MUST be an exact quote.
Return JSON:
{{
  "key_directives": [{{"value": "...", "source_text": "..."}}],
  "deadlines": [{{"value": {{"description": "...", "date": "..."}}, "source_text": "..."}}],
  "responsible_authority": {{"value": "...", "source_text": "..."}}
}}

TEXT:
{text}"""
    return parse_llm_json(call_llm(prompt, system_prompt, temperature=0.1))

def _merge_llm_result(result: dict, llm_data: dict, pages: list[dict], default_confidence: float):
    """Merge LLM structured output into the main result dict."""
    if not llm_data:
        return
        
    for key, data in llm_data.items():
        if key not in result:
            continue
            
        if isinstance(result[key], dict): # Single field
            # Only override if current value is empty or current confidence is lower
            if isinstance(data, dict) and data.get("value"):
                current_conf = result[key].get("confidence", 0)
                # LLM confidence is default_confidence, but boosted if source_text is provided
                llm_conf = default_confidence + (0.1 if data.get("source_text") else -0.2)
                
                if not result[key].get("value") or llm_conf > current_conf:
                    result[key] = {
                        "value": data["value"],
                        "source_text": data.get("source_text", ""),
                        "page_number": _find_page(data.get("source_text", ""), pages),
                        "confidence": min(0.99, llm_conf)
                    }
        elif isinstance(result[key], list): # List field
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and item.get("value"):
                        llm_conf = default_confidence + (0.1 if item.get("source_text") else -0.2)
                        result[key].append({
                            "value": item["value"],
                            "source_text": item.get("source_text", ""),
                            "page_number": _find_page(item.get("source_text", ""), pages),
                            "confidence": min(0.99, llm_conf)
                        })

def _calculate_final_confidence(result: dict):
    """Adjust confidence scores based on cross-validation."""
    # E.g. if case_title and parties_involved match up, boost confidence
    pass

def _find_page(text: str, pages: list[dict]) -> int:
    if not text:
        return 1
    # Simple substring search. Might fail if text spans pages or has OCR noise.
    for p in pages:
        if text.lower() in p.get("text", "").lower():
            return p.get("page_num", 1)
    return 1
