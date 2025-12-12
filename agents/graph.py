"""
LangGraph Pipeline Orchestrator with Rate Limit Protection

This is the main entry point that builds and runs the LangGraph StateGraph.
The graph defines a DAG (Directed Acyclic Graph) of agent nodes.

RATE LIMIT PROTECTION:
- LLM nodes run SEQUENTIALLY (not parallel) to avoid rate limits
- 15 second delay between each LLM call
"""

import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from langgraph.graph import StateGraph, END

from core.graph_state import AgentState
from agents.nodes import (
    parse_products_node,
    run_logic_blocks_node,
    generate_questions_node,
    generate_faq_node,
    generate_product_node,
    generate_comparison_node,
    write_outputs_node
)

# Rate limit delay between LLM calls (seconds)
RATE_LIMIT_DELAY = 15


def with_rate_limit(node_func, delay: int = RATE_LIMIT_DELAY):
    """Wrapper to add delay after LLM node execution."""
    async def wrapped(state: AgentState) -> Dict[str, Any]:
        # Await the async node function
        result = await node_func(state)
        print(f"  ⏳ Waiting {delay}s to avoid rate limits...")
        await asyncio.sleep(delay)
        return result
    return wrapped


def build_pipeline_graph() -> StateGraph:
    """
    Build the LangGraph pipeline with SEQUENTIAL LLM execution.
    """
    
    # Create the graph with our state type
    graph = StateGraph(AgentState)
    
    # Add nodes
    # Non-LLM nodes (sync)
    graph.add_node("parse_products", parse_products_node)
    graph.add_node("run_logic_blocks", run_logic_blocks_node)
    graph.add_node("write_outputs", write_outputs_node)
    
    # LLM nodes with rate limiting (async wrapped)
    graph.add_node("generate_questions", with_rate_limit(generate_questions_node))
    graph.add_node("generate_faq", with_rate_limit(generate_faq_node))
    graph.add_node("generate_product", with_rate_limit(generate_product_node))
    graph.add_node("generate_comparison", with_rate_limit(generate_comparison_node))
    
    # Define edges - SEQUENTIAL execution to avoid rate limits
    graph.set_entry_point("parse_products")
    
    graph.add_edge("parse_products", "run_logic_blocks")
    graph.add_edge("run_logic_blocks", "generate_questions")
    
    # LLM nodes run ONE AT A TIME (sequential, not parallel)
    graph.add_edge("generate_questions", "generate_faq")
    graph.add_edge("generate_faq", "generate_product")
    graph.add_edge("generate_product", "generate_comparison")
    graph.add_edge("generate_comparison", "write_outputs")
    
    # End after writing
    graph.add_edge("write_outputs", END)
    
    return graph.compile()


def load_product_data() -> tuple[Dict[str, Any], Dict[str, Any]]:
    """Load product data from JSON files."""
    data_dir = Path("data")
    
    # Create dummy data if files don't exist (robustness)
    if not data_dir.exists():
        return {}, {}
    
    try:
        with open(data_dir / "product_data.json", "r", encoding="utf-8") as f:
            product_a = json.load(f)
    except FileNotFoundError:
        product_a = {}
        
    try:
        with open(data_dir / "product_b_data.json", "r", encoding="utf-8") as f:
            product_b = json.load(f)
    except FileNotFoundError:
        product_b = {}
    
    return product_a, product_b


async def run_pipeline() -> Dict[str, Any]:
    """
    Run the complete LangGraph pipeline asynchronously.
    
    Returns:
        Final state with all generated outputs
    """
    print("\n" + "=" * 60)
    print("  Multi-Agent Content Generation System (LangGraph)")
    print("  Rate Limit Mode: Sequential with 15s delays")
    print("=" * 60)
    
    # Load input data
    product_a, product_b = load_product_data()
    
    # Initialize state
    initial_state: AgentState = {
        "raw_product_a": product_a,
        "raw_product_b": product_b,
        "product_a": None,
        "product_b": None,
        "benefits_data": None,
        "usage_data": None,
        "ingredients_data": None,
        "comparison_data": None,
        "questions": None,
        "faq_output": None,
        "product_output": None,
        "comparison_output": None,
        "outputs_written": False,
        "errors": [],
        "execution_log": []
    }
    
    # Build and run graph
    graph = build_pipeline_graph()
    
    print("\n[Pipeline] Starting LangGraph execution...")
    print("[Pipeline] 4 LLM calls with 15s delays = ~1 minute total\n")
    start_time = datetime.now()
    
    # Execute the graph asynchronously
    final_state = await graph.ainvoke(initial_state)
    
    end_time = datetime.now()
    duration_ms = (end_time - start_time).total_seconds() * 1000
    
    # Print execution log
    for log_entry in final_state.get("execution_log", []):
        print(log_entry)
    
    print("\n" + "=" * 60)
    print("  Pipeline completed successfully!")
    print(f"  Execution time: {duration_ms/1000:.1f}s")
    print("=" * 60)
    
    print("\n✅ Pipeline completed successfully!")
    print(f"   Pipeline ID: {datetime.now().strftime('%Y%m%d_%H%M%S')}")
    print("\nOutput files:")
    print("  - faq: output/faq.json")
    print("  - product_page: output/product_page.json")
    print("  - comparison_page: output/comparison_page.json")
    
    return {
        "success": True,
        "execution_time_ms": duration_ms,
        "faq_output": final_state.get("faq_output"),
        "product_output": final_state.get("product_output"),
        "comparison_output": final_state.get("comparison_output")
    }


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_pipeline())
