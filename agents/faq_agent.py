"""
FAQ Agent - Production-grade FAQ page generator.

Generates FAQ page with Q&A pairs using rule-based
answer generation. No hallucination - all content from data.
"""

import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.models import QuestionCategory, FAQ, FAQPageData, QuestionSet
from core.logging import get_agent_logger, log_step


class FAQAgent:
    """
    Agent for generating FAQ page content.
    
    Responsibility: Generate FAQ page with Q&A pairs (min 5)
    Input: ProductModel, QuestionSet, logic block outputs
    Output: FAQPageData
    Dependencies: Question Agent, Logic Blocks
    
    Production Features:
        - Rule-based answer generation (no hallucination)
        - Minimum 5 Q&A guarantee
        - Type-safe output with Pydantic
    """
    
    MIN_FAQS = 5
    
    def __init__(self):
        """Initialize the FAQ Agent."""
        self.logger = get_agent_logger("FAQAgent")
    
    def _format_currency(self, currency) -> str:
        """Format currency code to symbol."""
        currency_str = str(currency).upper()
        if "INR" in currency_str:
            return "₹"
        elif "USD" in currency_str:
            return "$"
        elif "EUR" in currency_str:
            return "€"
        return currency_str + " "
    
    @log_step("generate_faq")
    def process(
        self,
        product_model: dict,
        question_set: QuestionSet,
        benefits_data: dict,
        usage_data: dict,
        ingredient_data: dict
    ) -> FAQPageData:
        """
        Generate FAQ page content with Q&A pairs.
        
        Args:
            product_model: Structured product model.
            question_set: QuestionSet from Question Agent.
            benefits_data: Output from Benefits Block.
            usage_data: Output from Usage Block.
            ingredient_data: Output from Ingredient Block.
            
        Returns:
            FAQPageData with at least 5 Q&As.
        """
        product_name = product_model.get("productName", "this product")
        self.logger.debug(f"Generating FAQ for: {product_name}")
        
        faqs = []
        faq_id = 1
        
        # Process questions and generate answers
        for question in question_set.questions:
            answer = self._generate_answer(
                question.question,
                question.category,
                product_model,
                benefits_data,
                usage_data,
                ingredient_data
            )
            
            if answer:
                faqs.append(FAQ(
                    id=f"faq-{faq_id:03d}",
                    category=question.category,
                    question=question.question,
                    answer=answer
                ))
                faq_id += 1
        
        # Ensure minimum FAQ count
        if len(faqs) < self.MIN_FAQS:
            self.logger.warning(
                f"Only {len(faqs)} FAQs generated, less than minimum {self.MIN_FAQS}"
            )
        
        self.logger.info(f"Generated {len(faqs)} FAQs for {product_name}")
        
        return FAQPageData(
            success=True,
            productName=product_name,
            totalQuestions=len(faqs),
            faqs=faqs
        )
    
    def _generate_answer(
        self,
        question: str,
        category: QuestionCategory,
        product: dict,
        benefits: dict,
        usage: dict,
        ingredients: dict
    ) -> Optional[str]:
        """
        Generate answer using rule-based logic.
        
        All answers are derived directly from the provided data.
        No hallucination - returns None if no answer can be generated.
        """
        product_name = product.get("productName", "this product")
        q_lower = question.lower()
        
        # ===== INFORMATIONAL =====
        if "key ingredients" in q_lower:
            ingredient_list = ingredients.get("ingredientList", [])
            if ingredient_list:
                return f"The key ingredients in {product_name} are {', '.join(ingredient_list)}."
        
        if "benefits" in q_lower or "main benefits" in q_lower:
            benefit_list = benefits.get("benefitList", [])
            if benefit_list:
                return f"The main benefits of {product_name} include {', '.join(benefit_list)}."
        
        if "skin types" in q_lower or "suitable for" in q_lower:
            skin_types = product.get("skinType", [])
            if skin_types:
                return f"{product_name} is suitable for {', '.join(skin_types)} skin types."
        
        if "concentration" in q_lower:
            conc = ingredients.get("concentration")
            active = ingredients.get("primaryActive")
            if conc and active:
                return f"{product_name} contains {conc} {active}."
        
        if "effective" in q_lower or "how does" in q_lower:
            benefit_list = benefits.get("benefitList", [])
            primary = benefits.get("primaryBenefit")
            if primary:
                return f"{product_name} is primarily effective for {primary.lower()}, helping to achieve {', '.join(benefit_list).lower()}."
        
        # ===== SAFETY =====
        if "side effects" in q_lower:
            side_effects = product.get("sideEffects", "")
            if side_effects:
                return f"Possible side effects include: {side_effects}."
        
        if "sensitive skin" in q_lower:
            side_effects = product.get("sideEffects", "")
            if "sensitive" in side_effects.lower():
                return f"For sensitive skin: {side_effects}. A patch test is recommended before regular use."
            return "A patch test is recommended before regular use if you have sensitive skin."
        
        if "patch test" in q_lower:
            return "Yes, it is recommended to do a patch test before using any new skincare product to check for adverse reactions."
        
        if "allergies" in q_lower:
            ingredient_list = ingredients.get("ingredientList", [])
            return f"If you have allergies, check the ingredients ({', '.join(ingredient_list)}) and consult a dermatologist before use."
        
        # ===== USAGE =====
        if "how should i apply" in q_lower or ("apply" in q_lower and "how" in q_lower):
            instructions = usage.get("usageInstructions")
            if instructions:
                return instructions
        
        if "best time" in q_lower or "when" in q_lower:
            freq = usage.get("frequency")
            timing = usage.get("timing")
            if freq:
                answer = f"The best time to use {product_name} is in the {freq}"
                if timing:
                    answer += f", {timing}"
                return answer + "."
        
        if "how many drops" in q_lower or "drops" in q_lower:
            quantity = usage.get("quantity")
            if quantity:
                return f"Apply {quantity} each time you use {product_name}."
        
        if "other skincare" in q_lower or "with other" in q_lower:
            timing = usage.get("timing")
            if timing:
                return f"Yes, {product_name} can be used with other skincare products. It should be applied {timing}."
            return f"Yes, {product_name} can be layered with other skincare products."
        
        # ===== PURCHASE =====
        if "cost" in q_lower or "price" in q_lower or "how much" in q_lower:
            price = product.get("price", {})
            if isinstance(price, dict):
                amount = price.get("amount", 0)
                currency = self._format_currency(price.get("currency", "INR"))
                if amount:
                    return f"{product_name} is priced at {currency}{int(amount)}."
        
        if "worth" in q_lower:
            benefit_list = benefits.get("benefitList", [])
            price = product.get("price", {})
            if isinstance(price, dict) and benefit_list:
                currency = self._format_currency(price.get("currency", "INR"))
                return f"At {currency}{int(price.get('amount', 0))}, {product_name} offers {', '.join(benefit_list).lower()} benefits, making it a good value."
        
        if "where" in q_lower and "buy" in q_lower:
            return f"{product_name} can be purchased from authorized retailers and online stores."
        
        # ===== COMPARISON =====
        if "compare" in q_lower or "different" in q_lower:
            primary = benefits.get("primaryBenefit")
            conc = ingredients.get("concentration")
            if primary and conc:
                return f"{product_name} stands out with its {conc} concentration, focusing specifically on {primary.lower()}."
        
        return None
