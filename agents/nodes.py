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
    
    try:
        # Safe access with valid defaults
        raw_a = state.get("raw_product_a", {})
        raw_b = state.get("raw_product_b", {})
        
        # Ensure we have at least dictionaries
        product_a = raw_a if isinstance(raw_a, dict) else {}
        product_b = raw_b if isinstance(raw_b, dict) else {}
        
        log.append(f"  ✓ Parsed: {product_a.get('productName', 'Unknown')}")
        log.append(f"  ✓ Parsed: {product_b.get('productName', 'Unknown')}")
        log.append(f"[{datetime.now().isoformat()}] PARSE_PRODUCTS: Completed")
        
        return {
            "product_a": product_a,
            "product_b": product_b,
            "execution_log": log
        }
    except Exception as e:
        log.append(f"  ❌ Error parsing products: {str(e)}")
        # Return empty dicts to prevent downstream crashes
        return {
            "product_a": {},
            "product_b": {},
            "execution_log": log
        }


# ==================== LOGIC BLOCKS NODE ====================

def run_logic_blocks_node(state: AgentState) -> Dict[str, Any]:
    """
    Run pure-function logic blocks to extract structured data.
    """
    log = [f"[{datetime.now().isoformat()}] LOGIC_BLOCKS: Starting..."]
    
    try:
        product_a = state.get("product_a", {})
        product_b = state.get("product_b", {})
        
        # Benefits block
        benefits = product_a.get("benefits", []) or []
        benefits_data = {
            "items": benefits,
            "primary": benefits[0] if benefits else "",
            "count": len(benefits)
        }
        log.append(f"  ✓ Benefits: {len(benefits)} items")
        
        # Usage block
        app_method = product_a.get("applicationMethod", {}) or {}
        usage_data = {
            "instructions": " ".join(app_method.get("steps", []) or []),
            "frequency": app_method.get("frequency", ""),
            "quantity": "2-3 drops",
            "timing": "before sunscreen"
        }
        log.append(f"  ✓ Usage: frequency={usage_data['frequency']}")
        
        # Ingredients block
        ingredients = product_a.get("ingredients", []) or []
        ingredients_data = {
            "items": [i.get("name", i) if isinstance(i, dict) else i for i in ingredients],
            "count": len(ingredients)
        }
        log.append(f"  ✓ Ingredients: {len(ingredients)} items")
        
        # Comparison block
        price_a = product_a.get("price", {}).get("amount", 0) or 0
        price_b = product_b.get("price", {}).get("amount", 0) or 0
        
        ingredients_a = set(i.get("name", i) if isinstance(i, dict) else i for i in (product_a.get("ingredients", []) or []))
        ingredients_b = set(i.get("name", i) if isinstance(i, dict) else i for i in (product_b.get("ingredients", []) or []))
        
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
    except Exception as e:
        log.append(f"  ❌ Error in logic blocks: {str(e)}")
        # Return empty structures so graph continues
        return {
            "benefits_data": {},
            "usage_data": {},
            "ingredients_data": {},
            "comparison_data": {},
            "execution_log": log
        }



from core.validator import ContentValidator

# ==================== GENERATE QUESTIONS NODE ====================

async def generate_questions_node(state: AgentState) -> Dict[str, Any]:
    """
    Generate questions using independent QuestionGeneratorAgent.
    Includes validation and retry logic.
    """
    log = [f"[{datetime.now().isoformat()}] GENERATE_QUESTIONS: Invoking QuestionGeneratorAgent..."]
    
    agent = QuestionGeneratorAgent()
    max_retries = 2
    
    for attempt in range(max_retries):
        try:
            # Run Agent
            result = await agent.run(state["product_a"])
            
            # Validate
            errors = ContentValidator.validate_questions(result)
            if errors:
                log.append(f"  ⚠️ Validation incorrect (Attempt {attempt+1}): {errors}")
                if attempt < max_retries - 1:
                    continue # Retry
            else:
                # Success
                questions = result.get("questions", [])
                
                # Count stats
                categories = {}
                for q in questions:
                    cat = q.get("category", "other")
                    categories[cat] = categories.get(cat, 0) + 1
                
                log.append(f"  ✓ Agent generated {len(questions)} questions via LLM")
                log.append(f"  ✓ Validation passed")
                log.append(f"[{datetime.now().isoformat()}] GENERATE_QUESTIONS: Completed")
                
                return {
                    "questions": questions,
                    "execution_log": log
                }
                
        except Exception as e:
            log.append(f"  ❌ Error (Attempt {attempt+1}): {str(e)}")
            if attempt < max_retries - 1:
                log.append("  🔄 Retrying...")

    # Fallback if all retries fail
    log.append("  ❌ All retries failed. Returning empty list.")
    return {
        "questions": [],
        "execution_log": log
    }


# ==================== GENERATE FAQ NODE ====================

async def generate_faq_node(state: AgentState) -> Dict[str, Any]:
    """
    Generate FAQ using independent FAQGeneratorAgent.
    Includes validation and retry logic.
    """
    log = [f"[{datetime.now().isoformat()}] GENERATE_FAQ: Invoking FAQGeneratorAgent..."]
    
    # Prerequisite check
    if not state.get("questions"):
        log.append("  ⚠️ No questions available to generate answers. Skipping.")
        return {"faq_output": {"faqs": []}, "execution_log": log}

    agent = FAQGeneratorAgent()
    max_retries = 2
    
    for attempt in range(max_retries):
        try:
            result = await agent.run({
                "product": state["product_a"],
                "questions": state["questions"]
            })
            
            errors = ContentValidator.validate_faq(result)
            if errors:
                log.append(f"  ⚠️ Validation incorrect (Attempt {attempt+1}): {errors}")
                if attempt < max_retries - 1: continue
            else:
                faq_count = len(result.get("faqs", []))
                log.append(f"  ✓ Agent generated {faq_count} FAQ answers via LLM")
                log.append(f"[{datetime.now().isoformat()}] GENERATE_FAQ: Completed")
                return {
                    "faq_output": result,
                    "execution_log": log
                }
        except Exception as e:
            log.append(f"  ❌ Error (Attempt {attempt+1}): {str(e)}")
            
    return {"faq_output": {"faqs": []}, "execution_log": log}


# ==================== GENERATE PRODUCT PAGE NODE ====================

async def generate_product_node(state: AgentState) -> Dict[str, Any]:
    """
    Generate product page using independent ProductPageAgent.
    Includes validation and retry logic.
    """
    log = [f"[{datetime.now().isoformat()}] GENERATE_PRODUCT: Invoking ProductPageAgent..."]
    
    agent = ProductPageAgent()
    max_retries = 2
    
    for attempt in range(max_retries):
        try:
            result = await agent.run(state["product_a"])
            
            errors = ContentValidator.validate_product(result)
            if errors:
                log.append(f"  ⚠️ Validation incorrect (Attempt {attempt+1}): {errors}")
                if attempt < max_retries - 1: continue
            else:
                log.append(f"  ✓ Agent generated product page via LLM")
                log.append(f"[{datetime.now().isoformat()}] GENERATE_PRODUCT: Completed")
                return {
                    "product_output": result,
                    "execution_log": log
                }
        except Exception as e:
            log.append(f"  ❌ Error (Attempt {attempt+1}): {str(e)}")

    return {"product_output": None, "execution_log": log}


# ==================== GENERATE COMPARISON NODE ====================

async def generate_comparison_node(state: AgentState) -> Dict[str, Any]:
    """
    Generate comparison using independent ComparisonAgent.
    Includes validation and retry logic.
    """
    log = [f"[{datetime.now().isoformat()}] GENERATE_COMPARISON: Invoking ComparisonAgent..."]
    
    agent = ComparisonAgent()
    max_retries = 2
    
    for attempt in range(max_retries):
        try:
            result = await agent.run({
                "productA": state["product_a"],
                "productB": state["product_b"]
            })
            
            errors = ContentValidator.validate_comparison(result)
            if errors:
                log.append(f"  ⚠️ Validation incorrect (Attempt {attempt+1}): {errors}")
                if attempt < max_retries - 1: continue
            else:
                log.append(f"  ✓ Agent generated comparison via LLM")
                log.append(f"[{datetime.now().isoformat()}] GENERATE_COMPARISON: Completed")
                return {
                    "comparison_output": result,
                    "execution_log": log
                }
        except Exception as e:
            log.append(f"  ❌ Error (Attempt {attempt+1}): {str(e)}")

    return {"comparison_output": None, "execution_log": log}



# ==================== WRITE OUTPUTS NODE ====================

def write_outputs_node(state: AgentState) -> Dict[str, Any]:
    """
    Finalize outputs. 
    NOTE: File writing is disabled for stateless production deployment.
    Outputs are returned in the state object.
    """
    log = [f"[{datetime.now().isoformat()}] FINALIZE_OUTPUTS: Starting..."]
    
    # In a stateless architecture, we do not write to local disk.
    # The results are available in the state dict:
    # - state['faq_output']
    # - state['product_output']
    # - state['comparison_output']
    
    log.append("  ✓ Outputs finalized in memory (Stateless Mode)")
    
    # Optional: If you strictly needed local files for debugging, you could uncomment:
    # output_dir = Path("output")
    # output_dir.mkdir(exist_ok=True)
    # ... writes ...
    
    log.append(f"[{datetime.now().isoformat()}] FINALIZE_OUTPUTS: Completed")
    
    return {
        "outputs_written": True,
        "execution_log": log
    }

