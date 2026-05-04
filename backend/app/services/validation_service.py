"""Validation Service — Rule-based validation for extracted data."""

import logging
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)

def validate_extraction(extracted_data: Dict) -> List[Dict]:
    """
    Apply rule-based validation to extracted data.
    Returns a list of validation flags: {"rule": str, "message": str, "severity": "error"|"warning"}
    """
    flags = []
    
    # 1. Missing Critical Fields
    critical_fields = ["case_title", "case_number", "date_of_order"]
    for field in critical_fields:
        field_data = extracted_data.get(field, {})
        if not field_data.get("value"):
            flags.append({
                "rule": f"missing_{field}",
                "message": f"Critical field '{field}' is missing.",
                "severity": "error"
            })
            
    # 2. Check for actionable directives without deadlines
    directives = extracted_data.get("key_directives", [])
    deadlines = extracted_data.get("deadlines", [])
    
    if len(directives) > 0 and len(deadlines) == 0:
        flags.append({
            "rule": "directives_no_deadlines",
            "message": "Directives were found, but no deadlines were extracted. Please verify if deadlines were missed.",
            "severity": "warning"
        })

    # 3. Check for low confidence scores overall
    for key, data in extracted_data.items():
        if isinstance(data, dict) and "confidence" in data:
            if data["confidence"] < 0.6 and data.get("value"):
                flags.append({
                    "rule": f"low_confidence_{key}",
                    "message": f"Low confidence ({data['confidence']}) for '{key}'. Needs manual review.",
                    "severity": "warning"
                })
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, dict) and "confidence" in item:
                    if item["confidence"] < 0.6:
                        flags.append({
                            "rule": f"low_confidence_{key}_{i}",
                            "message": f"Low confidence ({item['confidence']}) for an item in '{key}'.",
                            "severity": "warning"
                        })
                        
    # 4. Check missing responsible authority when there are directives
    auth = extracted_data.get("responsible_authority", {})
    if len(directives) > 0 and not auth.get("value"):
         flags.append({
            "rule": "missing_authority",
            "message": "Directives found but no responsible authority identified.",
            "severity": "warning"
        })

    return flags
