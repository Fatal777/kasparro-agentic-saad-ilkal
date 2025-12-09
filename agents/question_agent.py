"""
Question Agent - Generates categorized user questions.

This agent is responsible for generating 15+ categorized questions
based on the product model data.
"""


class QuestionAgent:
    """
    Agent for generating categorized user questions about a product.
    
    Responsibility: Generate 15+ categorized questions
    Input: ProductModel dict
    Output: QuestionSet dict with categorized questions
    Dependencies: Parser Agent output
    """
    
    # Question categories as per assignment
    CATEGORIES = ["informational", "safety", "usage", "purchase", "comparison"]
    
    def __init__(self):
        """Initialize the Question Agent."""
        pass
    
    def process(self, product_model: dict) -> dict:
        """
        Generate categorized questions based on product model.
        
        Args:
            product_model: Structured product model dictionary.
            
        Returns:
            QuestionSet dictionary with 15+ categorized questions.
        """
        product_name = product_model.get("productName", "this product")
        ingredients = product_model.get("keyIngredients", [])
        benefits = product_model.get("benefits", [])
        skin_types = product_model.get("skinType", [])
        concentration = product_model.get("concentration", "")
        price = product_model.get("price", {})
        
        questions = []
        question_id = 1
        
        # Informational Questions (5+)
        informational_questions = [
            f"What are the key ingredients in {product_name}?",
            f"What are the main benefits of using {product_name}?",
            f"What skin types is {product_name} suitable for?",
            f"What is the concentration of active ingredients in {product_name}?",
            f"How does {product_name} help with skin care?",
        ]
        
        for ingredient in ingredients[:2]:
            informational_questions.append(
                f"What does {ingredient} do for my skin?"
            )
        
        for q in informational_questions:
            questions.append(self._create_question(question_id, "informational", q))
            question_id += 1
        
        # Safety Questions (3+)
        safety_questions = [
            f"Are there any side effects of using {product_name}?",
            f"Is {product_name} safe for sensitive skin?",
            f"Can I use {product_name} if I have allergies?",
            f"Should I do a patch test before using {product_name}?",
        ]
        
        for q in safety_questions:
            questions.append(self._create_question(question_id, "safety", q))
            question_id += 1
        
        # Usage Questions (3+)
        usage_questions = [
            f"How should I apply {product_name}?",
            f"When is the best time to use {product_name}?",
            f"How many drops of {product_name} should I use?",
            f"Can I use {product_name} with other skincare products?",
        ]
        
        for q in usage_questions:
            questions.append(self._create_question(question_id, "usage", q))
            question_id += 1
        
        # Purchase Questions (2+)
        price_amount = price.get("amount", 0)
        currency = price.get("currency", "INR")
        
        purchase_questions = [
            f"How much does {product_name} cost?",
            f"Is {product_name} worth the price of {currency} {price_amount}?",
            f"Where can I buy {product_name}?",
        ]
        
        for q in purchase_questions:
            questions.append(self._create_question(question_id, "purchase", q))
            question_id += 1
        
        # Comparison Questions (2+)
        comparison_questions = [
            f"How does {product_name} compare to other vitamin serums?",
            f"What makes {product_name} different from other brands?",
        ]
        
        for q in comparison_questions:
            questions.append(self._create_question(question_id, "comparison", q))
            question_id += 1
        
        return {
            "success": True,
            "productName": product_name,
            "totalQuestions": len(questions),
            "questions": questions,
            "categoryCounts": self._count_by_category(questions)
        }
    
    def _create_question(self, qid: int, category: str, question: str) -> dict:
        """Create a question object."""
        return {
            "id": f"q-{qid:03d}",
            "category": category,
            "question": question
        }
    
    def _count_by_category(self, questions: list) -> dict:
        """Count questions by category."""
        counts = {cat: 0 for cat in self.CATEGORIES}
        for q in questions:
            category = q.get("category", "")
            if category in counts:
                counts[category] += 1
        return counts
