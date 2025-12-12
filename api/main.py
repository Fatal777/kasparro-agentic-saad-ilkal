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
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents.graph import run_pipeline
from core.job_manager import job_manager, JobStatus

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent

app = FastAPI(
    title="Multi-Agent Content Generation API (LangGraph)",
    description="REST API for the LangGraph-based agentic content generation system",
    version="2.1.0"
)

# ... CORS setup ...
allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
if not allowed_origins or allowed_origins == [""]:
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
    job_id: str
    message: str
    status: str


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    framework: str


async def run_pipeline_task(job_id: str):
    """Background task wrapper for async pipeline."""
    try:
        job_manager.update_job(job_id, JobStatus.PROCESSING)
        
        # Async execution on event loop
        result = await run_pipeline()
        
        if result["success"]:
            job_manager.update_job(job_id, JobStatus.COMPLETED, result=result)
        else:
            job_manager.update_job(job_id, JobStatus.FAILED, error=result.get("error"))
            
    except Exception as e:
        job_manager.update_job(job_id, JobStatus.FAILED, error=str(e))


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="2.1.0",
        framework="LangGraph Async"
    )


@app.post("/api/run-pipeline", status_code=202)
async def api_run_pipeline(background_tasks: BackgroundTasks):
    """
    Start the pipeline asynchronously.
    Returns immediately with a job_id.
    """
    try:
        provider = os.getenv("LLM_PROVIDER", "gemini")
        
        # Check for API key based on provider
        if provider == "gemini" and not os.getenv("GOOGLE_API_KEY"):
            raise HTTPException(status_code=500, detail="GOOGLE_API_KEY not configured.")
        elif provider == "openai" and not os.getenv("OPENAI_API_KEY"):
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured.")
        
        # Create job
        job_id = job_manager.create_job()
        
        # Dispatch background task
        background_tasks.add_task(run_pipeline_task, job_id)
        
        return {
            "success": True,
            "job_id": job_id,
            "status": "processing",
            "message": "Pipeline started in background"
        }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get status of a background job."""
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.get("/api/products")
async def get_products():
    """Get the input product data."""
    try:
        # For this demo, we can just return the raw data files or a sample
        # In a real app, this would come from the database
        products_dir = PROJECT_ROOT.parent / "data"  # Assuming data is in root
        # ... logic ...
        # But actually, the agents/nodes.py loads from a file too?
        # Let's check state.py. Ah, the graph loads it.
        # For this endpoint, we will just return the hardcoded inputs we use in the graph
        # OR better, if we removed file I/O, we should just return what the job result has.
        return {"message": "Use /api/jobs/{id} to see inputs used in a specific run"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/system-info")
async def system_info():
    """Get system architecture info."""
    return {
        "architecture": "LangGraph Multi-Agent System",
        "llm_provider": os.getenv("LLM_PROVIDER", "gemini"),
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
