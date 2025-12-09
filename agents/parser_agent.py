"""
Parser Agent - Production-grade product data parser.

Converts raw product data into validated internal model with
type safety, error handling, and logging.
"""

import sys
from pathlib import Path
from typing import Optional

# Add project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.models import ProductModel, Price, AgentResult
from core.logging import get_agent_logger, log_step
from core.errors import ValidationError, retry_with_backoff


class ParserAgent:
    """
    Agent for parsing raw product data into validated internal model.
    
    Responsibility: Convert raw data -> validated ProductModel
    Input: dict - Raw product data
    Output: AgentResult with ProductModel
    Dependencies: None (first in DAG)
    
    Production Features:
        - Pydantic validation
        - Structured logging
        - Error handling with context
    """
    
    REQUIRED_FIELDS = ["productName", "keyIngredients", "benefits", "price"]
    
    def __init__(self):
        """Initialize the Parser Agent."""
        self.logger = get_agent_logger("ParserAgent")
    
    @log_step("parse_product")
    def process(self, input_data: dict) -> AgentResult:
        """
        Process raw product data and return validated model.
        
        Args:
            input_data: Raw product data dictionary.
            
        Returns:
            AgentResult with validated ProductModel or error.
        """
        self.logger.debug(f"Processing product: {input_data.get('productName', 'unknown')}")
        
        try:
            # Step 1: Validate required fields exist
            self._validate_required_fields(input_data)
            
            # Step 2: Normalize data
            normalized = self._normalize_data(input_data)
            
            # Step 3: Create validated Pydantic model
            product_model = ProductModel(**normalized)
            
            self.logger.info(f"Successfully parsed: {product_model.productName}")
            
            return AgentResult(
                success=True,
                error=None,
                data=product_model.model_dump()
            )
            
        except ValidationError as e:
            self.logger.error(f"Validation failed: {e}")
            return AgentResult(
                success=False,
                error=str(e),
                data=None
            )
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return AgentResult(
                success=False,
                error=f"Parse error: {str(e)}",
                data=None
            )
    
    def _validate_required_fields(self, data: dict) -> None:
        """Validate that required fields are present."""
        missing = [f for f in self.REQUIRED_FIELDS if f not in data]
        
        if missing:
            raise ValidationError(
                f"Missing required fields: {missing}",
                field=",".join(missing)
            )
    
    def _normalize_data(self, data: dict) -> dict:
        """Normalize raw data into expected format."""
        # Handle price normalization
        price_data = data.get("price", {})
        if isinstance(price_data, (int, float)):
            price = Price(amount=price_data, currency="INR")
        elif isinstance(price_data, dict):
            price = Price(
                amount=price_data.get("amount", 0),
                currency=price_data.get("currency", "INR")
            )
        else:
            price = Price(amount=0, currency="INR")
        
        # Handle skin type normalization
        skin_type = data.get("skinType", [])
        if isinstance(skin_type, str):
            skin_type = [skin_type]
        
        return {
            "productName": str(data.get("productName", "")).strip(),
            "concentration": str(data.get("concentration", "")).strip(),
            "skinType": list(skin_type),
            "keyIngredients": list(data.get("keyIngredients", [])),
            "benefits": list(data.get("benefits", [])),
            "howToUse": str(data.get("howToUse", "")).strip(),
            "sideEffects": str(data.get("sideEffects", "")).strip(),
            "price": price
        }
