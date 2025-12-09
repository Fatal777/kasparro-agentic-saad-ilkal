"""
Ingredient Block - Pure function for processing ingredient data.

This logic block extracts and structures ingredient information from the product model.
No side effects, no external dependencies, deterministic output.
"""

import re


def process_ingredients(product_model: dict) -> dict:
    """
    Process and structure product ingredient information.
    
    Args:
        product_model: Dictionary containing product data with 'keyIngredients' 
                       and 'concentration' keys.
        
    Returns:
        Structured dictionary with ingredient information.
        
    Example:
        Input: {
            "keyIngredients": ["Vitamin C", "Hyaluronic Acid"],
            "concentration": "10% Vitamin C"
        }
        Output: {
            "ingredientList": ["Vitamin C", "Hyaluronic Acid"],
            "ingredientCount": 2,
            "primaryActive": "Vitamin C",
            "concentration": "10%"
        }
    """
    ingredients = product_model.get("keyIngredients", [])
    concentration_str = product_model.get("concentration", "")
    
    # Extract percentage from concentration string
    concentration_match = re.search(r"(\d+(?:\.\d+)?%)", concentration_str)
    concentration = concentration_match.group(1) if concentration_match else None
    
    # Primary active is the first ingredient or extracted from concentration
    primary_active = None
    if ingredients:
        primary_active = ingredients[0]
    elif concentration_str:
        # Try to extract active name from concentration (e.g., "10% Vitamin C" -> "Vitamin C")
        active_match = re.search(r"\d+(?:\.\d+)?%\s+(.+)", concentration_str)
        primary_active = active_match.group(1) if active_match else None
    
    return {
        "ingredientList": list(ingredients),
        "ingredientCount": len(ingredients),
        "primaryActive": primary_active,
        "concentration": concentration
    }
