"""
Usage Block - Pure function for extracting usage instructions.

This logic block parses and structures usage information from the product model.
No side effects, no external dependencies, deterministic output.
"""

import re


def process_usage(product_model: dict) -> dict:
    """
    Process and structure product usage instructions.
    
    Args:
        product_model: Dictionary containing product data with 'howToUse' key.
        
    Returns:
        Structured dictionary with usage information.
        
    Example:
        Input: {"howToUse": "Apply 2–3 drops in the morning before sunscreen"}
        Output: {
            "usageInstructions": "Apply 2–3 drops in the morning before sunscreen",
            "frequency": "morning",
            "quantity": "2–3 drops",
            "timing": "before sunscreen"
        }
    """
    how_to_use = product_model.get("howToUse", "")
    
    if not how_to_use:
        return {
            "usageInstructions": "",
            "frequency": None,
            "quantity": None,
            "timing": None
        }
    
    # Extract quantity (e.g., "2–3 drops", "3-4 drops")
    quantity_match = re.search(r"(\d+[–-]\d+\s+drops|\d+\s+drops)", how_to_use, re.IGNORECASE)
    quantity = quantity_match.group(1) if quantity_match else None
    
    # Extract frequency (morning, evening, morning and evening)
    frequency = None
    if "morning and evening" in how_to_use.lower():
        frequency = "morning and evening"
    elif "morning" in how_to_use.lower():
        frequency = "morning"
    elif "evening" in how_to_use.lower():
        frequency = "evening"
    elif "night" in how_to_use.lower():
        frequency = "night"
    
    # Extract timing (before/after something)
    timing_match = re.search(r"(before|after)\s+(\w+)", how_to_use, re.IGNORECASE)
    timing = f"{timing_match.group(1)} {timing_match.group(2)}" if timing_match else None
    
    return {
        "usageInstructions": how_to_use,
        "frequency": frequency,
        "quantity": quantity,
        "timing": timing
    }
