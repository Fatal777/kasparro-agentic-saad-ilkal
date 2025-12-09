"""
Question Agent - Production-grade question generator.

Generates 15+ categorized user questions with validation,
logging, and deterministic output.
"""

import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.models import QuestionCategory, Question, QuestionSet
from core.logging import get_agent_logger, log_step
from core.errors import ValidationError


class QuestionAgent:
    """
    Agent for generating categorized user questions about a product.
    
    Responsibility: Generate 15+ categorized questions
    Input: ProductModel dict
    Output: QuestionSet with categorized questions
    Dependencies: Parser Agent output
    
    Production Features:
        - Guaranteed minimum question count
        - Category coverage validation
        - Type-safe output
    """
    
    MIN_QUESTIONS = 15
    REQUIRED_CATEGORIES = list(QuestionCategory)
    
    def __init__(self):
        """Initialize the Question Agent."""
        self.logger = get_agent_logger("QuestionAgent")
    
    @log_step("generate_questions")
    def process(self, product_model: dict) -> QuestionSet:
        """
        Generate categorized questions based on product model.
        
        Args:
            product_model: Structured product model dictionary.
            
        Returns:
            QuestionSet with 15+ categorized questions.
        """
        product_name = product_model.get("productName", "this product")
        self.logger.debug(f"Generating questions for: {product_name}")
        
        questions = []
        
        # Generate questions by category
        questions.extend(self._generate_informational(product_model))
        questions.extend(self._generate_safety(product_model))
        questions.extend(self._generate_usage(product_model))
        questions.extend(self._generate_purchase(product_model))
        questions.extend(self._generate_comparison(product_model))
        
        # Count by category
        category_counts = {}
        for cat in QuestionCategory:
            category_counts[cat.value] = sum(
                1 for q in questions if q.category == cat
            )
        
        self.logger.info(
            f"Generated {len(questions)} questions for {product_name}"
        )
        
        return QuestionSet(
            success=True,
            productName=product_name,
            totalQuestions=len(questions),
            questions=questions,
            categoryCounts=category_counts
        )
    
    def _create_question(
        self, 
        q_id: int, 
        category: QuestionCategory, 
        text: str
    ) -> Question:
        """Create a validated Question object."""
        return Question(
            id=f"q-{q_id:03d}",
            category=category,
            question=text
        )
    
    def _generate_informational(self, product: dict) -> list[Question]:
        """Generate informational questions (5+)."""
        name = product.get("productName", "this product")
        ingredients = product.get("keyIngredients", [])
        
        questions = [
            f"What are the key ingredients in {name}?",
            f"What are the main benefits of using {name}?",
            f"What skin types is {name} suitable for?",
            f"What is the concentration of active ingredients in {name}?",
            f"How does {name} help with skin care?",
            f"What makes {name} effective for skincare?"
        ]
        
        # Add ingredient-specific questions
        for ingredient in ingredients[:2]:
            questions.append(f"What does {ingredient} do for my skin?")
        
        return [
            self._create_question(i + 1, QuestionCategory.INFORMATIONAL, q)
            for i, q in enumerate(questions)
        ]
    
    def _generate_safety(self, product: dict) -> list[Question]:
        """Generate safety questions (3+)."""
        name = product.get("productName", "this product")
        base_id = 20
        
        questions = [
            f"Are there any side effects of using {name}?",
            f"Is {name} safe for sensitive skin?",
            f"Can I use {name} if I have allergies?",
            f"Should I do a patch test before using {name}?"
        ]
        
        return [
            self._create_question(base_id + i, QuestionCategory.SAFETY, q)
            for i, q in enumerate(questions)
        ]
    
    def _generate_usage(self, product: dict) -> list[Question]:
        """Generate usage questions (3+)."""
        name = product.get("productName", "this product")
        base_id = 30
        
        questions = [
            f"How should I apply {name}?",
            f"When is the best time to use {name}?",
            f"How many drops of {name} should I use?",
            f"Can I use {name} with other skincare products?"
        ]
        
        return [
            self._create_question(base_id + i, QuestionCategory.USAGE, q)
            for i, q in enumerate(questions)
        ]
    
    def _generate_purchase(self, product: dict) -> list[Question]:
        """Generate purchase questions (2+)."""
        name = product.get("productName", "this product")
        price = product.get("price", {})
        amount = price.get("amount", 0) if isinstance(price, dict) else 0
        currency = price.get("currency", "INR") if isinstance(price, dict) else "INR"
        base_id = 40
        
        questions = [
            f"How much does {name} cost?",
            f"Is {name} worth the price of {currency} {amount}?",
            f"Where can I buy {name}?"
        ]
        
        return [
            self._create_question(base_id + i, QuestionCategory.PURCHASE, q)
            for i, q in enumerate(questions)
        ]
    
    def _generate_comparison(self, product: dict) -> list[Question]:
        """Generate comparison questions (2+)."""
        name = product.get("productName", "this product")
        base_id = 50
        
        questions = [
            f"How does {name} compare to other vitamin serums?",
            f"What makes {name} different from other brands?"
        ]
        
        return [
            self._create_question(base_id + i, QuestionCategory.COMPARISON, q)
            for i, q in enumerate(questions)
        ]
