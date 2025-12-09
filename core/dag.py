"""
DAG (Directed Acyclic Graph) Validation Module

This module provides explicit DAG validation for the multi-agent pipeline,
ensuring no circular dependencies and correct execution order.
"""

from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
from enum import Enum


class AgentType(Enum):
    """Enumeration of all agent types in the system."""
    PARSER = "ParserAgent"
    QUESTION = "QuestionAgent"
    FAQ = "FAQAgent"
    PRODUCT_PAGE = "ProductPageAgent"
    COMPARISON = "ComparisonAgent"
    TEMPLATE = "TemplateAgent"


@dataclass
class DAGNode:
    """Represents a node in the execution DAG."""
    agent: AgentType
    dependencies: List[AgentType]
    description: str


class DAGValidator:
    """
    Validates the execution DAG for the multi-agent pipeline.
    
    Ensures:
    - No circular dependencies
    - All dependencies are satisfied before execution
    - Correct topological ordering
    """
    
    def __init__(self):
        """Initialize the DAG with agent dependencies."""
        self.nodes: Dict[AgentType, DAGNode] = {
            AgentType.PARSER: DAGNode(
                agent=AgentType.PARSER,
                dependencies=[],
                description="Parses raw product data into structured models"
            ),
            AgentType.QUESTION: DAGNode(
                agent=AgentType.QUESTION,
                dependencies=[AgentType.PARSER],
                description="Generates categorized questions from parsed data"
            ),
            AgentType.FAQ: DAGNode(
                agent=AgentType.FAQ,
                dependencies=[AgentType.PARSER, AgentType.QUESTION],
                description="Creates FAQ page from questions and product data"
            ),
            AgentType.PRODUCT_PAGE: DAGNode(
                agent=AgentType.PRODUCT_PAGE,
                dependencies=[AgentType.PARSER],
                description="Builds product page from parsed data"
            ),
            AgentType.COMPARISON: DAGNode(
                agent=AgentType.COMPARISON,
                dependencies=[AgentType.PARSER],
                description="Compares two products"
            ),
            AgentType.TEMPLATE: DAGNode(
                agent=AgentType.TEMPLATE,
                dependencies=[AgentType.FAQ, AgentType.PRODUCT_PAGE, AgentType.COMPARISON],
                description="Validates and formats final JSON output"
            ),
        }
    
    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate the DAG for correctness.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check for circular dependencies
        if self._has_cycle():
            errors.append("Circular dependency detected in agent graph")
        
        # Check all dependencies exist
        for agent, node in self.nodes.items():
            for dep in node.dependencies:
                if dep not in self.nodes:
                    errors.append(f"{agent.value} depends on unknown agent {dep.value}")
        
        return len(errors) == 0, errors
    
    def _has_cycle(self) -> bool:
        """Detect cycles using DFS with coloring."""
        WHITE, GRAY, BLACK = 0, 1, 2
        color: Dict[AgentType, int] = {agent: WHITE for agent in self.nodes}
        
        def dfs(agent: AgentType) -> bool:
            color[agent] = GRAY
            for dep in self.nodes[agent].dependencies:
                if color[dep] == GRAY:
                    return True  # Back edge = cycle
                if color[dep] == WHITE and dfs(dep):
                    return True
            color[agent] = BLACK
            return False
        
        for agent in self.nodes:
            if color[agent] == WHITE:
                if dfs(agent):
                    return True
        return False
    
    def get_execution_order(self) -> List[AgentType]:
        """
        Get topologically sorted execution order.
        
        Returns:
            List of agents in correct execution order
        """
        visited: Set[AgentType] = set()
        order: List[AgentType] = []
        
        def dfs(agent: AgentType):
            if agent in visited:
                return
            visited.add(agent)
            for dep in self.nodes[agent].dependencies:
                dfs(dep)
            order.append(agent)
        
        for agent in self.nodes:
            dfs(agent)
        
        return order
    
    def get_dependency_graph(self) -> Dict[str, List[str]]:
        """
        Get the dependency graph as a dictionary for visualization.
        
        Returns:
            Dict mapping agent names to their dependencies
        """
        return {
            agent.value: [dep.value for dep in node.dependencies]
            for agent, node in self.nodes.items()
        }
    
    def print_execution_plan(self) -> str:
        """
        Generate a human-readable execution plan.
        
        Returns:
            Formatted string showing execution order and dependencies
        """
        order = self.get_execution_order()
        lines = ["=" * 50, "EXECUTION PLAN (DAG Validated)", "=" * 50]
        
        for i, agent in enumerate(order, 1):
            node = self.nodes[agent]
            deps = ", ".join(d.value for d in node.dependencies) or "None"
            lines.append(f"\nStep {i}: {agent.value}")
            lines.append(f"  Dependencies: {deps}")
            lines.append(f"  Description: {node.description}")
        
        lines.append("\n" + "=" * 50)
        return "\n".join(lines)


def validate_pipeline_dag() -> bool:
    """
    Validate the pipeline DAG and print results.
    
    Returns:
        True if DAG is valid, False otherwise
    """
    validator = DAGValidator()
    is_valid, errors = validator.validate()
    
    if is_valid:
        print("✅ DAG Validation: PASSED")
        print(validator.print_execution_plan())
    else:
        print("❌ DAG Validation: FAILED")
        for error in errors:
            print(f"  - {error}")
    
    return is_valid


if __name__ == "__main__":
    validate_pipeline_dag()
