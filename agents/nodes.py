"""
LangGraph Agent Nodes using Independent Gemini Agents

Each node instantiates an independent agent that:
1. Has its own LLM instance (Gemini)
2. Runs independently without knowing about other agents
3. Makes real API calls to Google Gemini
"""

import os
import json
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

from dotenv import load_dotenv

from core.graph_state import AgentState
from agents.llm_agents import (
    QuestionGeneratorAgent,
    FAQGeneratorAgent,
    ProductPageAgent,
    ComparisonAgent
)

# Load environment variables
load_dotenv()


# ==================== PARSE PRODUCTS NODE ====================

def parse_products_node(state: AgentState) -> Dict[str, Any]:
    """
    Parse raw product data into structured format.
    This node validates and structures the input data.
    """
    log = [f"[{datetime.now().isoformat()}] PARSE_PRODUCTS: Starting..."]
    
    product_a = state["raw_product_a"]
    product_b = state["raw_product_b"]
    
    log.append(f"  ✓ Parsed: {product_a.get('productName', 'Unknown')}")
    log.append(f"  ✓ Parsed: {product_b.get('productName', 'Unknown')}")
    log.append(f"[{datetime.now().isoformat()}] PARSE_PRODUCTS: Completed")
    
    return {
        "product_a": product_a,
        "product_b": product_b,
        "execution_log": log
    }


# ==================== LOGIC BLOCKS NODE ====================

def run_logic_blocks_node(state: AgentState) -> Dict[str, Any]:
    """
    Run pure-function logic blocks to extract structured data.
    """
    log = [f"[{datetime.now().isoformat()}] LOGIC_BLOCKS: Starting..."]
    
    product_a = state["product_a"]
    product_b = state["product_b"]
    
    # Benefits block
    benefits = product_a.get("benefits", [])
    benefits_data = {
        "items": benefits,
        "primary": benefits[0] if benefits else "",
        "count": len(benefits)
    }
    log.append(f"  ✓ Benefits: {len(benefits)} items")
    
    # Usage block
    app_method = product_a.get("applicationMethod", {})
    usage_data = {
        "instructions": " ".join(app_method.get("steps", [])),
        "frequency": app_method.get("frequency", ""),
        "quantity": "2-3 drops",
        "timing": "before sunscreen"
    }
    log.append(f"  ✓ Usage: frequency={usage_data['frequency']}")
    
    # Ingredients block
    ingredients = product_a.get("ingredients", [])
    ingredients_data = {
        "items": [i.get("name", i) if isinstance(i, dict) else i for i in ingredients],
        "count": len(ingredients)
    }
    log.append(f"  ✓ Ingredients: {len(ingredients)} items")
    
    # Comparison block
    price_a = product_a.get("price", {}).get("amount", 0)
    price_b = product_b.get("price", {}).get("amount", 0)
    
    ingredients_a = set(i.get("name", i) if isinstance(i, dict) else i for i in product_a.get("ingredients", []))
    ingredients_b = set(i.get("name", i) if isinstance(i, dict) else i for i in product_b.get("ingredients", []))
    
    comparison_data = {
        "priceDifference": abs(price_a - price_b),
        "cheaperProduct": "productA" if price_a <= price_b else "productB",
        "commonIngredients": list(ingredients_a & ingredients_b),
        "uniqueToA": list(ingredients_a - ingredients_b),
        "uniqueToB": list(ingredients_b - ingredients_a)
    }
    log.append(f"  ✓ Comparison: price diff=₹{comparison_data['priceDifference']}")
    log.append(f"[{datetime.now().isoformat()}] LOGIC_BLOCKS: Completed")
    
    return {
        "benefits_data": benefits_data,
        "usage_data": usage_data,
        "ingredients_data": ingredients_data,
        "comparison_data": comparison_data,
        "execution_log": log
    }


# ==================== GENERATE QUESTIONS NODE ====================

def generate_questions_node(state: AgentState) -> Dict[str, Any]:
    """
    Generate questions using independent QuestionGeneratorAgent.
    
    The agent has its own Gemini LLM instance and runs independently.
    """
    log = [f"[{datetime.now().isoformat()}] GENERATE_QUESTIONS: Invoking QuestionGeneratorAgent..."]
    
    # Create independent agent
    agent = QuestionGeneratorAgent()
    
    # Agent runs with its own LLM
    result = agent.run(state["product_a"])
    
    questions = result.get("questions", [])
    
    # Count by category
    categories = {}
    for q in questions:
        cat = q.get("category", "other")
        categories[cat] = categories.get(cat, 0) + 1
    
    log.append(f"  ✓ Agent generated {len(questions)} questions via Gemini LLM")
    for cat, count in categories.items():
        log.append(f"    - {cat}: {count}")
    log.append(f"[{datetime.now().isoformat()}] GENERATE_QUESTIONS: Completed")
    
    return {
        "questions": questions,
        "execution_log": log
    }


# ==================== GENERATE FAQ NODE ====================

def generate_faq_node(state: AgentState) -> Dict[str, Any]:
    """
    Generate FAQ using independent FAQGeneratorAgent.
    """
    log = [f"[{datetime.now().isoformat()}] GENERATE_FAQ: Invoking FAQGeneratorAgent..."]
    
    # Create independent agent
    agent = FAQGeneratorAgent()
    
    # Agent runs with its own LLM
    result = agent.run({
        "product": state["product_a"],
        "questions": state["questions"]
    })
    
    faq_count = len(result.get("faqs", []))
    log.append(f"  ✓ Agent generated {faq_count} FAQ answers via Gemini LLM")
    log.append(f"[{datetime.now().isoformat()}] GENERATE_FAQ: Completed")
    
    return {
        "faq_output": result,
        "execution_log": log
    }


# ==================== GENERATE PRODUCT PAGE NODE ====================

def generate_product_node(state: AgentState) -> Dict[str, Any]:
    """
    Generate product page using independent ProductPageAgent.
    """
    log = [f"[{datetime.now().isoformat()}] GENERATE_PRODUCT: Invoking ProductPageAgent..."]
    
    # Create independent agent
    agent = ProductPageAgent()
    
    # Agent runs with its own LLM
    result = agent.run(state["product_a"])
    
    log.append(f"  ✓ Agent generated product page for {result.get('productName', 'Unknown')} via Gemini LLM")
    log.append(f"[{datetime.now().isoformat()}] GENERATE_PRODUCT: Completed")
    
    return {
        "product_output": result,
        "execution_log": log
    }


# ==================== GENERATE COMPARISON NODE ====================

def generate_comparison_node(state: AgentState) -> Dict[str, Any]:
    """
    Generate comparison using independent ComparisonAgent.
    """
    log = [f"[{datetime.now().isoformat()}] GENERATE_COMPARISON: Invoking ComparisonAgent..."]
    
    # Create independent agent
    agent = ComparisonAgent()
    
    # Agent runs with its own LLM
    result = agent.run({
        "productA": state["product_a"],
        "productB": state["product_b"]
    })
    
    log.append(f"  ✓ Agent generated comparison via Gemini LLM")
    log.append(f"[{datetime.now().isoformat()}] GENERATE_COMPARISON: Completed")
    
    return {
        "comparison_output": result,
        "execution_log": log
    }


# ==================== WRITE OUTPUTS NODE ====================

def write_outputs_node(state: AgentState) -> Dict[str, Any]:
    """
    Write final JSON outputs to files.
    """
    log = [f"[{datetime.now().isoformat()}] WRITE_OUTPUTS: Starting..."]
    
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Write FAQ
    if state.get("faq_output"):
        with open(output_dir / "faq.json", "w", encoding="utf-8") as f:
            json.dump(state["faq_output"], f, indent=2, ensure_ascii=False)
        log.append(f"  ✓ Written: output/faq.json")
    
    # Write Product Page
    if state.get("product_output"):
        with open(output_dir / "product_page.json", "w", encoding="utf-8") as f:
            json.dump(state["product_output"], f, indent=2, ensure_ascii=False)
        log.append(f"  ✓ Written: output/product_page.json")
    
    # Write Comparison Page
    if state.get("comparison_output"):
        with open(output_dir / "comparison_page.json", "w", encoding="utf-8") as f:
            json.dump(state["comparison_output"], f, indent=2, ensure_ascii=False)
        log.append(f"  ✓ Written: output/comparison_page.json")
    
    log.append(f"[{datetime.now().isoformat()}] WRITE_OUTPUTS: Completed")
    
    return {
        "outputs_written": True,
        "execution_log": log
    }
