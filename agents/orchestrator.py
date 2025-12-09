"""
Orchestrator - Production-grade DAG controller.

Coordinates all agents and manages execution flow with:
- State persistence and recovery
- Structured logging and step tracking
- Error handling with graceful degradation
- CAP theorem implementation
"""

import json
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

# Add project root
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

from core.config import Settings, get_settings
from core.logging import PipelineLogger, StepTracker, get_agent_logger
from core.errors import PipelineError, DataLoadError, AgentError
from core.state import StateManager


class Orchestrator:
    """
    DAG-based orchestrator for multi-agent content generation.
    
    Production Features:
        - State persistence (CAP: Consistency)
        - Retry logic (CAP: Availability)
        - Agent isolation (CAP: Partition tolerance)
        - Structured logging and step tracking
        - Checkpoint-based recovery
    
    Execution Order (DAG):
        1. Parse Product Data (A & B)
        2. Process Logic Blocks
        3. Generate Questions
        4. Generate Page Content
        5. Fill Templates & Validate
        6. Write Output Files
    """
    
    def __init__(
        self,
        data_dir: str = "data",
        templates_dir: str = "templates",
        output_dir: str = "output",
        settings: Optional[Settings] = None
    ):
        """
        Initialize the Orchestrator.
        
        Args:
            data_dir: Path to data directory.
            templates_dir: Path to templates directory.
            output_dir: Path to output directory.
            settings: Optional settings override.
        """
        self.data_dir = Path(data_dir)
        self.templates_dir = Path(templates_dir)
        self.output_dir = Path(output_dir)
        self.settings = settings or get_settings()
        
        # Initialize logging
        PipelineLogger.initialize(
            level=self.settings.logging.level,
            log_format=self.settings.logging.format,
            log_to_file=self.settings.logging.log_to_file,
            log_file_path=Path(self.settings.paths.logs_dir) / self.settings.logging.log_file_name
        )
        
        self.logger = get_agent_logger("Orchestrator")
        self.step_tracker = StepTracker()
        
        # Initialize state manager for persistence
        self.state_manager = StateManager(
            state_dir=self.output_dir / ".state"
        )
        
        # Initialize agents (lazy - created on first use)
        self._parser_agent: Optional[ParserAgent] = None
        self._question_agent: Optional[QuestionAgent] = None
        self._faq_agent: Optional[FAQAgent] = None
        self._product_page_agent: Optional[ProductPageAgent] = None
        self._comparison_agent: Optional[ComparisonAgent] = None
        self._template_agent: Optional[TemplateAgent] = None
    
    # ===== Agent Properties (Lazy Initialization) =====
    
    @property
    def parser_agent(self) -> ParserAgent:
        if self._parser_agent is None:
            self._parser_agent = ParserAgent()
        return self._parser_agent
    
    @property
    def question_agent(self) -> QuestionAgent:
        if self._question_agent is None:
            self._question_agent = QuestionAgent()
        return self._question_agent
    
    @property
    def faq_agent(self) -> FAQAgent:
        if self._faq_agent is None:
            self._faq_agent = FAQAgent()
        return self._faq_agent
    
    @property
    def product_page_agent(self) -> ProductPageAgent:
        if self._product_page_agent is None:
            self._product_page_agent = ProductPageAgent()
        return self._product_page_agent
    
    @property
    def comparison_agent(self) -> ComparisonAgent:
        if self._comparison_agent is None:
            self._comparison_agent = ComparisonAgent()
        return self._comparison_agent
    
    @property
    def template_agent(self) -> TemplateAgent:
        if self._template_agent is None:
            self._template_agent = TemplateAgent(str(self.templates_dir))
        return self._template_agent
    
    # ===== Main Execution =====
    
    def run(self, resume_from: Optional[str] = None) -> dict:
        """
        Execute the full pipeline.
        
        Args:
            resume_from: Optional pipeline_id to resume from checkpoint.
            
        Returns:
            Dictionary with execution results and output file paths.
        """
        self.logger.info("=" * 60)
        self.logger.info("Multi-Agent Content Generation System")
        self.logger.info("=" * 60)
        
        # Check for resume
        if resume_from and self.state_manager.load_checkpoint(resume_from):
            self.logger.info(f"Resuming from checkpoint: {resume_from}")
        
        try:
            # Step 1: Parse products
            self._execute_step("parse_products", self._parse_products)
            
            # Step 2: Process logic blocks
            self._execute_step("logic_blocks", self._process_logic_blocks)
            
            # Step 3: Generate questions
            self._execute_step("generate_questions", self._generate_questions)
            
            # Step 4: Generate pages
            self._execute_step("generate_pages", self._generate_pages)
            
            # Step 5: Fill templates
            self._execute_step("fill_templates", self._fill_templates)
            
            # Step 6: Write outputs
            self._execute_step("write_outputs", self._write_outputs)
            
            # Mark complete
            self.state_manager.complete()
            
            self.logger.info("=" * 60)
            self.logger.info("Pipeline completed successfully!")
            self.logger.info("=" * 60)
            
            return {
                "success": True,
                "pipeline_id": self.state_manager.state.pipeline_id,
                "outputs": {
                    "faq": str(self.output_dir / "faq.json"),
                    "product_page": str(self.output_dir / "product_page.json"),
                    "comparison_page": str(self.output_dir / "comparison_page.json")
                },
                "execution_summary": self.step_tracker.get_summary()
            }
            
        except PipelineError as e:
            self.logger.error(f"Pipeline failed: {e}")
            self.state_manager.fail(str(e))
            return {
                "success": False,
                "error": str(e),
                "execution_summary": self.step_tracker.get_summary()
            }
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            self.state_manager.fail(str(e))
            return {
                "success": False,
                "error": str(e),
                "execution_summary": self.step_tracker.get_summary()
            }
    
    def _execute_step(self, step_name: str, step_func) -> None:
        """Execute a pipeline step with tracking."""
        # Skip if already completed (resume scenario)
        if self.state_manager.can_resume_from(step_name):
            self.logger.info(f"Skipping completed step: {step_name}")
            return
        
        self.step_tracker.start_step(step_name)
        self.logger.info(f"\n[{step_name.upper()}] Starting...")
        
        try:
            step_func()
            self.state_manager.checkpoint(step_name)
            self.step_tracker.complete_step()
            self.logger.info(f"[{step_name.upper()}] Completed")
        except Exception as e:
            self.step_tracker.fail_step(str(e))
            raise
    
    # ===== Pipeline Steps =====
    
    def _load_json(self, file_path: Path) -> dict:
        """Load JSON file with proper error handling."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            raise DataLoadError(str(file_path), "File not found")
        except json.JSONDecodeError as e:
            raise DataLoadError(str(file_path), f"Invalid JSON: {e}")
    
    def _parse_products(self):
        """Step 1: Parse product data files."""
        # Load raw data
        product_a_raw = self._load_json(self.data_dir / "product_data.json")
        product_b_raw = self._load_json(self.data_dir / "product_b_data.json")
        
        # Parse through agent
        result_a = self.parser_agent.process(product_a_raw)
        result_b = self.parser_agent.process(product_b_raw)
        
        if not result_a.success:
            raise AgentError("ParserAgent", result_a.error or "Unknown error")
        if not result_b.success:
            raise AgentError("ParserAgent", result_b.error or "Unknown error")
        
        # Store in state
        self.state_manager.set_data("product_a", result_a.data)
        self.state_manager.set_data("product_b", result_b.data)
        
        self.logger.info(f"  ✓ Parsed: {result_a.data['productName']}")
        self.logger.info(f"  ✓ Parsed: {result_b.data['productName']}")
    
    def _process_logic_blocks(self):
        """Step 2: Execute logic blocks on product data."""
        product_a = self.state_manager.get_data("product_a")
        product_b = self.state_manager.get_data("product_b")
        
        # Process Product A through logic blocks
        benefits_data = process_benefits(product_a)
        usage_data = process_usage(product_a)
        ingredients_data = process_ingredients(product_a)
        comparison_data = compare_products(product_a, product_b)
        
        # Store in state
        self.state_manager.set_data("benefits_data", benefits_data)
        self.state_manager.set_data("usage_data", usage_data)
        self.state_manager.set_data("ingredients_data", ingredients_data)
        self.state_manager.set_data("comparison_data", comparison_data)
        
        self.logger.info(f"  ✓ Benefits: {benefits_data['benefitCount']} items")
        self.logger.info(f"  ✓ Usage: frequency={usage_data['frequency']}")
        self.logger.info(f"  ✓ Ingredients: {ingredients_data['ingredientCount']} items")
        self.logger.info(f"  ✓ Comparison: price diff=₹{comparison_data['priceDifference']}")
    
    def _generate_questions(self):
        """Step 3: Generate categorized questions."""
        product_a = self.state_manager.get_data("product_a")
        
        question_set = self.question_agent.process(product_a)
        
        # Store in state (as dict for JSON serialization)
        self.state_manager.set_data("questions", question_set.model_dump(mode="json"))
        
        self.logger.info(f"  ✓ Generated {question_set.totalQuestions} questions")
        for cat, count in question_set.categoryCounts.items():
            self.logger.info(f"    - {cat}: {count}")
    
    def _generate_pages(self):
        """Step 4: Generate page content using page agents."""
        product_a = self.state_manager.get_data("product_a")
        product_b = self.state_manager.get_data("product_b")
        benefits_data = self.state_manager.get_data("benefits_data")
        usage_data = self.state_manager.get_data("usage_data")
        ingredients_data = self.state_manager.get_data("ingredients_data")
        comparison_data = self.state_manager.get_data("comparison_data")
        
        # Reconstruct QuestionSet from stored data
        from core.models import QuestionSet
        questions_dict = self.state_manager.get_data("questions")
        question_set = QuestionSet(**questions_dict)
        
        # Generate FAQ Page
        faq_page = self.faq_agent.process(
            product_model=product_a,
            question_set=question_set,
            benefits_data=benefits_data,
            usage_data=usage_data,
            ingredient_data=ingredients_data
        )
        self.state_manager.set_data("faq_page", faq_page.model_dump(mode="json"))
        self.logger.info(f"  ✓ FAQ Page: {faq_page.totalQuestions} Q&As")
        
        # Generate Product Page
        product_page = self.product_page_agent.process(
            product_model=product_a,
            benefits_data=benefits_data,
            usage_data=usage_data,
            ingredient_data=ingredients_data
        )
        self.state_manager.set_data("product_page", product_page.model_dump(mode="json"))
        self.logger.info(f"  ✓ Product Page: {product_page.productName}")
        
        # Generate Comparison Page
        comparison_page = self.comparison_agent.process(
            product_a=product_a,
            product_b=product_b,
            comparison_data=comparison_data
        )
        self.state_manager.set_data("comparison_page", comparison_page.model_dump(mode="json"))
        self.logger.info(f"  ✓ Comparison Page: {comparison_page.productA.name} vs {comparison_page.productB.name}")
    
    def _fill_templates(self):
        """Step 5: Fill templates and validate output."""
        faq_data = self.state_manager.get_data("faq_page")
        product_data = self.state_manager.get_data("product_page")
        comparison_data = self.state_manager.get_data("comparison_page")
        
        # FAQ Template
        faq_result = self.template_agent.process("faq", faq_data)
        if not faq_result.success:
            raise AgentError("TemplateAgent", faq_result.error or "FAQ template failed")
        self.state_manager.set_data("faq_output", faq_result.data)
        self.logger.info("  ✓ FAQ template validated")
        
        # Product Template
        product_result = self.template_agent.process("product", product_data)
        if not product_result.success:
            raise AgentError("TemplateAgent", product_result.error or "Product template failed")
        self.state_manager.set_data("product_output", product_result.data)
        self.logger.info("  ✓ Product template validated")
        
        # Comparison Template
        comparison_result = self.template_agent.process("comparison", comparison_data)
        if not comparison_result.success:
            raise AgentError("TemplateAgent", comparison_result.error or "Comparison template failed")
        self.state_manager.set_data("comparison_output", comparison_result.data)
        self.logger.info("  ✓ Comparison template validated")
    
    def _write_outputs(self):
        """Step 6: Write validated JSON files."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Write FAQ
        faq_path = self.output_dir / "faq.json"
        self.template_agent.write_output(
            faq_path, 
            self.state_manager.get_data("faq_output")
        )
        
        # Write Product Page
        product_path = self.output_dir / "product_page.json"
        self.template_agent.write_output(
            product_path,
            self.state_manager.get_data("product_output")
        )
        
        # Write Comparison Page
        comparison_path = self.output_dir / "comparison_page.json"
        self.template_agent.write_output(
            comparison_path,
            self.state_manager.get_data("comparison_output")
        )


def main():
    """Main entry point."""
    orchestrator = Orchestrator()
    result = orchestrator.run()
    
    if result["success"]:
        print("\n✅ Pipeline completed successfully!")
        print(f"   Pipeline ID: {result['pipeline_id']}")
        print("\nOutput files:")
        for name, path in result["outputs"].items():
            print(f"  - {name}: {path}")
        return 0
    else:
        print(f"\n❌ Pipeline failed: {result.get('error', 'Unknown error')}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
