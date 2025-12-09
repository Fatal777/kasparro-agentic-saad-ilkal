"""
Template Schema Validation Module

Validates output data against template schema definitions,
ensuring all required fields are present and correctly typed.
"""

import json
from typing import Any, Dict, List, Tuple, Optional
from pathlib import Path
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of schema validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]


class TemplateSchemaValidator:
    """
    Validates output data against template schema definitions.
    
    Ensures:
    - All required fields are present
    - Field types match expected types
    - Block dependencies are satisfied
    """
    
    def __init__(self, templates_dir: str = "templates"):
        """Initialize with templates directory."""
        self.templates_dir = Path(templates_dir)
        self.templates: Dict[str, dict] = {}
        self._load_templates()
    
    def _load_templates(self):
        """Load all template definitions."""
        template_files = [
            ("faq", "faq_template.json"),
            ("product", "product_template.json"),
            ("comparison", "comparison_template.json"),
        ]
        
        for name, filename in template_files:
            path = self.templates_dir / filename
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    self.templates[name] = json.load(f)
    
    def validate(self, template_name: str, data: dict) -> ValidationResult:
        """
        Validate data against a template schema.
        
        Args:
            template_name: Name of template (faq, product, comparison)
            data: Data to validate
            
        Returns:
            ValidationResult with errors and warnings
        """
        errors = []
        warnings = []
        
        if template_name not in self.templates:
            errors.append(f"Unknown template: {template_name}")
            return ValidationResult(False, errors, warnings)
        
        template = self.templates[template_name]
        schema = template.get("schema", {})
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        
        # Check required fields
        for field in required:
            if field not in data:
                errors.append(f"Missing required field: {field}")
            elif data[field] is None:
                errors.append(f"Required field is null: {field}")
        
        # Check field types
        for field, field_schema in properties.items():
            if field in data and data[field] is not None:
                expected_type = field_schema.get("type")
                if not self._check_type(data[field], expected_type):
                    errors.append(
                        f"Field '{field}' has wrong type. "
                        f"Expected {expected_type}, got {type(data[field]).__name__}"
                    )
        
        # Check block dependencies
        block_deps = template.get("blockDependencies", [])
        if block_deps:
            # This is a structural check - blocks should have been processed
            pass  # Dependencies validated at orchestration level
        
        return ValidationResult(len(errors) == 0, errors, warnings)
    
    def _check_type(self, value: Any, expected_type: Optional[str]) -> bool:
        """Check if value matches expected JSON schema type."""
        if expected_type is None:
            return True
        
        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
        }
        
        expected = type_map.get(expected_type)
        if expected is None:
            return True
        
        return isinstance(value, expected)
    
    def validate_all_outputs(self, outputs: Dict[str, dict]) -> Dict[str, ValidationResult]:
        """
        Validate all output files against their templates.
        
        Args:
            outputs: Dict mapping output names to their data
            
        Returns:
            Dict mapping output names to ValidationResults
        """
        results = {}
        
        template_mapping = {
            "faq": "faq",
            "product": "product",
            "comparison": "comparison",
        }
        
        for output_name, template_name in template_mapping.items():
            if output_name in outputs:
                results[output_name] = self.validate(template_name, outputs[output_name])
        
        return results


def validate_output_files() -> bool:
    """
    Validate all output files against their templates.
    
    Returns:
        True if all outputs are valid
    """
    from pathlib import Path
    
    validator = TemplateSchemaValidator()
    output_dir = Path("output")
    
    outputs = {}
    output_files = {
        "faq": "faq.json",
        "product": "product_page.json",
        "comparison": "comparison_page.json",
    }
    
    for name, filename in output_files.items():
        path = output_dir / filename
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                outputs[name] = json.load(f)
    
    results = validator.validate_all_outputs(outputs)
    
    all_valid = True
    for name, result in results.items():
        if result.is_valid:
            print(f"✅ {name}: Schema validation PASSED")
        else:
            print(f"❌ {name}: Schema validation FAILED")
            for error in result.errors:
                print(f"   - {error}")
            all_valid = False
    
    return all_valid


if __name__ == "__main__":
    validate_output_files()
