"""
State Persistence - State management for pipeline consistency.

Implements CAP: Consistency - ensures pipeline state is persisted
and can be recovered from failures.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from pydantic import BaseModel, Field


class PipelineState(BaseModel):
    """
    Persistent state for the pipeline.
    
    Tracks:
        - Current step in execution
        - Intermediate results
        - Execution metadata
    """
    
    pipeline_id: str = Field(default="")
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    current_step: str = Field(default="initialized")
    status: str = Field(default="running")
    
    # Intermediate data (stored as JSON-serializable dicts)
    product_a: Optional[dict] = None
    product_b: Optional[dict] = None
    benefits_data: Optional[dict] = None
    usage_data: Optional[dict] = None
    ingredients_data: Optional[dict] = None
    comparison_data: Optional[dict] = None
    questions: Optional[dict] = None
    faq_page: Optional[dict] = None
    product_page: Optional[dict] = None
    comparison_page: Optional[dict] = None
    
    # Execution tracking
    steps_completed: list[str] = Field(default_factory=list)
    errors: list[dict] = Field(default_factory=list)
    
    model_config = {"extra": "allow"}


class StateManager:
    """
    Manages pipeline state persistence and recovery.
    
    Features:
        - Checkpoint creation after each step
        - State recovery from checkpoints
        - State validation
    """
    
    def __init__(self, state_dir: Path = Path("output/.state")):
        self.state_dir = state_dir
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self._state: Optional[PipelineState] = None
    
    @property
    def state(self) -> PipelineState:
        """Get current state or create new."""
        if self._state is None:
            self._state = PipelineState(
                pipeline_id=datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            )
        return self._state
    
    def checkpoint(self, step: str) -> None:
        """
        Save checkpoint after completing a step.
        
        Enables recovery if pipeline fails at a later step.
        """
        self.state.current_step = step
        self.state.steps_completed.append(step)
        
        checkpoint_path = self.state_dir / f"checkpoint_{self.state.pipeline_id}.json"
        
        with open(checkpoint_path, "w", encoding="utf-8") as f:
            json.dump(
                self.state.model_dump(mode="json"),
                f,
                indent=2,
                default=str
            )
    
    def load_checkpoint(self, pipeline_id: str) -> bool:
        """
        Load state from a previous checkpoint.
        
        Returns True if checkpoint was loaded successfully.
        """
        checkpoint_path = self.state_dir / f"checkpoint_{pipeline_id}.json"
        
        if not checkpoint_path.exists():
            return False
        
        try:
            with open(checkpoint_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            self._state = PipelineState(**data)
            return True
        except (json.JSONDecodeError, ValueError):
            return False
    
    def set_data(self, key: str, value: Any) -> None:
        """Set intermediate data."""
        if hasattr(self.state, key):
            setattr(self.state, key, value)
    
    def get_data(self, key: str) -> Optional[Any]:
        """Get intermediate data."""
        return getattr(self.state, key, None)
    
    def record_error(self, step: str, error: str) -> None:
        """Record an error that occurred during execution."""
        self.state.errors.append({
            "step": step,
            "error": error,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def complete(self) -> None:
        """Mark pipeline as completed."""
        self.state.completed_at = datetime.utcnow()
        self.state.status = "completed"
        self.checkpoint("completed")
    
    def fail(self, error: str) -> None:
        """Mark pipeline as failed."""
        self.state.status = "failed"
        self.record_error(self.state.current_step, error)
        self.checkpoint("failed")
    
    def can_resume_from(self, step: str) -> bool:
        """Check if pipeline can resume from a given step."""
        return step in self.state.steps_completed
    
    def get_resume_step(self) -> Optional[str]:
        """Get the step to resume from after a failure."""
        if not self.state.steps_completed:
            return None
        return self.state.steps_completed[-1]
    
    def clear(self) -> None:
        """Clear current state."""
        self._state = None
        
        # Optionally clean up old checkpoints
        for checkpoint in self.state_dir.glob("checkpoint_*.json"):
            # Keep last 5 checkpoints
            pass
