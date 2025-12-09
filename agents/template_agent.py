"""
Template Agent - Fills templates with structured data and validates output.

This agent is responsible for loading templates, filling placeholders
with logic block output, and validating required fields.
"""

import json
from pathlib import Path
from datetime import datetime, timezone


class TemplateAgent:
    """
    Agent for filling templates and producing final JSON output.
    
    Responsibility: Fill templates, validate, produce final JSON
    Input: Template schema + structured data
    Output: Validated JSON file content
    Dependencies: Page agents, Templates
    """
    
    def __init__(self, templates_dir: str = "templates"):
        """
        Initialize the Template Agent.
        
        Args:
            templates_dir: Path to templates directory.
        """
        self.templates_dir = Path(templates_dir)
    
    def process(self, template_name: str, page_data: dict) -> dict:
        """
        Fill template with page data and validate.
        
        Args:
            template_name: Name of template (e.g., "faq", "product", "comparison").
            page_data: Structured page data from page agent.
            
        Returns:
            Validated JSON-ready dictionary or error.
        """
        # Load template schema
        template = self._load_template(template_name)
        if not template:
            return {
                "success": False,
                "error": f"Template '{template_name}' not found",
                "data": None
            }
        
        # Validate required fields
        required_fields = template.get("requiredFields", [])
        missing_fields = self._validate_required_fields(page_data, required_fields)
        
        if missing_fields:
            return {
                "success": False,
                "error": f"Missing required fields: {missing_fields}",
                "data": None
            }
        
        # Add metadata
        output_data = self._add_metadata(page_data)
        
        return {
            "success": True,
            "error": None,
            "data": output_data
        }
    
    def _load_template(self, template_name: str) -> dict:
        """Load template JSON file."""
        template_path = self.templates_dir / f"{template_name}_template.json"
        
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
    
    def _validate_required_fields(self, data: dict, required: list) -> list:
        """Check for missing required fields."""
        missing = []
        for field in required:
            if field not in data or data[field] is None:
                missing.append(field)
            elif isinstance(data[field], list) and len(data[field]) == 0:
                # Empty lists for required fields
                missing.append(field)
        return missing
    
    def _add_metadata(self, data: dict) -> dict:
        """Add generation metadata to output."""
        output = dict(data)
        output["generatedAt"] = datetime.now(timezone.utc).isoformat()
        
        # Remove internal success flag if present
        if "success" in output:
            del output["success"]
        
        return output
    
    def write_output(self, output_path: str, data: dict) -> bool:
        """
        Write validated JSON to file.
        
        Args:
            output_path: Path to output file.
            data: Validated data dictionary.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except (IOError, OSError) as e:
            print(f"Error writing output: {e}")
            return False
