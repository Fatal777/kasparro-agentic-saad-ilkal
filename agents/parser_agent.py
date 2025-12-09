"""
Parser Agent - Converts raw product data into internal model.

This agent is responsible for parsing and validating raw product data,
converting it into a clean internal model structure.
"""


class ParserAgent:
    """
    Agent for parsing raw product data into structured internal model.
    
    Responsibility: Convert raw data -> internal model
    Input: dict - Raw product data
    Output: dict - Structured ProductModel
    Dependencies: None
    """
    
    def __init__(self):
        """Initialize the Parser Agent."""
        self.required_fields = [
            "productName",
            "keyIngredients",
            "benefits",
            "price"
        ]
    
    def process(self, input_data: dict) -> dict:
        """
        Process raw product data and return structured internal model.
        
        Args:
            input_data: Raw product data dictionary.
            
        Returns:
            Structured ProductModel dictionary.
            
        Raises:
            ValueError: If required fields are missing.
        """
        # Validate required fields
        missing_fields = [
            field for field in self.required_fields 
            if field not in input_data
        ]
        
        if missing_fields:
            return {
                "success": False,
                "error": f"Missing required fields: {missing_fields}",
                "data": None
            }
        
        # Build internal model with normalized structure
        product_model = {
            "productName": input_data.get("productName", ""),
            "concentration": input_data.get("concentration", ""),
            "skinType": self._normalize_list(input_data.get("skinType", [])),
            "keyIngredients": self._normalize_list(input_data.get("keyIngredients", [])),
            "benefits": self._normalize_list(input_data.get("benefits", [])),
            "howToUse": input_data.get("howToUse", ""),
            "sideEffects": input_data.get("sideEffects", ""),
            "price": self._normalize_price(input_data.get("price", {}))
        }
        
        return {
            "success": True,
            "error": None,
            "data": product_model
        }
    
    def _normalize_list(self, value) -> list:
        """Ensure value is a list."""
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [value]
        return []
    
    def _normalize_price(self, price_data) -> dict:
        """Normalize price data structure."""
        if isinstance(price_data, dict):
            return {
                "amount": price_data.get("amount", 0),
                "currency": price_data.get("currency", "INR")
            }
        if isinstance(price_data, (int, float)):
            return {"amount": price_data, "currency": "INR"}
        return {"amount": 0, "currency": "INR"}
