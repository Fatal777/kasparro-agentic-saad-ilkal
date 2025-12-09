"""
Unit tests for Logic Blocks.

Each test validates that logic blocks are pure functions
producing deterministic output.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from logic_blocks.benefits_block import process_benefits
from logic_blocks.usage_block import process_usage
from logic_blocks.ingredient_block import process_ingredients
from logic_blocks.comparison_block import compare_products


class TestBenefitsBlock:
    """Tests for benefits_block.py"""
    
    def test_process_benefits_normal(self):
        """Test normal benefits processing."""
        input_data = {"benefits": ["Brightening", "Fades dark spots"]}
        result = process_benefits(input_data)
        
        assert result["benefitList"] == ["Brightening", "Fades dark spots"]
        assert result["benefitCount"] == 2
        assert result["primaryBenefit"] == "Brightening"
    
    def test_process_benefits_empty(self):
        """Test empty benefits list."""
        input_data = {"benefits": []}
        result = process_benefits(input_data)
        
        assert result["benefitList"] == []
        assert result["benefitCount"] == 0
        assert result["primaryBenefit"] is None
    
    def test_process_benefits_missing_key(self):
        """Test missing benefits key."""
        input_data = {}
        result = process_benefits(input_data)
        
        assert result["benefitList"] == []
        assert result["benefitCount"] == 0


class TestUsageBlock:
    """Tests for usage_block.py"""
    
    def test_process_usage_morning(self):
        """Test morning usage extraction."""
        input_data = {"howToUse": "Apply 2–3 drops in the morning before sunscreen"}
        result = process_usage(input_data)
        
        assert result["frequency"] == "morning"
        assert result["quantity"] == "2–3 drops"
        assert result["timing"] == "before sunscreen"
    
    def test_process_usage_morning_evening(self):
        """Test morning and evening usage."""
        input_data = {"howToUse": "Apply 3–4 drops morning and evening"}
        result = process_usage(input_data)
        
        assert result["frequency"] == "morning and evening"
        assert result["quantity"] == "3–4 drops"
    
    def test_process_usage_empty(self):
        """Test empty usage string."""
        input_data = {"howToUse": ""}
        result = process_usage(input_data)
        
        assert result["usageInstructions"] == ""
        assert result["frequency"] is None


class TestIngredientBlock:
    """Tests for ingredient_block.py"""
    
    def test_process_ingredients_normal(self):
        """Test normal ingredient processing."""
        input_data = {
            "keyIngredients": ["Vitamin C", "Hyaluronic Acid"],
            "concentration": "10% Vitamin C"
        }
        result = process_ingredients(input_data)
        
        assert result["ingredientList"] == ["Vitamin C", "Hyaluronic Acid"]
        assert result["ingredientCount"] == 2
        assert result["primaryActive"] == "Vitamin C"
        assert result["concentration"] == "10%"
    
    def test_process_ingredients_empty(self):
        """Test empty ingredients."""
        input_data = {"keyIngredients": [], "concentration": ""}
        result = process_ingredients(input_data)
        
        assert result["ingredientList"] == []
        assert result["ingredientCount"] == 0


class TestComparisonBlock:
    """Tests for comparison_block.py"""
    
    def test_compare_products_different(self):
        """Test products with different ingredients."""
        product_a = {
            "keyIngredients": ["Vitamin C", "Hyaluronic Acid"],
            "benefits": ["Brightening"],
            "price": {"amount": 699}
        }
        product_b = {
            "keyIngredients": ["Niacinamide", "Salicylic Acid"],
            "benefits": ["Controls oil"],
            "price": {"amount": 799}
        }
        
        result = compare_products(product_a, product_b)
        
        assert result["commonIngredients"] == []
        assert set(result["uniqueToProductA"]) == {"Vitamin C", "Hyaluronic Acid"}
        assert set(result["uniqueToProductB"]) == {"Niacinamide", "Salicylic Acid"}
        assert result["priceDifference"] == 100
        assert result["cheaperProduct"] == "productA"
    
    def test_compare_products_common_ingredient(self):
        """Test products with common ingredients."""
        product_a = {
            "keyIngredients": ["Vitamin C", "Hyaluronic Acid"],
            "benefits": [],
            "price": {"amount": 500}
        }
        product_b = {
            "keyIngredients": ["Vitamin C", "Niacinamide"],
            "benefits": [],
            "price": {"amount": 500}
        }
        
        result = compare_products(product_a, product_b)
        
        assert result["commonIngredients"] == ["Vitamin C"]
        assert result["cheaperProduct"] == "equal"


def run_tests():
    """Run all tests and print results."""
    test_classes = [
        TestBenefitsBlock,
        TestUsageBlock,
        TestIngredientBlock,
        TestComparisonBlock
    ]
    
    total_passed = 0
    total_failed = 0
    
    for test_class in test_classes:
        print(f"\n{test_class.__name__}")
        print("-" * 40)
        
        instance = test_class()
        for method_name in dir(instance):
            if method_name.startswith("test_"):
                try:
                    getattr(instance, method_name)()
                    print(f"  ✓ {method_name}")
                    total_passed += 1
                except AssertionError as e:
                    print(f"  ✗ {method_name}: {e}")
                    total_failed += 1
    
    print("\n" + "=" * 40)
    print(f"Results: {total_passed} passed, {total_failed} failed")
    
    return total_failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
