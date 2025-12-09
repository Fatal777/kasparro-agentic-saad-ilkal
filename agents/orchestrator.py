"""
Orchestrator - DAG controller for multi-agent content generation system.

This is the main entry point that coordinates all agents and manages
the execution flow as a Directed Acyclic Graph (DAG).
"""

import json
import sys
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.parser_agent import ParserAgent
from agents.question_agent import QuestionAgent
from agents.faq_agent import FAQAgent
from agents.product_page_agent import ProductPageAgent
from agents.comparison_agent import ComparisonAgent
from agents.template_agent import TemplateAgent

from logic_blocks.benefits_block import process_benefits
from logic_blocks.usage_block import process_usage
from logic_blocks.ingredient_block import process_ingredients
from logic_blocks.comparison_block import compare_products


class Orchestrator:
    """
    DAG-based orchestrator for multi-agent content generation.
    
    Responsibility: 
        - DAG execution order management
        - Agent coordination and message passing
        - Output validation and file writing
    
    Execution Order (DAG):
        1. Parse Product Data (A & B)
        2. Process Logic Blocks
        3. Generate Questions
        4. Generate Page Content (parallel: FAQ, Product, Comparison)
        5. Fill Templates & Validate
        6. Write Output Files
    """
    
    def __init__(
        self,
        data_dir: str = "data",
        templates_dir: str = "templates",
        output_dir: str = "output"
    ):
        """
        Initialize the Orchestrator.
        
        Args:
            data_dir: Path to data directory.
            templates_dir: Path to templates directory.
            output_dir: Path to output directory.
        """
        self.data_dir = Path(data_dir)
        self.templates_dir = Path(templates_dir)
        self.output_dir = Path(output_dir)
        
        # Initialize agents
        self.parser_agent = ParserAgent()
        self.question_agent = QuestionAgent()
        self.faq_agent = FAQAgent()
        self.product_page_agent = ProductPageAgent()
        self.comparison_agent = ComparisonAgent()
        self.template_agent = TemplateAgent(templates_dir)
        
        # State storage for pipeline
        self._state = {}
    
    def run(self) -> dict:
        """
        Execute the full pipeline.
        
        Returns:
            Dictionary with execution results and output file paths.
        """
        print("=" * 60)
        print("Multi-Agent Content Generation System")
        print("=" * 60)
        
        try:
            # Step 1: Load and parse product data
            print("\n[Step 1] Parsing product data...")
            self._parse_products()
            
            # Step 2: Process logic blocks
            print("\n[Step 2] Processing logic blocks...")
            self._process_logic_blocks()
            
            # Step 3: Generate questions
            print("\n[Step 3] Generating questions...")
            self._generate_questions()
            
            # Step 4: Generate page content
            print("\n[Step 4] Generating page content...")
            self._generate_pages()
            
            # Step 5: Fill templates and validate
            print("\n[Step 5] Filling templates and validating...")
            self._fill_templates()
            
            # Step 6: Write output files
            print("\n[Step 6] Writing output files...")
            self._write_outputs()
            
            print("\n" + "=" * 60)
            print("Pipeline completed successfully!")
            print("=" * 60)
            
            return {
                "success": True,
                "outputs": {
                    "faq": str(self.output_dir / "faq.json"),
                    "product_page": str(self.output_dir / "product_page.json"),
                    "comparison_page": str(self.output_dir / "comparison_page.json")
                }
            }
            
        except Exception as e:
            print(f"\nError during pipeline execution: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _load_json(self, file_path: Path) -> dict:
        """Load JSON file."""
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _parse_products(self):
        """Step 1: Parse product data files."""
        # Load raw data
        product_a_raw = self._load_json(self.data_dir / "product_data.json")
        product_b_raw = self._load_json(self.data_dir / "product_b_data.json")
        
        # Parse through agent
        result_a = self.parser_agent.process(product_a_raw)
        result_b = self.parser_agent.process(product_b_raw)
        
        if not result_a["success"]:
            raise ValueError(f"Failed to parse Product A: {result_a['error']}")
        if not result_b["success"]:
            raise ValueError(f"Failed to parse Product B: {result_b['error']}")
        
        self._state["product_a"] = result_a["data"]
        self._state["product_b"] = result_b["data"]
        
        print(f"  ✓ Parsed: {self._state['product_a']['productName']}")
        print(f"  ✓ Parsed: {self._state['product_b']['productName']}")
    
    def _process_logic_blocks(self):
        """Step 2: Execute logic blocks on product data."""
        product_a = self._state["product_a"]
        product_b = self._state["product_b"]
        
        # Process Product A through logic blocks
        self._state["benefits_a"] = process_benefits(product_a)
        self._state["usage_a"] = process_usage(product_a)
        self._state["ingredients_a"] = process_ingredients(product_a)
        
        # Compare products
        self._state["comparison"] = compare_products(product_a, product_b)
        
        print(f"  ✓ Benefits: {self._state['benefits_a']['benefitCount']} items")
        print(f"  ✓ Usage: frequency={self._state['usage_a']['frequency']}")
        print(f"  ✓ Ingredients: {self._state['ingredients_a']['ingredientCount']} items")
        print(f"  ✓ Comparison: price diff=₹{self._state['comparison']['priceDifference']}")
    
    def _generate_questions(self):
        """Step 3: Generate categorized questions."""
        product_a = self._state["product_a"]
        
        question_result = self.question_agent.process(product_a)
        
        if not question_result["success"]:
            raise ValueError("Failed to generate questions")
        
        self._state["questions"] = question_result
        
        print(f"  ✓ Generated {question_result['totalQuestions']} questions")
        for cat, count in question_result["categoryCounts"].items():
            print(f"    - {cat}: {count}")
    
    def _generate_pages(self):
        """Step 4: Generate page content using page agents."""
        product_a = self._state["product_a"]
        product_b = self._state["product_b"]
        
        # FAQ Page
        faq_result = self.faq_agent.process(
            product_model=product_a,
            question_set=self._state["questions"],
            benefits_data=self._state["benefits_a"],
            usage_data=self._state["usage_a"],
            ingredient_data=self._state["ingredients_a"]
        )
        self._state["faq_page"] = faq_result
        print(f"  ✓ FAQ Page: {faq_result['totalQuestions']} Q&As")
        
        # Product Page
        product_result = self.product_page_agent.process(
            product_model=product_a,
            benefits_data=self._state["benefits_a"],
            usage_data=self._state["usage_a"],
            ingredient_data=self._state["ingredients_a"]
        )
        self._state["product_page"] = product_result
        print(f"  ✓ Product Page: {product_result['productName']}")
        
        # Comparison Page
        comparison_result = self.comparison_agent.process(
            product_a=product_a,
            product_b=product_b,
            comparison_data=self._state["comparison"]
        )
        self._state["comparison_page"] = comparison_result
        print(f"  ✓ Comparison Page: {comparison_result['productA']['name']} vs {comparison_result['productB']['name']}")
    
    def _fill_templates(self):
        """Step 5: Fill templates and validate output."""
        # FAQ Template
        faq_output = self.template_agent.process("faq", self._state["faq_page"])
        if not faq_output["success"]:
            raise ValueError(f"FAQ template validation failed: {faq_output['error']}")
        self._state["faq_output"] = faq_output["data"]
        print("  ✓ FAQ template validated")
        
        # Product Template
        product_output = self.template_agent.process("product", self._state["product_page"])
        if not product_output["success"]:
            raise ValueError(f"Product template validation failed: {product_output['error']}")
        self._state["product_output"] = product_output["data"]
        print("  ✓ Product template validated")
        
        # Comparison Template
        comparison_output = self.template_agent.process("comparison", self._state["comparison_page"])
        if not comparison_output["success"]:
            raise ValueError(f"Comparison template validation failed: {comparison_output['error']}")
        self._state["comparison_output"] = comparison_output["data"]
        print("  ✓ Comparison template validated")
    
    def _write_outputs(self):
        """Step 6: Write validated JSON files."""
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Write FAQ
        faq_path = self.output_dir / "faq.json"
        self.template_agent.write_output(faq_path, self._state["faq_output"])
        print(f"  ✓ Written: {faq_path}")
        
        # Write Product Page
        product_path = self.output_dir / "product_page.json"
        self.template_agent.write_output(product_path, self._state["product_output"])
        print(f"  ✓ Written: {product_path}")
        
        # Write Comparison Page
        comparison_path = self.output_dir / "comparison_page.json"
        self.template_agent.write_output(comparison_path, self._state["comparison_output"])
        print(f"  ✓ Written: {comparison_path}")


def main():
    """Main entry point."""
    orchestrator = Orchestrator()
    result = orchestrator.run()
    
    if result["success"]:
        print("\nOutput files:")
        for name, path in result["outputs"].items():
            print(f"  - {name}: {path}")
        return 0
    else:
        print(f"\nFailed: {result.get('error', 'Unknown error')}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
