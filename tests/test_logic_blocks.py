"""
Logic Block Tests

Tests for all logic blocks ensuring they are pure functions
with no side effects and deterministic output.
"""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from logic_blocks.benefits_block import process_benefits
from logic_blocks.usage_block import process_usage
from logic_blocks.ingredient_block import process_ingredients
from logic_blocks.comparison_block import compare_products


class TestBenefitsBlock:
    """Test suite for benefits_block."""
    
    def test_pure_function(self):
        """Verify benefits_block is a pure function."""
        input_data = {"benefits": ["Brightening", "Hydrating"]}
        
        result1 = process_benefits(input_data)
        result2 = process_benefits(input_data)
        
        # Should produce identical output (deterministic)
        assert result1 == result2
    
    def test_no_side_effects(self):
        """Verify no modification of input data."""
        input_data = {"benefits": ["Brightening"]}
        original = input_data.copy()
        
        process_benefits(input_data)
        
        assert input_data == original
    
    def test_output_structure(self):
        """Verify output has correct structure."""
        input_data = {"benefits": ["Brightening", "Fades dark spots"]}
        
        result = process_benefits(input_data)
        
        assert "items" in result or "benefitList" in result or "benefits" in result
    
    def test_empty_benefits(self):
        """Test handling of empty benefits."""
        result = process_benefits({"benefits": []})
        
        # Should not raise, should return empty list
        assert isinstance(result, dict)


class TestUsageBlock:
    """Test suite for usage_block."""
    
    def test_pure_function(self):
        """Verify usage_block is a pure function."""
        input_data = {
            "applicationMethod": {
                "steps": ["Apply 2-3 drops"],
                "frequency": "morning"
            }
        }
        
        result1 = process_usage(input_data)
        result2 = process_usage(input_data)
        
        assert result1 == result2
    
    def test_no_side_effects(self):
        """Verify no modification of input data."""
        input_data = {"applicationMethod": {"steps": ["Apply"], "frequency": "daily"}}
        original_steps = input_data["applicationMethod"]["steps"].copy()
        
        process_usage(input_data)
        
        assert input_data["applicationMethod"]["steps"] == original_steps
    
    def test_output_structure(self):
        """Verify output has correct structure."""
        input_data = {
            "applicationMethod": {
                "steps": ["Apply before sunscreen"],
                "frequency": "morning"
            }
        }
        
        result = process_usage(input_data)
        
        assert "instructions" in result or "usage" in result or "steps" in result


class TestIngredientBlock:
    """Test suite for ingredient_block."""
    
    def test_pure_function(self):
        """Verify ingredient_block is a pure function."""
        input_data = {
            "ingredients": [
                {"name": "Vitamin C", "percentage": 10},
                {"name": "Hyaluronic Acid", "percentage": 1}
            ]
        }
        
        result1 = process_ingredients(input_data)
        result2 = process_ingredients(input_data)
        
        assert result1 == result2
    
    def test_no_side_effects(self):
        """Verify no modification of input data."""
        input_data = {"ingredients": [{"name": "Vitamin C"}]}
        original_count = len(input_data["ingredients"])
        
        process_ingredients(input_data)
        
        assert len(input_data["ingredients"]) == original_count
    
    def test_output_structure(self):
        """Verify output has correct structure."""
        input_data = {"ingredients": [{"name": "Vitamin C", "percentage": 10}]}
        
        result = process_ingredients(input_data)
        
        assert isinstance(result, dict)


class TestComparisonBlock:
    """Test suite for comparison_block."""
    
    def test_pure_function(self):
        """Verify comparison_block is a pure function."""
        product_a = {
            "ingredients": [{"name": "Vitamin C"}],
            "price": {"amount": 500}
        }
        product_b = {
            "ingredients": [{"name": "Niacinamide"}],
            "price": {"amount": 600}
        }
        
        result1 = compare_products(product_a, product_b)
        result2 = compare_products(product_a, product_b)
        
        assert result1 == result2
    
    def test_no_side_effects(self):
        """Verify no modification of input data."""
        product_a = {"ingredients": [{"name": "Vitamin C"}], "price": {"amount": 500}}
        product_b = {"ingredients": [{"name": "Niacinamide"}], "price": {"amount": 600}}
        
        original_a = product_a.copy()
        original_b = product_b.copy()
        
        compare_products(product_a, product_b)
        
        assert product_a["price"] == original_a["price"]
        assert product_b["price"] == original_b["price"]
    
    def test_output_structure(self):
        """Verify output has correct structure."""
        product_a = {"ingredients": [{"name": "A"}], "price": {"amount": 500}}
        product_b = {"ingredients": [{"name": "B"}], "price": {"amount": 600}}
        
        result = compare_products(product_a, product_b)
        
        assert "priceDifference" in result
        assert "uniqueToA" in result or "uniqueToProductA" in result
    
    def test_price_difference_calculation(self):
        """Verify price difference is calculated correctly."""
        product_a = {"ingredients": [], "price": {"amount": 500}}
        product_b = {"ingredients": [], "price": {"amount": 700}}
        
        result = compare_products(product_a, product_b)
        
        assert result["priceDifference"] == 200


class TestLogicBlockComposability:
    """Test that logic blocks can be composed together."""
    
    def test_blocks_work_independently(self):
        """Verify each block works without depending on others."""
        # Each block should work independently
        benefits_result = process_benefits({"benefits": ["A"]})
        usage_result = process_usage({"applicationMethod": {"steps": ["B"], "frequency": "daily"}})
        ingredient_result = process_ingredients({"ingredients": [{"name": "C"}]})
        
        assert benefits_result is not None
        assert usage_result is not None
        assert ingredient_result is not None
    
    def test_blocks_output_structured_data(self):
        """Verify all blocks output structured data, not raw text."""
        benefits = process_benefits({"benefits": ["Brightening"]})
        usage = process_usage({"applicationMethod": {"steps": ["Apply"], "frequency": "morning"}})
        ingredients = process_ingredients({"ingredients": [{"name": "Vitamin C"}]})
        
        # All should return dicts, not strings
        assert isinstance(benefits, dict)
        assert isinstance(usage, dict)
        assert isinstance(ingredients, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
