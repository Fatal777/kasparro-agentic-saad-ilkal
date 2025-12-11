"""
FastAPI Backend - REST API with LangGraph Pipeline

This API exposes the LangGraph-based multi-agent content generation system.
Agents make actual LLM calls to generate content.

Endpoints:
    GET  /api/health - Health check
    POST /api/run-pipeline - Run the LangGraph pipeline
    GET  /api/outputs/faq - Get FAQ output
    GET  /api/outputs/product - Get Product page output
    GET  /api/outputs/comparison - Get Comparison page output
    GET  /api/products - Get input product data
    GET  /api/system-info - Get system architecture info
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Import LangGraph pipeline
from agents.graph import run_pipeline

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent

app = FastAPI(
    title="Multi-Agent Content Generation API (LangGraph)",
    description="REST API for the LangGraph-based agentic content generation system",
    version="2.0.0"
)

# CORS configuration - secure defaults
# Set ALLOWED_ORIGINS env var for production (comma-separated list)
allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
if not allowed_origins or allowed_origins == [""]:
    # Development defaults - specific origins, not wildcard
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)


class PipelineResponse(BaseModel):
    success: bool
    pipeline_id: Optional[str] = None
    message: str
    execution_time_ms: Optional[float] = None


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    framework: str


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="2.0.0",
        framework="LangGraph"
    )


@app.post("/api/run-pipeline", response_model=PipelineResponse)
async def api_run_pipeline():
    """
    Run the full LangGraph multi-agent pipeline.
    
    This makes actual LLM API calls to generate content.
    Requires LLM_PROVIDER and appropriate API key in .env
    """
    try:
        provider = os.getenv("LLM_PROVIDER", "gemini")
        
        # Check for API key based on provider
        if provider == "gemini" and not os.getenv("GOOGLE_API_KEY"):
            raise HTTPException(
                status_code=500,
                detail="GOOGLE_API_KEY not configured. Set it in .env file."
            )
        elif provider == "openai" and not os.getenv("OPENAI_API_KEY"):
            raise HTTPException(
                status_code=500,
                detail="OPENAI_API_KEY not configured. Set it in .env file."
            )
        # Ollama doesn't need an API key
        
        # Run LangGraph pipeline
        result = run_pipeline()
        
        if result["success"]:
            return PipelineResponse(
                success=True,
                pipeline_id=datetime.now().strftime("%Y%m%d_%H%M%S"),
                message="LangGraph pipeline executed successfully with LLM calls",
                execution_time_ms=result.get("execution_time_ms")
            )
        else:
            return PipelineResponse(
                success=False,
                message=result.get("error", "Unknown error"),
                execution_time_ms=result.get("execution_time_ms")
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/outputs/faq")
async def get_faq_output():
    """Get the FAQ page output (LLM-generated)."""
    faq_path = PROJECT_ROOT / "output" / "faq.json"
    
    if not faq_path.exists():
        raise HTTPException(
            status_code=404, 
            detail="FAQ output not found. Run the pipeline first via POST /api/run-pipeline"
        )
    
    with open(faq_path, "r", encoding="utf-8") as f:
        return json.load(f)


@app.get("/api/outputs/product")
async def get_product_output():
    """Get the Product page output (LLM-generated)."""
    product_path = PROJECT_ROOT / "output" / "product_page.json"
    
    if not product_path.exists():
        raise HTTPException(
            status_code=404, 
            detail="Product output not found. Run the pipeline first via POST /api/run-pipeline"
        )
    
    with open(product_path, "r", encoding="utf-8") as f:
        return json.load(f)


@app.get("/api/outputs/comparison")
async def get_comparison_output():
    """Get the Comparison page output (LLM-generated)."""
    comparison_path = PROJECT_ROOT / "output" / "comparison_page.json"
    
    if not comparison_path.exists():
        raise HTTPException(
            status_code=404, 
            detail="Comparison output not found. Run the pipeline first via POST /api/run-pipeline"
        )
    
    with open(comparison_path, "r", encoding="utf-8") as f:
        return json.load(f)


@app.get("/api/products")
async def get_products():
    """Get input product data."""
    try:
        product_a_path = PROJECT_ROOT / "data" / "product_data.json"
        product_b_path = PROJECT_ROOT / "data" / "product_b_data.json"
        
        with open(product_a_path, "r", encoding="utf-8") as f:
            product_a = json.load(f)
        
        with open(product_b_path, "r", encoding="utf-8") as f:
            product_b = json.load(f)
        
        return {
            "productA": product_a,
            "productB": product_b
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/system-info")
async def get_system_info():
    """Get system architecture info."""
    provider = os.getenv("LLM_PROVIDER", "gemini")
    
    return {
        "name": "Multi-Agent Content Generation System",
        "version": "2.0.0",
        "framework": "LangGraph",
        "architecture": "StateGraph DAG with LLM-powered independent agents",
        "llm": {
            "provider": provider.capitalize(),
            "model": os.getenv("MODEL_NAME", "llama3.2" if provider == "ollama" else "gemini-1.5-flash"),
            "configured": True if provider == "ollama" else bool(os.getenv("GOOGLE_API_KEY") or os.getenv("OPENAI_API_KEY"))
        },
        "agents": [
            {"name": "QuestionGeneratorAgent", "type": "independent", "llm": True, "role": "Generate 21 questions via LLM"},
            {"name": "FAQGeneratorAgent", "type": "independent", "llm": True, "role": "Generate FAQ answers via LLM"},
            {"name": "ProductPageAgent", "type": "independent", "llm": True, "role": "Generate product page via LLM"},
            {"name": "ComparisonAgent", "type": "independent", "llm": True, "role": "Generate comparison via LLM"},
        ],
        "nodes": [
            {"name": "parse_products", "role": "Parse raw product data", "llm": False},
            {"name": "run_logic_blocks", "role": "Execute pure-function logic blocks", "llm": False},
            {"name": "generate_questions", "role": "Invoke QuestionGeneratorAgent", "llm": True},
            {"name": "generate_faq", "role": "Invoke FAQGeneratorAgent", "llm": True},
            {"name": "generate_product", "role": "Invoke ProductPageAgent", "llm": True},
            {"name": "generate_comparison", "role": "Invoke ComparisonAgent", "llm": True},
            {"name": "write_outputs", "role": "Write JSON output files", "llm": False}
        ],
        "outputs": ["faq.json", "product_page.json", "comparison_page.json"]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
