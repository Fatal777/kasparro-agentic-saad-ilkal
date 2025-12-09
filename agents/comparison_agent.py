"""
Comparison Agent - Production-grade product comparison generator.

Generates structured comparison page with rule-based recommendations.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.models import (
    ComparisonPageData,
    ProductSummary,
    ComparisonSection
)
from core.logging import get_agent_logger, log_step


class ComparisonAgent:
    """
    Agent for generating comparison page content.
    
    Responsibility: Generate comparison between Product A & B
    Input: Two ProductModels, ComparisonBlock output
    Output: ComparisonPageData
    Dependencies: Parser Agent, Comparison Block
    
    Production Features:
        - Structured comparison sections
        - Rule-based recommendation generation
        - Type-safe Pydantic output
    """
    
    def __init__(self):
        """Initialize the Comparison Agent."""
        self.logger = get_agent_logger("ComparisonAgent")
    
    @log_step("generate_comparison")
    def process(
        self,
        product_a: dict,
        product_b: dict,
        comparison_data: dict
    ) -> ComparisonPageData:
        """
        Generate comparison page content.
        
        Args:
            product_a: Product A model.
            product_b: Product B model.
            comparison_data: Output from Comparison Block.
            
        Returns:
            ComparisonPageData with structured comparison.
        """
        name_a = product_a.get("productName", "Product A")
        name_b = product_b.get("productName", "Product B")
        
        self.logger.debug(f"Comparing: {name_a} vs {name_b}")
        
        # Build product summaries
        summary_a = self._build_product_summary(product_a)
        summary_b = self._build_product_summary(product_b)
        
        # Build comparison section
        comparison = self._build_comparison_section(
            product_a, 
            product_b, 
            comparison_data
        )
        
        self.logger.info(f"Generated comparison: {name_a} vs {name_b}")
        
        return ComparisonPageData(
            success=True,
            productA=summary_a,
            productB=summary_b,
            comparison=comparison
        )
    
    def _build_product_summary(self, product: dict) -> ProductSummary:
        """Build ProductSummary from product model."""
        price_data = product.get("price", {})
        
        if isinstance(price_data, dict):
            price_amount = price_data.get("amount", 0)
            currency = price_data.get("currency", "INR")
        else:
            price_amount = 0
            currency = "INR"
        
        return ProductSummary(
            name=product.get("productName", ""),
            concentration=product.get("concentration", ""),
            price=price_amount,
            currency=currency,
            benefits=product.get("benefits", []),
            ingredients=product.get("keyIngredients", []),
            skinTypes=product.get("skinType", [])
        )
    
    def _build_comparison_section(
        self,
        product_a: dict,
        product_b: dict,
        comparison_data: dict
    ) -> ComparisonSection:
        """Build ComparisonSection with recommendation."""
        recommendation = self._generate_recommendation(
            product_a,
            product_b,
            comparison_data
        )
        
        return ComparisonSection(
            commonIngredients=comparison_data.get("commonIngredients", []),
            uniqueToA=comparison_data.get("uniqueToProductA", []),
            uniqueToB=comparison_data.get("uniqueToProductB", []),
            commonBenefits=comparison_data.get("commonBenefits", []),
            uniqueBenefitsA=comparison_data.get("uniqueBenefitsA", []),
            uniqueBenefitsB=comparison_data.get("uniqueBenefitsB", []),
            priceDifference=comparison_data.get("priceDifference", 0),
            cheaperProduct=comparison_data.get("cheaperProduct", "equal"),
            recommendation=recommendation
        )
    
    def _generate_recommendation(
        self,
        product_a: dict,
        product_b: dict,
        comparison_data: dict
    ) -> str:
        """
        Generate rule-based recommendation.
        
        All recommendations are derived from the data - no hallucination.
        """
        name_a = product_a.get("productName", "Product A")
        name_b = product_b.get("productName", "Product B")
        
        price_a = self._get_price_amount(product_a)
        price_b = self._get_price_amount(product_b)
        price_diff = comparison_data.get("priceDifference", 0)
        cheaper = comparison_data.get("cheaperProduct", "equal")
        
        benefits_a = product_a.get("benefits", [])
        benefits_b = product_b.get("benefits", [])
        
        skin_a = product_a.get("skinType", [])
        skin_b = product_b.get("skinType", [])
        
        parts = []
        
        # Price comparison
        if cheaper == "productA" and price_diff > 0:
            parts.append(f"{name_a} is more affordable by ₹{price_diff}")
        elif cheaper == "productB" and price_diff > 0:
            parts.append(f"{name_b} is more affordable by ₹{price_diff}")
        elif cheaper == "equal":
            parts.append("Both products are equally priced")
        
        # Primary benefit focus
        if benefits_a:
            parts.append(f"{name_a} focuses on {', '.join(benefits_a).lower()}")
        if benefits_b:
            parts.append(f"{name_b} focuses on {', '.join(benefits_b).lower()}")
        
        # Skin type recommendation
        common_skin = set(skin_a) & set(skin_b)
        if common_skin:
            parts.append(f"Both are suitable for {', '.join(common_skin).lower()} skin")
        
        if parts:
            return ". ".join(parts) + "."
        
        return "Both products offer unique benefits suitable for different skincare needs."
    
    def _get_price_amount(self, product: dict) -> float:
        """Extract price amount from product."""
        price = product.get("price", {})
        if isinstance(price, dict):
            return price.get("amount", 0)
        return 0
