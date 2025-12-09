"""
Benefits Block - Pure function for processing product benefits.

This logic block normalizes and structures benefit data from the product model.
No side effects, no external dependencies, deterministic output.
"""


def process_benefits(product_model: dict) -> dict:
    """
    Process and structure product benefits.
    
    Args:
        product_model: Dictionary containing product data with 'benefits' key.
        
    Returns:
        Structured dictionary with benefit information.
        
    Example:
        Input: {"benefits": ["Brightening", "Fades dark spots"]}
        Output: {
            "benefitList": ["Brightening", "Fades dark spots"],
            "benefitCount": 2,
            "primaryBenefit": "Brightening"
        }
    """
    benefits = product_model.get("benefits", [])
    
    if not benefits:
        return {
            "benefitList": [],
            "benefitCount": 0,
            "primaryBenefit": None
        }
    
    return {
        "benefitList": list(benefits),
        "benefitCount": len(benefits),
        "primaryBenefit": benefits[0] if benefits else None
    }
