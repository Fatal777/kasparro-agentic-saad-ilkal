"""
Product Page Agent - Production-grade product description generator.

Generates structured product page content with type-safe output.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.models import (
    ProductPageData, 
    BenefitsSection, 
    UsageSection,
    Price
)
from core.logging import get_agent_logger, log_step


class ProductPageAgent:
    """
    Agent for generating product description page content.
    
    Responsibility: Generate product description page
    Input: ProductModel, logic block outputs
    Output: ProductPageData
    Dependencies: Parser Agent, Benefits/Usage/Ingredient Blocks
    
    Production Features:
        - Type-safe Pydantic output
        - Structured sections
        - Complete product representation
    """
    
    def __init__(self):
        """Initialize the Product Page Agent."""
        self.logger = get_agent_logger("ProductPageAgent")
    
    @log_step("generate_product_page")
    def process(
        self,
        product_model: dict,
        benefits_data: dict,
        usage_data: dict,
        ingredient_data: dict
    ) -> ProductPageData:
        """
        Generate product page content.
        
        Args:
            product_model: Structured product model.
            benefits_data: Output from Benefits Block.
            usage_data: Output from Usage Block.
            ingredient_data: Output from Ingredient Block.
            
        Returns:
            ProductPageData with complete product information.
        """
        product_name = product_model.get("productName", "")
        self.logger.debug(f"Generating product page for: {product_name}")
        
        # Build benefits section
        benefits = BenefitsSection(
            items=benefits_data.get("benefitList", []),
            primary=benefits_data.get("primaryBenefit", ""),
            count=benefits_data.get("benefitCount", 0)
        )
        
        # Build usage section
        usage = UsageSection(
            instructions=usage_data.get("usageInstructions", ""),
            frequency=usage_data.get("frequency") or "",
            quantity=usage_data.get("quantity") or "",
            timing=usage_data.get("timing") or ""
        )
        
        # Build price
        price_data = product_model.get("price", {})
        if isinstance(price_data, dict):
            price = Price(
                amount=price_data.get("amount", 0),
                currency=price_data.get("currency", "INR")
            )
        else:
            price = Price(amount=0, currency="INR")
        
        self.logger.info(f"Generated product page for: {product_name}")
        
        return ProductPageData(
            success=True,
            productName=product_name,
            concentration=product_model.get("concentration", ""),
            skinTypes=product_model.get("skinType", []),
            keyIngredients=ingredient_data.get("ingredientList", []),
            benefits=benefits,
            usage=usage,
            sideEffects=product_model.get("sideEffects", ""),
            price=price
        )
