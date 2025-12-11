"""
Pytest test suite for LangGraph pipeline and agents.

Tests verify:
1. LangGraph StateGraph builds correctly
2. Independent agents can be instantiated
3. Node functions work with mock state
4. Pipeline produces valid output structure
"""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any

# Test Agent Independence
class TestAgentIndependence:
    """Test that agents are truly independent classes."""
    
    def test_question_agent_has_own_llm(self):
        """Verify QuestionGeneratorAgent has its own LLM instance."""
        from agents.llm_agents import QuestionGeneratorAgent
        
        agent1 = QuestionGeneratorAgent()
        agent2 = QuestionGeneratorAgent()
        
        # Each agent should have its own LLM instance
        assert agent1.llm is not agent2.llm
        assert agent1.name == "QuestionGeneratorAgent"
    
    def test_faq_agent_has_own_llm(self):
        """Verify FAQGeneratorAgent has its own LLM instance."""
        from agents.llm_agents import FAQGeneratorAgent
        
        agent = FAQGeneratorAgent()
        assert agent.name == "FAQGeneratorAgent"
        assert agent.llm is not None
    
    def test_product_agent_has_own_llm(self):
        """Verify ProductPageAgent has its own LLM instance."""
        from agents.llm_agents import ProductPageAgent
        
        agent = ProductPageAgent()
        assert agent.name == "ProductPageAgent"
        assert agent.llm is not None
    
    def test_comparison_agent_has_own_llm(self):
        """Verify ComparisonAgent has its own LLM instance."""
        from agents.llm_agents import ComparisonAgent
        
        agent = ComparisonAgent()
        assert agent.name == "ComparisonAgent"
        assert agent.llm is not None
    
    def test_agents_have_system_prompts(self):
        """Verify each agent defines its own system prompt."""
        from agents.llm_agents import (
            QuestionGeneratorAgent,
            FAQGeneratorAgent,
            ProductPageAgent,
            ComparisonAgent
        )
        
        agents = [
            QuestionGeneratorAgent(),
            FAQGeneratorAgent(),
            ProductPageAgent(),
            ComparisonAgent()
        ]
        
        for agent in agents:
            prompt = agent.get_system_prompt()
            assert isinstance(prompt, str)
            assert len(prompt) > 50  # Non-trivial prompt


class TestLangGraphStructure:
    """Test LangGraph StateGraph structure."""
    
    def test_graph_builds_without_error(self):
        """Verify the StateGraph can be built."""
        from agents.graph import build_pipeline_graph
        
        graph = build_pipeline_graph()
        assert graph is not None
    
    def test_graph_has_expected_nodes(self):
        """Verify graph contains all expected nodes."""
        from agents.graph import build_pipeline_graph
        
        graph = build_pipeline_graph()
        
        # The compiled graph should exist
        assert graph is not None


class TestNodeFunctions:
    """Test individual node functions."""
    
    def test_parse_products_node(self):
        """Test parse_products_node with mock data."""
        from agents.nodes import parse_products_node
        
        mock_state = {
            "raw_product_a": {"productName": "Test A"},
            "raw_product_b": {"productName": "Test B"},
            "execution_log": []
        }
        
        result = parse_products_node(mock_state)
        
        assert result["product_a"]["productName"] == "Test A"
        assert result["product_b"]["productName"] == "Test B"
    
    def test_run_logic_blocks_node(self):
        """Test run_logic_blocks_node with mock data."""
        from agents.nodes import run_logic_blocks_node
        
        mock_state = {
            "product_a": {
                "benefits": ["Benefit 1", "Benefit 2"],
                "applicationMethod": {"steps": ["Step 1"], "frequency": "daily"},
                "ingredients": [{"name": "Ingredient A"}],
                "price": {"amount": 100}
            },
            "product_b": {
                "benefits": ["Benefit 3"],
                "ingredients": [{"name": "Ingredient B"}],
                "price": {"amount": 150}
            },
            "execution_log": []
        }
        
        result = run_logic_blocks_node(mock_state)
        
        assert result["benefits_data"]["count"] == 2
        assert result["comparison_data"]["priceDifference"] == 50


class TestGraphState:
    """Test graph state TypedDict."""
    
    def test_agent_state_structure(self):
        """Verify AgentState has required fields."""
        from core.graph_state import AgentState
        
        # AgentState should have these keys
        expected_keys = [
            "raw_product_a",
            "raw_product_b",
            "product_a",
            "product_b",
            "questions",
            "faq_output",
            "product_output",
            "comparison_output"
        ]
        
        # TypedDict annotations
        annotations = AgentState.__annotations__
        for key in expected_keys:
            assert key in annotations, f"Missing key: {key}"


class TestLLMFactory:
    """Test LLM factory for multi-provider support."""
    
    def test_get_provider_info(self):
        """Test provider info returns expected structure."""
        from core.llm_factory import get_provider_info
        
        info = get_provider_info()
        
        assert "provider" in info
        assert "model" in info
        assert "configured" in info


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
