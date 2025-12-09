"""
FastAPI Backend - REST API to expose the multi-agent pipeline.

Endpoints:
    GET  /api/health - Health check
    POST /api/run-pipeline - Run the full pipeline
    GET  /api/outputs/faq - Get FAQ output
    GET  /api/outputs/product - Get Product page output
    GET  /api/outputs/comparison - Get Comparison page output
    GET  /api/products - Get input product data
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add project root
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import pipeline components
from agents.orchestrator import Orchestrator

app = FastAPI(
    title="Multi-Agent Content Generation API",
    description="REST API for the agentic content generation system",
    version="1.0.0"
)

# CORS for Vercel frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your Vercel domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


# Store last run results
_last_run: Optional[dict] = None


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0"
    )


@app.post("/api/run-pipeline", response_model=PipelineResponse)
async def run_pipeline():
    """Run the full multi-agent pipeline."""
    global _last_run
    
    try:
        start_time = datetime.utcnow()
        
        orchestrator = Orchestrator(
            data_dir=str(PROJECT_ROOT / "data"),
            templates_dir=str(PROJECT_ROOT / "templates"),
            output_dir=str(PROJECT_ROOT / "output")
        )
        
        result = orchestrator.run()
        
        end_time = datetime.utcnow()
        execution_time = (end_time - start_time).total_seconds() * 1000
        
        _last_run = result
        
        if result["success"]:
            return PipelineResponse(
                success=True,
                pipeline_id=result.get("pipeline_id"),
                message="Pipeline executed successfully",
                execution_time_ms=execution_time
            )
        else:
            return PipelineResponse(
                success=False,
                message=result.get("error", "Unknown error"),
                execution_time_ms=execution_time
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/outputs/faq")
async def get_faq_output():
    """Get the FAQ page output."""
    faq_path = PROJECT_ROOT / "output" / "faq.json"
    
    if not faq_path.exists():
        raise HTTPException(status_code=404, detail="FAQ output not found. Run the pipeline first.")
    
    with open(faq_path, "r", encoding="utf-8") as f:
        return json.load(f)


@app.get("/api/outputs/product")
async def get_product_output():
    """Get the Product page output."""
    product_path = PROJECT_ROOT / "output" / "product_page.json"
    
    if not product_path.exists():
        raise HTTPException(status_code=404, detail="Product output not found. Run the pipeline first.")
    
    with open(product_path, "r", encoding="utf-8") as f:
        return json.load(f)


@app.get("/api/outputs/comparison")
async def get_comparison_output():
    """Get the Comparison page output."""
    comparison_path = PROJECT_ROOT / "output" / "comparison_page.json"
    
    if not comparison_path.exists():
        raise HTTPException(status_code=404, detail="Comparison output not found. Run the pipeline first.")
    
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
    return {
        "name": "Multi-Agent Content Generation System",
        "architecture": "DAG-based orchestration",
        "agents": [
            {"name": "Parser Agent", "role": "Converts raw data to ProductModel"},
            {"name": "Question Agent", "role": "Generates 15+ categorized questions"},
            {"name": "FAQ Agent", "role": "Creates FAQ Q&A pairs"},
            {"name": "Product Page Agent", "role": "Generates product description"},
            {"name": "Comparison Agent", "role": "Compares Product A vs B"},
            {"name": "Template Agent", "role": "Validates and writes JSON output"}
        ],
        "logicBlocks": [
            {"name": "benefits_block", "role": "Extract & structure benefits"},
            {"name": "usage_block", "role": "Parse usage instructions"},
            {"name": "ingredient_block", "role": "Extract ingredient info"},
            {"name": "comparison_block", "role": "Compare two products"}
        ],
        "outputs": ["faq.json", "product_page.json", "comparison_page.json"]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
