"""
Integration test for Orchestrator.

Tests the full pipeline execution.
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.orchestrator import Orchestrator


class TestOrchestrator:
    """Integration tests for orchestrator.py"""
    
    def test_full_pipeline(self):
        """Test complete pipeline execution."""
        orchestrator = Orchestrator()
        result = orchestrator.run()
        
        assert result["success"] is True
        assert "outputs" in result
        assert "faq" in result["outputs"]
        assert "product_page" in result["outputs"]
        assert "comparison_page" in result["outputs"]
    
    def test_faq_output_valid(self):
        """Test FAQ output is valid JSON with required fields."""
        output_path = Path("output/faq.json")
        
        if output_path.exists():
            with open(output_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            assert "productName" in data
            assert "faqs" in data
            assert len(data["faqs"]) >= 5  # Min 5 Q&As
            
            # Check FAQ structure
            for faq in data["faqs"]:
                assert "id" in faq
                assert "category" in faq
                assert "question" in faq
                assert "answer" in faq
    
    def test_product_output_valid(self):
        """Test product page output is valid JSON."""
        output_path = Path("output/product_page.json")
        
        if output_path.exists():
            with open(output_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            assert "productName" in data
            assert "benefits" in data
            assert "usage" in data
            assert "price" in data
    
    def test_comparison_output_valid(self):
        """Test comparison page output is valid JSON."""
        output_path = Path("output/comparison_page.json")
        
        if output_path.exists():
            with open(output_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            assert "productA" in data
            assert "productB" in data
            assert "comparison" in data
            assert "priceDifference" in data["comparison"]


def run_tests():
    """Run all tests and print results."""
    test_class = TestOrchestrator
    
    total_passed = 0
    total_failed = 0
    
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
            except Exception as e:
                print(f"  ✗ {method_name}: {type(e).__name__}: {e}")
                total_failed += 1
    
    print("\n" + "=" * 40)
    print(f"Results: {total_passed} passed, {total_failed} failed")
    
    return total_failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
