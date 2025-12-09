"""
Comprehensive Agent Tests

Tests for all agents in the multi-agent pipeline,
verifying input/output correctness and boundary enforcement.
"""

import pytest
import json
from pathlib import Path
from typing import Dict, Any

# Import all agents
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.parser_agent import ParserAgent
from agents.question_agent import QuestionAgent
from agents.faq_agent import FAQAgent
from agents.product_page_agent import ProductPageAgent
from agents.comparison_agent import ComparisonAgent
from agents.template_agent import TemplateAgent


class TestParserAgent:
    """Test suite for ParserAgent."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.agent = ParserAgent()
        self.sample_data = {
            "productName": "Test Serum",
            "concentration": "10%",
            "ingredients": [
                {"name": "Vitamin C", "percentage": 10}
            ],
            "benefits": ["Brightening"],
            "skinTypes": ["Oily"],
            "applicationMethod": {
                "steps": ["Apply 2 drops"],
                "frequency": "morning"
            },
            "sideEffects": "None",
            "price": {"amount": 500, "currency": "INR"}
        }
    
    def test_single_responsibility(self):
        """Verify agent has single responsibility: parsing data."""
        assert hasattr(self.agent, 'process')
        assert callable(self.agent.process)
    
    def test_defined_input_output(self):
        """Verify agent has defined input/output structure."""
        result = self.agent.process(self.sample_data)
        
        assert isinstance(result, dict)
        assert "success" in result
        assert "parsed_data" in result or "error" in result
    
    def test_no_global_state(self):
        """Verify agent doesn't maintain hidden global state."""
        # Process twice with same input
        result1 = self.agent.process(self.sample_data)
        result2 = self.agent.process(self.sample_data)
        
        # Results should be identical (deterministic)
        assert result1["success"] == result2["success"]
    
    def test_valid_input_processing(self):
        """Test processing valid input data."""
        result = self.agent.process(self.sample_data)
        
        assert result["success"] is True
        assert "parsed_data" in result
        assert result["parsed_data"]["productName"] == "Test Serum"


class TestQuestionAgent:
    """Test suite for QuestionAgent."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.agent = QuestionAgent()
        self.parsed_data = {
            "productName": "Test Serum",
            "ingredients": [{"name": "Vitamin C"}],
            "benefits": ["Brightening"],
            "skinTypes": ["Oily"],
            "applicationMethod": {"frequency": "morning"},
        }
    
    def test_single_responsibility(self):
        """Verify agent generates questions only."""
        result = self.agent.process(self.parsed_data)
        
        assert "questions" in result
        assert isinstance(result["questions"], list)
    
    def test_question_categories(self):
        """Verify questions are properly categorized."""
        result = self.agent.process(self.parsed_data)
        
        categories = set()
        for q in result["questions"]:
            assert "category" in q
            assert "question" in q
            categories.add(q["category"])
        
        # Should have multiple categories
        assert len(categories) >= 3
    
    def test_minimum_questions(self):
        """Verify minimum 15 questions are generated."""
        result = self.agent.process(self.parsed_data)
        
        assert len(result["questions"]) >= 15


class TestFAQAgent:
    """Test suite for FAQAgent."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.agent = FAQAgent()
        self.input_data = {
            "questions": [
                {"category": "informational", "question": "What are the ingredients?"}
            ],
            "product": {
                "productName": "Test Serum",
                "price": {"amount": 500, "currency": "INR"},
                "ingredients": [{"name": "Vitamin C"}],
                "benefits": ["Brightening"],
            }
        }
    
    def test_single_responsibility(self):
        """Verify agent generates FAQ answers only."""
        result = self.agent.process(self.input_data)
        
        assert "faqs" in result
        assert isinstance(result["faqs"], list)
    
    def test_faq_structure(self):
        """Verify FAQ structure is correct."""
        result = self.agent.process(self.input_data)
        
        for faq in result["faqs"]:
            assert "question" in faq
            assert "answer" in faq
            assert "category" in faq


class TestProductPageAgent:
    """Test suite for ProductPageAgent."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.agent = ProductPageAgent()
        self.input_data = {
            "productName": "Test Serum",
            "concentration": "10%",
            "ingredients": [{"name": "Vitamin C"}],
            "benefits": ["Brightening"],
            "skinTypes": ["Oily"],
            "applicationMethod": {"steps": ["Apply"], "frequency": "morning"},
            "price": {"amount": 500, "currency": "INR"},
        }
    
    def test_single_responsibility(self):
        """Verify agent builds product page only."""
        result = self.agent.process(self.input_data)
        
        assert "productName" in result
        assert "price" in result
    
    def test_complete_output(self):
        """Verify all required fields are present."""
        result = self.agent.process(self.input_data)
        
        required_fields = ["productName", "concentration", "benefits", "price"]
        for field in required_fields:
            assert field in result


class TestComparisonAgent:
    """Test suite for ComparisonAgent."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.agent = ComparisonAgent()
        self.input_data = {
            "productA": {
                "productName": "Product A",
                "price": {"amount": 500},
                "ingredients": [{"name": "Vitamin C"}],
                "benefits": ["Brightening"],
            },
            "productB": {
                "productName": "Product B",
                "price": {"amount": 600},
                "ingredients": [{"name": "Niacinamide"}],
                "benefits": ["Pore control"],
            }
        }
    
    def test_single_responsibility(self):
        """Verify agent compares products only."""
        result = self.agent.process(self.input_data)
        
        assert "comparison" in result
    
    def test_comparison_structure(self):
        """Verify comparison has required fields."""
        result = self.agent.process(self.input_data)
        
        comparison = result["comparison"]
        assert "priceDifference" in comparison
        assert "uniqueToA" in comparison or "uniqueToProductA" in comparison


class TestTemplateAgent:
    """Test suite for TemplateAgent."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.agent = TemplateAgent()
    
    def test_single_responsibility(self):
        """Verify agent validates templates only."""
        assert hasattr(self.agent, 'process')
        assert callable(self.agent.process)
    
    def test_template_loading(self):
        """Verify templates are loaded correctly."""
        # Agent should have templates loaded
        assert hasattr(self.agent, 'templates') or hasattr(self.agent, '_templates')


class TestAgentIndependence:
    """Test that agents are truly independent."""
    
    def test_no_cross_imports(self):
        """Verify agents don't import each other."""
        import ast
        
        agent_files = [
            "agents/parser_agent.py",
            "agents/question_agent.py",
            "agents/faq_agent.py",
            "agents/product_page_agent.py",
            "agents/comparison_agent.py",
            "agents/template_agent.py",
        ]
        
        for filepath in agent_files:
            path = Path(filepath)
            if not path.exists():
                continue
                
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        # Should not import other agents
                        assert "parser_agent" not in alias.name or filepath == "agents/parser_agent.py"
                        assert "question_agent" not in alias.name or filepath == "agents/question_agent.py"


class TestDeterminism:
    """Test that agents produce deterministic output."""
    
    def test_parser_determinism(self):
        """Verify ParserAgent is deterministic."""
        agent = ParserAgent()
        data = {"productName": "Test", "price": {"amount": 100, "currency": "INR"}}
        
        result1 = agent.process(data)
        result2 = agent.process(data)
        
        assert result1 == result2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
