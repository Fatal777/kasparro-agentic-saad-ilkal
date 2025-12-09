"""
Logic Blocks Package

This package contains pure function logic blocks for content transformation.
Each block follows single-responsibility principle with deterministic output.
"""

from logic_blocks.benefits_block import process_benefits
from logic_blocks.usage_block import process_usage
from logic_blocks.ingredient_block import process_ingredients
from logic_blocks.comparison_block import compare_products

__all__ = [
    "process_benefits",
    "process_usage", 
    "process_ingredients",
    "compare_products"
]
