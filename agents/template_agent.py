"""
Template Agent - Production-grade template processor.

Fills templates with structured data, validates output,
and produces final JSON files.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.models import AgentResult
from core.logging import get_agent_logger, log_step
from core.errors import ValidationError, retry_with_backoff


class TemplateAgent:
    """
    Agent for filling templates and producing final JSON output.
    
    Responsibility: Fill templates, validate, produce final JSON
    Input: Template schema + structured data
    Output: Validated JSON file content
    Dependencies: Page agents, Templates
    
    Production Features:
        - Template schema validation
        - Required field checking
        - JSON output with proper encoding
        - Retry logic for file operations
    """
    
    def __init__(self, templates_dir: str = "templates"):
        """
        Initialize the Template Agent.
        
        Args:
            templates_dir: Path to templates directory.
        """
        self.templates_dir = Path(templates_dir)
        self.logger = get_agent_logger("TemplateAgent")
    
    @log_step("process_template")
    def process(self, template_name: str, page_data: Any) -> AgentResult:
        """
        Fill template with page data and validate.
        
        Args:
            template_name: Name of template (faq, product, comparison).
            page_data: Pydantic model or dict with page data.
            
        Returns:
            AgentResult with validated JSON-ready data.
        """
        self.logger.debug(f"Processing template: {template_name}")
        
        try:
            # Load template schema
            template = self._load_template(template_name)
            if not template:
                raise ValidationError(
                    f"Template '{template_name}' not found",
                    field="template_name"
                )
            
            # Convert Pydantic model to dict if necessary
            if hasattr(page_data, "model_dump"):
                data_dict = page_data.model_dump(mode="json")
            else:
                data_dict = dict(page_data)
            
            # Validate required fields
            required_fields = template.get("requiredFields", [])
            missing = self._validate_required_fields(data_dict, required_fields)
            
            if missing:
                raise ValidationError(
                    f"Missing required fields: {missing}",
                    field=",".join(missing)
                )
            
            # Add metadata
            output_data = self._add_metadata(data_dict)
            
            self.logger.info(f"Template '{template_name}' processed successfully")
            
            return AgentResult(
                success=True,
                error=None,
                data=output_data
            )
            
        except ValidationError as e:
            self.logger.error(f"Validation failed: {e}")
            return AgentResult(
                success=False,
                error=str(e),
                data=None
            )
        except Exception as e:
            self.logger.error(f"Template processing failed: {e}")
            return AgentResult(
                success=False,
                error=str(e),
                data=None
            )
    
    def _load_template(self, template_name: str) -> Optional[dict]:
        """Load template JSON schema."""
        template_path = self.templates_dir / f"{template_name}_template.json"
        
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.warning(f"Template not found: {template_path}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid template JSON: {e}")
            return None
    
    def _validate_required_fields(
        self, 
        data: dict, 
        required: list[str]
    ) -> list[str]:
        """Check for missing required fields."""
        missing = []
        
        for field in required:
            if field not in data:
                missing.append(field)
            elif data[field] is None:
                missing.append(field)
            elif isinstance(data[field], list) and len(data[field]) == 0:
                # Allow empty lists to pass (they exist)
                pass
        
        return missing
    
    def _add_metadata(self, data: dict) -> dict:
        """Add generation metadata to output."""
        output = dict(data)
        
        # Add timestamp if not present
        if "generatedAt" not in output or output["generatedAt"] is None:
            output["generatedAt"] = datetime.now(timezone.utc).isoformat()
        
        # Remove internal success flag
        if "success" in output:
            del output["success"]
        
        return output
    
    @retry_with_backoff(max_retries=3, base_delay=0.5)
    def write_output(self, output_path: str | Path, data: dict) -> bool:
        """
        Write validated JSON to file with retry logic.
        
        Args:
            output_path: Path to output file.
            data: Validated data dictionary.
            
        Returns:
            True if successful.
            
        Raises:
            IOError: If write fails after retries.
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Written: {output_file}")
            return True
            
        except (IOError, OSError) as e:
            self.logger.error(f"Failed to write {output_file}: {e}")
            raise
