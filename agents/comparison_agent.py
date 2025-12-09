"""
Comparison Agent - Generates comparison page content.

This agent is responsible for generating the comparison page
between Product A and Product B using comparison block data.
"""


class ComparisonAgent:
    """
    Agent for generating comparison page content.
    
    Responsibility: Generate comparison between Product A & B
    Input: ProductModel A, ProductModel B, ComparisonBlock output
    Output: ComparisonPageData dict
    Dependencies: Parser Agent, Comparison Block
    """
    
    def __init__(self):
        """Initialize the Comparison Agent."""
        pass
    
    def process(
        self,
        product_a: dict,
        product_b: dict,
        comparison_data: dict
    ) -> dict:
        """
        Generate comparison page content.
        
        Args:
            product_a: Structured product model for Product A.
            product_b: Structured product model for Product B.
            comparison_data: Output from Comparison Block.
            
        Returns:
            ComparisonPageData dictionary.
        """
        # Generate recommendation based on comparison
        recommendation = self._generate_recommendation(
            product_a, 
            product_b, 
            comparison_data
        )
        
        return {
            "success": True,
            "productA": {
                "name": product_a.get("productName", ""),
                "concentration": product_a.get("concentration", ""),
                "price": product_a.get("price", {}).get("amount", 0),
                "currency": product_a.get("price", {}).get("currency", "INR"),
                "benefits": product_a.get("benefits", []),
                "ingredients": product_a.get("keyIngredients", []),
                "skinTypes": product_a.get("skinType", [])
            },
            "productB": {
                "name": product_b.get("productName", ""),
                "concentration": product_b.get("concentration", ""),
                "price": product_b.get("price", {}).get("amount", 0),
                "currency": product_b.get("price", {}).get("currency", "INR"),
                "benefits": product_b.get("benefits", []),
                "ingredients": product_b.get("keyIngredients", []),
                "skinTypes": product_b.get("skinType", [])
            },
            "comparison": {
                "commonIngredients": comparison_data.get("commonIngredients", []),
                "uniqueToA": comparison_data.get("uniqueToProductA", []),
                "uniqueToB": comparison_data.get("uniqueToProductB", []),
                "commonBenefits": comparison_data.get("commonBenefits", []),
                "uniqueBenefitsA": comparison_data.get("uniqueBenefitsA", []),
                "uniqueBenefitsB": comparison_data.get("uniqueBenefitsB", []),
                "priceDifference": comparison_data.get("priceDifference", 0),
                "cheaperProduct": comparison_data.get("cheaperProduct", ""),
                "recommendation": recommendation
            }
        }
    
    def _generate_recommendation(
        self,
        product_a: dict,
        product_b: dict,
        comparison_data: dict
    ) -> str:
        """
        Generate recommendation based on comparison data.
        
        Rule-based recommendation without hallucination.
        """
        name_a = product_a.get("productName", "Product A")
        name_b = product_b.get("productName", "Product B")
        price_a = product_a.get("price", {}).get("amount", 0)
        price_b = product_b.get("price", {}).get("amount", 0)
        price_diff = comparison_data.get("priceDifference", 0)
        cheaper = comparison_data.get("cheaperProduct", "")
        
        benefits_a = product_a.get("benefits", [])
        benefits_b = product_b.get("benefits", [])
        
        # Build recommendation
        parts = []
        
        # Price comparison
        if cheaper == "productA" and price_diff > 0:
            parts.append(f"{name_a} is more affordable by ₹{price_diff}")
        elif cheaper == "productB" and price_diff > 0:
            parts.append(f"{name_b} is more affordable by ₹{price_diff}")
        elif cheaper == "equal":
            parts.append("Both products are priced equally")
        
        # Benefit focus
        if benefits_a:
            parts.append(f"{name_a} focuses on {', '.join(benefits_a)}")
        if benefits_b:
            parts.append(f"{name_b} focuses on {', '.join(benefits_b)}")
        
        return ". ".join(parts) + "." if parts else "Both products offer unique benefits."
