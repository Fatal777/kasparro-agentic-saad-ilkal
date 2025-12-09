"""
Data Models - Pydantic models for type safety and validation.

These models enforce schema validation, type checking, and provide
clear contracts between agents (CAP: Consistency).
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


# ============================================================================
# Enums
# ============================================================================

class QuestionCategory(str, Enum):
    """Enum for question categories."""
    INFORMATIONAL = "informational"
    SAFETY = "safety"
    USAGE = "usage"
    PURCHASE = "purchase"
    COMPARISON = "comparison"


class Currency(str, Enum):
    """Supported currencies."""
    INR = "INR"
    USD = "USD"
    EUR = "EUR"


# ============================================================================
# Core Models
# ============================================================================

class Price(BaseModel):
    """Price model with currency support."""
    amount: float = Field(..., ge=0, description="Price amount")
    currency: Currency = Field(default=Currency.INR, description="Currency code")
    
    model_config = {"extra": "forbid"}


class ProductModel(BaseModel):
    """
    Internal product model - the canonical representation of a product.
    
    All agents work with this model to ensure consistency across the pipeline.
    """
    productName: str = Field(..., min_length=1, max_length=200)
    concentration: str = Field(default="")
    skinType: list[str] = Field(default_factory=list)
    keyIngredients: list[str] = Field(default_factory=list, min_length=1)
    benefits: list[str] = Field(default_factory=list, min_length=1)
    howToUse: str = Field(default="")
    sideEffects: str = Field(default="")
    price: Price
    
    model_config = {"extra": "forbid"}
    
    @field_validator("keyIngredients", "benefits")
    @classmethod
    def validate_non_empty_strings(cls, v):
        """Ensure list items are non-empty strings."""
        return [item.strip() for item in v if item.strip()]


# ============================================================================
# Logic Block Output Models
# ============================================================================

class BenefitsData(BaseModel):
    """Output model for benefits_block."""
    benefitList: list[str] = Field(default_factory=list)
    benefitCount: int = Field(ge=0)
    primaryBenefit: Optional[str] = None
    
    model_config = {"extra": "forbid"}


class UsageData(BaseModel):
    """Output model for usage_block."""
    usageInstructions: str = Field(default="")
    frequency: Optional[str] = None
    quantity: Optional[str] = None
    timing: Optional[str] = None
    
    model_config = {"extra": "forbid"}


class IngredientData(BaseModel):
    """Output model for ingredient_block."""
    ingredientList: list[str] = Field(default_factory=list)
    ingredientCount: int = Field(ge=0)
    primaryActive: Optional[str] = None
    concentration: Optional[str] = None
    
    model_config = {"extra": "forbid"}


class ComparisonData(BaseModel):
    """Output model for comparison_block."""
    commonIngredients: list[str] = Field(default_factory=list)
    uniqueToProductA: list[str] = Field(default_factory=list)
    uniqueToProductB: list[str] = Field(default_factory=list)
    commonBenefits: list[str] = Field(default_factory=list)
    uniqueBenefitsA: list[str] = Field(default_factory=list)
    uniqueBenefitsB: list[str] = Field(default_factory=list)
    priceDifference: float = Field(ge=0)
    cheaperProduct: str = Field(default="equal")
    
    model_config = {"extra": "forbid"}


# ============================================================================
# Question Models
# ============================================================================

class Question(BaseModel):
    """Single question model."""
    id: str = Field(..., pattern=r"^q-\d{3}$")
    category: QuestionCategory
    question: str = Field(..., min_length=5)
    
    model_config = {"extra": "forbid"}


class QuestionSet(BaseModel):
    """Output model for question_agent."""
    success: bool = True
    productName: str
    totalQuestions: int = Field(ge=0)
    questions: list[Question] = Field(default_factory=list)
    categoryCounts: dict[str, int] = Field(default_factory=dict)
    
    model_config = {"extra": "forbid"}


# ============================================================================
# FAQ Models
# ============================================================================

class FAQ(BaseModel):
    """Single FAQ entry."""
    id: str = Field(..., pattern=r"^faq-\d{3}$")
    category: QuestionCategory
    question: str = Field(..., min_length=5)
    answer: str = Field(..., min_length=5)
    
    model_config = {"extra": "forbid"}


class FAQPageData(BaseModel):
    """Output model for faq_agent."""
    success: bool = True
    productName: str
    generatedAt: Optional[datetime] = None
    totalQuestions: int = Field(ge=5)  # Minimum 5 Q&As required
    faqs: list[FAQ] = Field(..., min_length=5)
    
    model_config = {"extra": "forbid"}


# ============================================================================
# Product Page Models
# ============================================================================

class BenefitsSection(BaseModel):
    """Benefits section for product page."""
    list: list[str] = Field(default_factory=list)
    primary: str = Field(default="")
    count: int = Field(ge=0)


class UsageSection(BaseModel):
    """Usage section for product page."""
    instructions: str = Field(default="")
    frequency: str = Field(default="")
    quantity: str = Field(default="")
    timing: str = Field(default="")


class ProductPageData(BaseModel):
    """Output model for product_page_agent."""
    success: bool = True
    productName: str
    concentration: str = Field(default="")
    skinTypes: list[str] = Field(default_factory=list)
    keyIngredients: list[str] = Field(default_factory=list)
    benefits: BenefitsSection
    usage: UsageSection
    sideEffects: str = Field(default="")
    price: Price
    generatedAt: Optional[datetime] = None
    
    model_config = {"extra": "forbid"}


# ============================================================================
# Comparison Page Models
# ============================================================================

class ProductSummary(BaseModel):
    """Product summary for comparison."""
    name: str
    concentration: str = Field(default="")
    price: float = Field(ge=0)
    currency: str = Field(default="INR")
    benefits: list[str] = Field(default_factory=list)
    ingredients: list[str] = Field(default_factory=list)
    skinTypes: list[str] = Field(default_factory=list)


class ComparisonSection(BaseModel):
    """Comparison details section."""
    commonIngredients: list[str] = Field(default_factory=list)
    uniqueToA: list[str] = Field(default_factory=list)
    uniqueToB: list[str] = Field(default_factory=list)
    commonBenefits: list[str] = Field(default_factory=list)
    uniqueBenefitsA: list[str] = Field(default_factory=list)
    uniqueBenefitsB: list[str] = Field(default_factory=list)
    priceDifference: float = Field(ge=0)
    cheaperProduct: str
    recommendation: str = Field(default="")


class ComparisonPageData(BaseModel):
    """Output model for comparison_agent."""
    success: bool = True
    productA: ProductSummary
    productB: ProductSummary
    comparison: ComparisonSection
    generatedAt: Optional[datetime] = None
    
    model_config = {"extra": "forbid"}


# ============================================================================
# Agent Result Models
# ============================================================================

class AgentResult(BaseModel):
    """Generic result wrapper for agent operations."""
    success: bool
    error: Optional[str] = None
    data: Optional[dict] = None
    
    model_config = {"extra": "allow"}
