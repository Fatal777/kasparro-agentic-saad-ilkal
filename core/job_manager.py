from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional
import uuid

class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class JobManager:
    """
    Singleton in-memory job manager.
    In production, replace this dict with Redis/DB.
    Includes auto-cleanup to prevent memory leaks.
    """
    _instance = None
    _jobs: Dict[str, Dict[str, Any]] = {}
    MAX_JOBS = 100  # Keep only last 100 jobs

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(JobManager, cls).__new__(cls)
        return cls._instance

    def create_job(self) -> str:
        """Create a new job and return its ID."""
        job_id = str(uuid.uuid4())
        
        # Cleanup if limit reached
        if len(self._jobs) >= self.MAX_JOBS:
            # Remove oldest job (Python 3.7+ dicts are insertion-ordered)
            oldest_key = next(iter(self._jobs))
            del self._jobs[oldest_key]
            
        self._jobs[job_id] = {
            "id": job_id,
            "status": JobStatus.PENDING,
            "created_at": datetime.now().isoformat(),
            "result": None,
            "error": None
        }
        return job_id

    def update_job(self, job_id: str, status: JobStatus, result: Optional[Dict] = None, error: Optional[str] = None):
        """Update job status and result."""
        if job_id in self._jobs:
            self._jobs[job_id]["status"] = status
            if result:
                self._jobs[job_id]["result"] = result
            if error:
                self._jobs[job_id]["error"] = error
            self._jobs[job_id]["updated_at"] = datetime.now().isoformat()

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job detail."""
        return self._jobs.get(job_id)

    def list_jobs(self) -> Dict[str, Dict[str, Any]]:
        """List all jobs (debug only)."""
        return self._jobs

# Global instance
job_manager = JobManager()
