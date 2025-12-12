from pathlib import Path
from typing import Dict, Optional

class PromptLoader:
    """
    Utility to load system prompts from external files.
    """
    _prompts: Dict[str, str] = {}
    _prompts_dir = Path(__file__).parent.parent / "prompts"

    @classmethod
    def load(cls, prompt_name: str) -> str:
        """
        Load a prompt by name (e.g., 'question_generator').
        Caches the result in memory.
        """
        if prompt_name in cls._prompts:
            return cls._prompts[prompt_name]
        
        file_path = cls._prompts_dir / f"{prompt_name}.txt"
        
        if not file_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {file_path}")
            
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            
        cls._prompts[prompt_name] = content
        return content

    @classmethod
    def get_question_prompt(cls) -> str:
        return cls.load("question_generator")
        
    @classmethod
    def get_faq_prompt(cls) -> str:
        return cls.load("faq_generator")
        
    @classmethod
    def get_product_prompt(cls) -> str:
        return cls.load("product_page")
        
    @classmethod
    def get_comparison_prompt(cls) -> str:
        return cls.load("comparison_page")

# Global instance not strictly needed as methods are classmethods, 
# but consistent with other managers.
prompt_loader = PromptLoader()
