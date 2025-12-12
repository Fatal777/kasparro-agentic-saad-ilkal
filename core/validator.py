from typing import Dict, Any, List, Optional
import logging

class ContentValidator:
    """
    Validates the structure and content of agent outputs.
    """
    
    @staticmethod
    def validate_questions(data: Dict[str, Any]) -> List[str]:
        """Validate questions output."""
        errors = []
        if not isinstance(data, dict):
            return ["Output is not a dictionary"]
        
        questions = data.get("questions", [])
        if not isinstance(questions, list):
            errors.append("Field 'questions' is not a list")
            return errors
            
        if len(questions) < 3:
            errors.append(f"Too few questions generated: {len(questions)} (expected 3+)")
            
        for i, q in enumerate(questions):
            if not q.get("question"):
                errors.append(f"Question {i} missing 'question' text")
            if not q.get("category"):
                errors.append(f"Question {i} missing 'category'")
                
        return errors

    @staticmethod
    def validate_faq(data: Dict[str, Any]) -> List[str]:
        """Validate FAQ output."""
        errors = []
        if not isinstance(data, dict):
            return ["Output is not a dictionary"]
            
        faqs = data.get("faqs", [])
        if not isinstance(faqs, list):
            errors.append("Field 'faqs' is not a list")
            return errors
            
        if len(faqs) < 1:
            errors.append("No FAQ entries generated")
            
        for i, f in enumerate(faqs):
            if not f.get("question"):
                errors.append(f"FAQ {i} missing 'question'")
            if not f.get("answer"):
                errors.append(f"FAQ {i} missing 'answer'")
                
        return errors

    @staticmethod
    def validate_product(data: Dict[str, Any]) -> List[str]:
        """Validate Product Page output."""
        errors = []
        if not isinstance(data, dict):
            return ["Output is not a dictionary"]
            
        required_fields = ["productName", "benefits", "price"]
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
                
        return errors

    @staticmethod
    def validate_comparison(data: Dict[str, Any]) -> List[str]:
        """Validate Comparison output."""
        errors = []
        if not isinstance(data, dict):
            return ["Output is not a dictionary"]
            
        required = ["productA", "productB", "comparison"]
        for field in required:
            if field not in data:
                errors.append(f"Missing required field: {field}")
                
        return errors
