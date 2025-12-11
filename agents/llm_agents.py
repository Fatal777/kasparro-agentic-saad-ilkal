"""
Independent LangChain Agents with Multi-Provider LLM Support

Each agent is a self-contained class that:
1. Has its own LLM instance
2. Defines its own prompt template
3. Can run independently without orchestrator
4. Makes real LLM API calls (Gemini, Ollama, or OpenAI)

Supports:
- Google Gemini (cloud, requires API key)
- Ollama (FREE local, no API key needed)
- OpenAI GPT (cloud, requires API key)
"""

import os
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from core.llm_factory import get_llm, get_provider_info

# Load environment
load_dotenv()


class BaseAgent(ABC):
    """
    Abstract base class for all agents.
    
    Each agent is independent and can:
    - Initialize its own LLM (supports Gemini, Ollama, OpenAI)
    - Define its own system prompt
    - Execute without knowing about other agents
    """
    
    def __init__(self, name: str):
        self.name = name
        self.llm = get_llm()  # Uses LLM factory for multi-provider support
        self.provider_info = get_provider_info()
        self.created_at = datetime.now()
    
    def _invoke_with_retry(self, chain, input_data: Dict, max_retries: int = 3):
        """Invoke chain with retry logic for rate limiting."""
        for attempt in range(max_retries):
            try:
                return chain.invoke(input_data)
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    wait_time = (attempt + 1) * 15  # 15, 30, 45 seconds
                    self.log(f"Rate limited, waiting {wait_time}s (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    raise
        raise Exception(f"Failed after {max_retries} retries")
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the agent's system prompt."""
        pass
    
    @abstractmethod
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's task."""
        pass
    
    def log(self, message: str):
        """Log agent activity."""
        print(f"[{self.name}] {message}")


class QuestionGeneratorAgent(BaseAgent):
    """
    Independent agent that generates categorized questions about a product.
    
    Uses Gemini to intelligently create 21+ user questions across categories:
    - informational, safety, usage, purchase, comparison
    """
    
    def __init__(self):
        super().__init__("QuestionGeneratorAgent")
    
    def get_system_prompt(self) -> str:
        return """You are a product content expert specializing in skincare.
Your job is to generate exactly 21 user questions about a product.

IMPORTANT: You must generate questions that users would actually ask.
Think like a customer who is considering buying this product.

Categories and requirements:
- informational (8 questions): About ingredients, what it does, how it works
- safety (4 questions): Side effects, allergies, skin reactions
- usage (4 questions): How to apply, when, frequency, amount
- purchase (3 questions): Price, value, where to buy
- comparison (2 questions): How it compares to alternatives

Return ONLY valid JSON, no markdown or extra text."""
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate 21 categorized questions using LLM."""
        provider = self.provider_info.get("provider", "LLM")
        self.log(f"Starting question generation via {provider} API...")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.get_system_prompt()),
            ("human", """Generate 21 questions for this product:

Product Name: {product_name}
Concentration: {concentration}
Key Ingredients: {ingredients}
Benefits: {benefits}
Skin Types: {skin_types}
How to Use: {usage}
Side Effects: {side_effects}
Price: ₹{price}

Return JSON: {{"questions": [{{"category": "...", "question": "..."}}]}}""")
        ])
        
        chain = prompt | self.llm | JsonOutputParser()
        
        result = chain.invoke({
            "product_name": input_data.get("productName", ""),
            "concentration": input_data.get("concentration", ""),
            "ingredients": ", ".join(
                i.get("name", i) if isinstance(i, dict) else i 
                for i in input_data.get("ingredients", [])
            ),
            "benefits": ", ".join(input_data.get("benefits", [])),
            "skin_types": ", ".join(input_data.get("skinTypes", [])),
            "usage": " ".join(input_data.get("applicationMethod", {}).get("steps", [])),
            "side_effects": input_data.get("sideEffects", ""),
            "price": input_data.get("price", {}).get("amount", 0)
        })
        
        questions = result.get("questions", [])
        self.log(f"Generated {len(questions)} questions via {provider}")
        
        return {"questions": questions, "count": len(questions)}


class FAQGeneratorAgent(BaseAgent):
    """
    Independent agent that generates FAQ answers.
    
    Takes questions and product data, uses Gemini to create
    helpful, accurate answers based ONLY on provided data.
    """
    
    def __init__(self):
        super().__init__("FAQGeneratorAgent")
    
    def get_system_prompt(self) -> str:
        return """You are a skincare product expert.
Your job is to answer FAQ questions accurately and helpfully.

RULES:
1. Only use information provided - never make up facts
2. Keep answers concise (1-2 sentences)
3. Be helpful and customer-friendly
4. Include specific details like ingredients, prices when relevant

Return ONLY valid JSON, no markdown or extra text."""
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate FAQ answers using LLM."""
        provider = self.provider_info.get("provider", "LLM")
        self.log(f"Starting FAQ generation via {provider} API...")
        
        product = input_data.get("product", {})
        questions = input_data.get("questions", [])
        
        import json
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.get_system_prompt()),
            ("human", """Create FAQ answers for these questions:

Product Information:
- Name: {product_name}
- Concentration: {concentration}
- Key Ingredients: {ingredients}
- Benefits: {benefits}
- Skin Types: {skin_types}
- Usage: {usage}
- Side Effects: {side_effects}
- Price: ₹{price}

Questions to answer:
{questions_json}

Return JSON: {{
  "productName": "{product_name}",
  "generatedAt": "{timestamp}",
  "totalQuestions": <count>,
  "faqs": [{{"id": "faq-001", "category": "...", "question": "...", "answer": "..."}}]
}}""")
        ])
        
        chain = prompt | self.llm | JsonOutputParser()
        
        result = chain.invoke({
            "product_name": product.get("productName", ""),
            "concentration": product.get("concentration", ""),
            "ingredients": ", ".join(
                i.get("name", i) if isinstance(i, dict) else i 
                for i in product.get("ingredients", [])
            ),
            "benefits": ", ".join(product.get("benefits", [])),
            "skin_types": ", ".join(product.get("skinTypes", [])),
            "usage": " ".join(product.get("applicationMethod", {}).get("steps", [])),
            "side_effects": product.get("sideEffects", ""),
            "price": product.get("price", {}).get("amount", 0),
            "questions_json": json.dumps(questions, indent=2),
            "timestamp": datetime.now().isoformat()
        })
        
        faq_count = len(result.get("faqs", []))
        self.log(f"Generated {faq_count} FAQ answers via {provider}")
        
        return result


class ProductPageAgent(BaseAgent):
    """
    Independent agent that generates product page content.
    
    Creates rich, engaging product descriptions using Gemini.
    """
    
    def __init__(self):
        super().__init__("ProductPageAgent")
    
    def get_system_prompt(self) -> str:
        return """You are a professional product content writer for skincare.
Your job is to create engaging, informative product page content.

RULES:
1. Use only the provided product information
2. Make content engaging but accurate
3. Highlight key benefits and usage
4. Structure content for easy reading

Return ONLY valid JSON, no markdown or extra text."""
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate product page content using LLM."""
        provider = self.provider_info.get("provider", "LLM")
        self.log(f"Starting product page generation via {provider} API...")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.get_system_prompt()),
            ("human", """Create a product page for:

Product Name: {product_name}
Concentration: {concentration}
Key Ingredients: {ingredients}
Benefits: {benefits}
Skin Types: {skin_types}
How to Use: {usage}
Side Effects: {side_effects}
Price: ₹{price}

Return JSON: {{
  "productName": "...",
  "concentration": "...",
  "skinTypes": [...],
  "keyIngredients": [...],
  "benefits": {{"items": [...], "primary": "...", "count": N, "description": "..."}},
  "usage": {{"instructions": "...", "frequency": "...", "quantity": "...", "timing": "...", "tips": "..."}},
  "sideEffects": "...",
  "price": {{"amount": N, "currency": "INR"}}
}}""")
        ])
        
        chain = prompt | self.llm | JsonOutputParser()
        
        result = chain.invoke({
            "product_name": input_data.get("productName", ""),
            "concentration": input_data.get("concentration", ""),
            "ingredients": ", ".join(
                i.get("name", i) if isinstance(i, dict) else i 
                for i in input_data.get("ingredients", [])
            ),
            "benefits": ", ".join(input_data.get("benefits", [])),
            "skin_types": ", ".join(input_data.get("skinTypes", [])),
            "usage": " ".join(input_data.get("applicationMethod", {}).get("steps", [])),
            "side_effects": input_data.get("sideEffects", ""),
            "price": input_data.get("price", {}).get("amount", 0)
        })
        
        self.log(f"Generated product page for {result.get('productName', 'Unknown')}")
        
        return result


class ComparisonAgent(BaseAgent):
    """
    Independent agent that compares two products.
    
    Analyzes differences and creates intelligent recommendations.
    """
    
    def __init__(self):
        super().__init__("ComparisonAgent")
    
    def get_system_prompt(self) -> str:
        return """You are a skincare product comparison expert.
Your job is to objectively compare two products and provide recommendations.

RULES:
1. Be objective and fair to both products
2. Highlight genuine differences
3. Give actionable recommendations
4. Consider different user needs

Return ONLY valid JSON, no markdown or extra text."""
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate product comparison using LLM."""
        provider = self.provider_info.get("provider", "LLM")
        self.log(f"Starting product comparison via {provider} API...")
        
        product_a = input_data.get("productA", {})
        product_b = input_data.get("productB", {})
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.get_system_prompt()),
            ("human", """Compare these two skincare products:

PRODUCT A:
- Name: {product_a_name}
- Price: ₹{product_a_price}
- Benefits: {product_a_benefits}
- Ingredients: {product_a_ingredients}

PRODUCT B:
- Name: {product_b_name}
- Price: ₹{product_b_price}
- Benefits: {product_b_benefits}
- Ingredients: {product_b_ingredients}

Return JSON: {{
  "productA": {{"name": "...", "price": N, "benefits": [...], "ingredients": [...]}},
  "productB": {{"name": "...", "price": N, "benefits": [...], "ingredients": [...]}},
  "comparison": {{
    "commonIngredients": [...],
    "uniqueToA": [...],
    "uniqueToB": [...],
    "priceDifference": N,
    "cheaperProduct": "productA" or "productB",
    "recommendation": "2-3 sentence recommendation explaining which product suits which needs"
  }}
}}""")
        ])
        
        chain = prompt | self.llm | JsonOutputParser()
        
        result = chain.invoke({
            "product_a_name": product_a.get("productName", ""),
            "product_a_price": product_a.get("price", {}).get("amount", 0),
            "product_a_benefits": ", ".join(product_a.get("benefits", [])),
            "product_a_ingredients": ", ".join(
                i.get("name", i) if isinstance(i, dict) else i 
                for i in product_a.get("ingredients", [])
            ),
            "product_b_name": product_b.get("productName", ""),
            "product_b_price": product_b.get("price", {}).get("amount", 0),
            "product_b_benefits": ", ".join(product_b.get("benefits", [])),
            "product_b_ingredients": ", ".join(
                i.get("name", i) if isinstance(i, dict) else i 
                for i in product_b.get("ingredients", [])
            )
        })
        
        self.log(f"Generated comparison: {product_a.get('productName')} vs {product_b.get('productName')}")
        
        return result


# Export all agents
__all__ = [
    "BaseAgent",
    "QuestionGeneratorAgent", 
    "FAQGeneratorAgent",
    "ProductPageAgent",
    "ComparisonAgent"
]


if __name__ == "__main__":
    # Test individual agent independence
    import json
    
    print("Testing Agent Independence...")
    print("=" * 50)
    
    # Test data
    test_product = {
        "productName": "GlowBoost Vitamin C Serum",
        "concentration": "10% Vitamin C",
        "ingredients": [{"name": "Vitamin C"}, {"name": "Hyaluronic Acid"}],
        "benefits": ["Brightening", "Fades dark spots"],
        "skinTypes": ["Oily", "Combination"],
        "applicationMethod": {"steps": ["Apply 2-3 drops in the morning"], "frequency": "morning"},
        "sideEffects": "Mild tingling for sensitive skin",
        "price": {"amount": 699, "currency": "INR"}
    }
    
    # Test QuestionGeneratorAgent independently
    print("\n1. Testing QuestionGeneratorAgent...")
    q_agent = QuestionGeneratorAgent()
    questions = q_agent.run(test_product)
    print(f"   Result: {questions['count']} questions generated")
    
    print("\n✅ Agents can run independently with their own LLM!")
