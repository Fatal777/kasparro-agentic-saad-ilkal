"""
Unit tests for Agents.

Each test validates agent input/output contracts and single responsibility.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.parser_agent import ParserAgent
from agents.question_agent import QuestionAgent


class TestParserAgent:
    """Tests for parser_agent.py"""
    
    def test_parse_valid_product(self):
        """Test parsing valid product data."""
        agent = ParserAgent()
        
        input_data = {
            "productName": "Test Serum",
            "concentration": "10% Vitamin C",
            "skinType": ["Oily"],
            "keyIngredients": ["Vitamin C"],
            "benefits": ["Brightening"],
            "howToUse": "Apply daily",
            "sideEffects": "None",
            "price": {"amount": 500, "currency": "INR"}
        }
        
        result = agent.process(input_data)
        
        assert result["success"] is True
        assert result["data"]["productName"] == "Test Serum"
        assert result["data"]["price"]["amount"] == 500
    
    def test_parse_missing_required_fields(self):
        """Test parsing with missing required fields."""
        agent = ParserAgent()
        
        input_data = {
            "productName": "Test Serum"
            # Missing keyIngredients, benefits, price
        }
        
        result = agent.process(input_data)
        
        assert result["success"] is False
        assert "Missing required fields" in result["error"]
    
    def test_parse_normalize_price_number(self):
        """Test price normalization from number."""
        agent = ParserAgent()
        
        input_data = {
            "productName": "Test",
            "keyIngredients": ["A"],
            "benefits": ["B"],
            "price": 699  # Plain number
        }
        
        result = agent.process(input_data)
        
        assert result["success"] is True
        assert result["data"]["price"]["amount"] == 699
        assert result["data"]["price"]["currency"] == "INR"


class TestQuestionAgent:
    """Tests for question_agent.py"""
    
    def test_generate_questions_count(self):
        """Test that 15+ questions are generated."""
        agent = QuestionAgent()
        
        product_model = {
            "productName": "GlowBoost Serum",
            "keyIngredients": ["Vitamin C", "Hyaluronic Acid"],
            "benefits": ["Brightening"],
            "skinType": ["Oily"],
            "concentration": "10%",
            "price": {"amount": 699, "currency": "INR"}
        }
        
        result = agent.process(product_model)
        
        assert result["success"] is True
        assert result["totalQuestions"] >= 15
    
    def test_generate_questions_categories(self):
        """Test that all categories are covered."""
        agent = QuestionAgent()
        
        product_model = {
            "productName": "Test Serum",
            "keyIngredients": ["A"],
            "benefits": ["B"],
            "skinType": [],
            "concentration": "",
            "price": {"amount": 100, "currency": "INR"}
        }
        
        result = agent.process(product_model)
        
        # Check all categories have at least one question
        categories = result["categoryCounts"]
        assert categories["informational"] >= 1
        assert categories["safety"] >= 1
        assert categories["usage"] >= 1
        assert categories["purchase"] >= 1
        assert categories["comparison"] >= 1


def run_tests():
    """Run all tests and print results."""
    test_classes = [
        TestParserAgent,
        TestQuestionAgent
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
