"""Segmentation Service — Splits court judgment texts into functional segments."""

import logging
import re
from typing import List, Dict

logger = logging.getLogger(__name__)

def segment_document(full_text: str, pages: List[Dict]) -> Dict[str, str]:
    """
    Split the document into Header, Body, and Final Judgment.
    Returns a dictionary mapping segment types to text.
    """
    segments = {
        "header": "",
        "body": "",
        "final_judgment": ""
    }

    # Extremely simple heuristic-based segmentation
    # Header: First 15% of the text or until first "ORDER" or "JUDGMENT"
    # Final Judgment: Look for keywords in the last 30% of the text
    
    text_length = len(full_text)
    if text_length < 1000:
        # Too short to segment effectively, put everything in body
        segments["body"] = full_text
        return segments

    # 1. Extract Header
    header_end_idx = int(text_length * 0.15)
    
    # Try to find a clear start of the body
    body_start_match = re.search(r'\b(ORDER|JUDGMENT|O R D E R)\b', full_text[:int(text_length * 0.3)], re.IGNORECASE)
    if body_start_match:
        header_end_idx = body_start_match.start()
    
    segments["header"] = full_text[:header_end_idx].strip()
    
    # 2. Extract Final Judgment
    # Look at the last 30% or last 2-3 pages
    search_start_idx = int(text_length * 0.7)
    tail_text = full_text[search_start_idx:]
    
    final_judgment_start_idx = search_start_idx
    
    # Keywords indicating the concluding directives
    conclusion_keywords = [
        r'\b(In view of the above)\b',
        r'\b(Therefore|Accordingly)\b',
        r'\b(It is (?:hereby )?ordered)\b',
        r'\b(The petition is (?:allowed|dismissed|disposed of))\b',
        r'\b(We direct)\b'
    ]
    
    for kw in conclusion_keywords:
        match = re.search(kw, tail_text, re.IGNORECASE)
        if match:
            # We found a potential start of the final judgment
            final_judgment_start_idx = search_start_idx + match.start()
            break
            
    segments["final_judgment"] = full_text[final_judgment_start_idx:].strip()
    
    # 3. Extract Body
    segments["body"] = full_text[header_end_idx:final_judgment_start_idx].strip()
    
    return segments
