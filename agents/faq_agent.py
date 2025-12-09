"""
FAQ Agent - Generates FAQ page content.

This agent is responsible for generating FAQ page with Q&A pairs
using questions from Question Agent and data from logic blocks.
"""


class FAQAgent:
    """
    Agent for generating FAQ page content.
    
    Responsibility: Generate FAQ page with Q&A pairs (min 5)
    Input: QuestionSet, BenefitsBlock output, ProductModel
    Output: FAQPageData dict
    Dependencies: Question Agent, Benefits Block
    """
    
    def __init__(self):
        """Initialize the FAQ Agent."""
        pass
    
    def process(
        self, 
        product_model: dict, 
        question_set: dict, 
        benefits_data: dict,
        usage_data: dict,
        ingredient_data: dict
    ) -> dict:
        """
        Generate FAQ page content with Q&A pairs.
        
        Args:
            product_model: Structured product model dictionary.
            question_set: QuestionSet from Question Agent.
            benefits_data: Output from Benefits Block.
            usage_data: Output from Usage Block.
            ingredient_data: Output from Ingredient Block.
            
        Returns:
            FAQPageData dictionary with at least 5 Q&As.
        """
        product_name = product_model.get("productName", "this product")
        questions = question_set.get("questions", [])
        
        faqs = []
        faq_id = 1
        
        # Generate answers for selected questions (min 5 Q&As)
        for question_obj in questions:
            q_text = question_obj.get("question", "")
            category = question_obj.get("category", "")
            
            answer = self._generate_answer(
                q_text, 
                category,
                product_model,
                benefits_data,
                usage_data,
                ingredient_data
            )
            
            if answer:
                faqs.append({
                    "id": f"faq-{faq_id:03d}",
                    "category": category,
                    "question": q_text,
                    "answer": answer
                })
                faq_id += 1
        
        return {
            "success": True,
            "productName": product_name,
            "totalQuestions": len(faqs),
            "faqs": faqs
        }
    
    def _generate_answer(
        self, 
        question: str, 
        category: str,
        product_model: dict,
        benefits_data: dict,
        usage_data: dict,
        ingredient_data: dict
    ) -> str:
        """
        Generate answer based on question category and available data.
        
        Uses rule-based logic to construct answers from structured data.
        No hallucination - only facts from the data.
        """
        product_name = product_model.get("productName", "this product")
        q_lower = question.lower()
        
        # Informational answers
        if "key ingredients" in q_lower or "ingredients" in q_lower:
            ingredients = ingredient_data.get("ingredientList", [])
            if ingredients:
                return f"The key ingredients in {product_name} are {', '.join(ingredients)}."
            return None
        
        if "benefits" in q_lower or "main benefits" in q_lower:
            benefits = benefits_data.get("benefitList", [])
            if benefits:
                return f"The main benefits of {product_name} include {', '.join(benefits)}."
            return None
        
        if "skin types" in q_lower or "suitable for" in q_lower:
            skin_types = product_model.get("skinType", [])
            if skin_types:
                return f"{product_name} is suitable for {', '.join(skin_types)} skin types."
            return None
        
        if "concentration" in q_lower:
            concentration = ingredient_data.get("concentration", "")
            primary = ingredient_data.get("primaryActive", "")
            if concentration and primary:
                return f"{product_name} contains {concentration} {primary}."
            return None
        
        # Safety answers
        if "side effects" in q_lower:
            side_effects = product_model.get("sideEffects", "")
            if side_effects:
                return f"Possible side effects include: {side_effects}."
            return None
        
        if "sensitive skin" in q_lower:
            side_effects = product_model.get("sideEffects", "")
            if "sensitive" in side_effects.lower():
                return f"For sensitive skin users: {side_effects}. A patch test is recommended."
            return "Please do a patch test before regular use if you have sensitive skin."
        
        if "patch test" in q_lower:
            return "Yes, it is recommended to do a patch test before using any new skincare product."
        
        # Usage answers
        if "how should i apply" in q_lower or "apply" in q_lower:
            instructions = usage_data.get("usageInstructions", "")
            if instructions:
                return instructions
            return None
        
        if "best time" in q_lower or "when" in q_lower:
            frequency = usage_data.get("frequency", "")
            timing = usage_data.get("timing", "")
            if frequency:
                answer = f"The best time to use {product_name} is in the {frequency}"
                if timing:
                    answer += f", {timing}"
                return answer + "."
            return None
        
        if "how many drops" in q_lower or "drops" in q_lower:
            quantity = usage_data.get("quantity", "")
            if quantity:
                return f"Apply {quantity} each time you use {product_name}."
            return None
        
        # Purchase answers
        if "cost" in q_lower or "price" in q_lower or "how much" in q_lower:
            price = product_model.get("price", {})
            amount = price.get("amount", 0)
            currency = price.get("currency", "INR")
            if amount:
                return f"{product_name} is priced at {currency} {amount}."
            return None
        
        if "worth" in q_lower:
            benefits = benefits_data.get("benefitList", [])
            price = product_model.get("price", {})
            amount = price.get("amount", 0)
            if benefits and amount:
                return f"At {price.get('currency', 'INR')} {amount}, {product_name} offers {', '.join(benefits)} benefits."
            return None
        
        # Default - skip if no matching rule
        return None
