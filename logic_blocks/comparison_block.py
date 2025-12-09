"""
Comparison Block - Pure function for comparing two products.

This logic block compares ingredients, benefits, and pricing between two products.
No side effects, no external dependencies, deterministic output.
"""


def compare_products(product_a: dict, product_b: dict) -> dict:
    """
    Compare two products and return structured comparison data.
    
    Args:
        product_a: Dictionary containing first product data.
        product_b: Dictionary containing second product data.
        
    Returns:
        Structured dictionary with comparison information.
        
    Example:
        Input: 
            product_a: {"keyIngredients": ["Vitamin C", "Hyaluronic Acid"], "price": {"amount": 699}}
            product_b: {"keyIngredients": ["Niacinamide", "Salicylic Acid"], "price": {"amount": 799}}
        Output: {
            "commonIngredients": [],
            "uniqueToProductA": ["Vitamin C", "Hyaluronic Acid"],
            "uniqueToProductB": ["Niacinamide", "Salicylic Acid"],
            "priceDifference": 100,
            "cheaperProduct": "productA"
        }
    """
    ingredients_a = set(product_a.get("keyIngredients", []))
    ingredients_b = set(product_b.get("keyIngredients", []))
    
    # Find common and unique ingredients
    common_ingredients = list(ingredients_a & ingredients_b)
    unique_to_a = list(ingredients_a - ingredients_b)
    unique_to_b = list(ingredients_b - ingredients_a)
    
    # Compare prices
    price_a = product_a.get("price", {}).get("amount", 0)
    price_b = product_b.get("price", {}).get("amount", 0)
    price_difference = abs(price_a - price_b)
    
    if price_a < price_b:
        cheaper_product = "productA"
    elif price_b < price_a:
        cheaper_product = "productB"
    else:
        cheaper_product = "equal"
    
    # Compare benefits
    benefits_a = set(product_a.get("benefits", []))
    benefits_b = set(product_b.get("benefits", []))
    common_benefits = list(benefits_a & benefits_b)
    unique_benefits_a = list(benefits_a - benefits_b)
    unique_benefits_b = list(benefits_b - benefits_a)
    
    return {
        "commonIngredients": sorted(common_ingredients),
        "uniqueToProductA": sorted(unique_to_a),
        "uniqueToProductB": sorted(unique_to_b),
        "commonBenefits": sorted(common_benefits),
        "uniqueBenefitsA": sorted(unique_benefits_a),
        "uniqueBenefitsB": sorted(unique_benefits_b),
        "priceDifference": price_difference,
        "cheaperProduct": cheaper_product
    }
