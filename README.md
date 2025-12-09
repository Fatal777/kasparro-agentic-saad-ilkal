# Multi-Agent Content Generation System

A production-grade, modular agentic automation system that takes product datasets and autonomously generates structured, machine-readable content pages.

## 🎯 Overview

This system implements a **DAG-based multi-agent architecture** following the CAP theorem principles:

- **Consistency**: Type-safe Pydantic models & state persistence
- **Availability**: Retry logic with exponential backoff
- **Partition Tolerance**: Agent isolation & graceful degradation

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         ORCHESTRATOR                            │
│  (DAG Controller - manages execution order & message passing)   │
└─────────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌───────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ Parser Agent  │────▶│  Logic Blocks   │────▶│  Page Agents    │
│ (raw → model) │     │ (pure functions)│     │ (FAQ/Product/   │
└───────────────┘     └─────────────────┘     │  Comparison)    │
                                              └─────────────────┘
                                                      │
                                                      ▼
                                              ┌─────────────────┐
                                              │ Template Agent  │
                                              │ (validate+write)│
                                              └─────────────────┘
                                                      │
                                                      ▼
                                               JSON OUTPUT
```

## 📦 Project Structure

```
├── agents/                  # Agent implementations
│   ├── orchestrator.py      # DAG controller
│   ├── parser_agent.py      # Data parsing
│   ├── question_agent.py    # Question generation
│   ├── faq_agent.py         # FAQ page generation
│   ├── product_page_agent.py# Product page generation
│   ├── comparison_agent.py  # Comparison page generation
│   └── template_agent.py    # Template processing
│
├── logic_blocks/            # Pure function transformations
│   ├── benefits_block.py
│   ├── usage_block.py
│   ├── ingredient_block.py
│   └── comparison_block.py
│
├── core/                    # Production infrastructure
│   ├── models.py            # Pydantic data models
│   ├── config.py            # Configuration management
│   ├── logging.py           # Structured logging
│   ├── errors.py            # Error handling & retry
│   └── state.py             # State persistence
│
├── templates/               # JSON template schemas
├── data/                    # Input product data
├── output/                  # Generated JSON outputs
├── tests/                   # Unit & integration tests
└── docs/                    # Documentation
```

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd kasparro-agentic-content-generation

# Install dependencies
pip install -r requirements.txt

# Or install as package
pip install -e .
```

### Run the Pipeline

```bash
# Run the full pipeline
python -m agents.orchestrator

# Or use the entry point (if installed)
generate-content
```

### Expected Output

```
============================================================
Multi-Agent Content Generation System
============================================================

[PARSE_PRODUCTS] Starting...
  ✓ Parsed: GlowBoost Vitamin C Serum
  ✓ Parsed: ClearGlow Niacinamide Serum
[PARSE_PRODUCTS] Completed

[LOGIC_BLOCKS] Starting...
  ✓ Benefits: 2 items
  ✓ Usage: frequency=morning
  ✓ Ingredients: 2 items
  ✓ Comparison: price diff=₹100
[LOGIC_BLOCKS] Completed

...

✅ Pipeline completed successfully!
   Pipeline ID: 20251209_103000

Output files:
  - faq: output/faq.json
  - product_page: output/product_page.json
  - comparison_page: output/comparison_page.json
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=agents --cov=logic_blocks --cov=core

# Run specific test files
python tests/test_logic_blocks.py
python tests/test_agents.py
python tests/test_orchestrator.py
```

## ⚙️ Configuration

Set environment variables to configure the system:

```bash
# Environment (development, staging, production)
export PIPELINE_ENV=production

# Debug mode
export PIPELINE_DEBUG=false

# Logging level
export PIPELINE_LOGGING__LEVEL=WARNING
```

## 📄 Output Structure

### faq.json
```json
{
  "productName": "GlowBoost Vitamin C Serum",
  "generatedAt": "2025-12-09T10:00:00Z",
  "totalQuestions": 10,
  "faqs": [
    {
      "id": "faq-001",
      "category": "informational",
      "question": "What are the key ingredients?",
      "answer": "The key ingredients are Vitamin C and Hyaluronic Acid."
    }
  ]
}
```

### product_page.json
```json
{
  "productName": "GlowBoost Vitamin C Serum",
  "concentration": "10% Vitamin C",
  "skinTypes": ["Oily", "Combination"],
  "benefits": {
    "list": ["Brightening", "Fades dark spots"],
    "primary": "Brightening"
  },
  "usage": {
    "instructions": "Apply 2–3 drops in the morning before sunscreen",
    "frequency": "morning"
  },
  "price": {"amount": 699, "currency": "INR"}
}
```

### comparison_page.json
```json
{
  "productA": {"name": "GlowBoost Vitamin C Serum", ...},
  "productB": {"name": "ClearGlow Niacinamide Serum", ...},
  "comparison": {
    "commonIngredients": [],
    "uniqueToA": ["Vitamin C", "Hyaluronic Acid"],
    "uniqueToB": ["Niacinamide", "Salicylic Acid"],
    "priceDifference": 100,
    "recommendation": "GlowBoost is more affordable by ₹100..."
  }
}
```

## 🔧 Production Features

| Feature | Implementation |
|---------|---------------|
| **Type Safety** | Pydantic models with validation |
| **Error Handling** | Retry logic, circuit breaker |
| **State Persistence** | Checkpoint-based recovery |
| **Logging** | Structured logging with step tracking |
| **Configuration** | Environment-based settings |
| **Testing** | Unit + integration tests |

## 📋 Requirements

- Python 3.10+
- pydantic >= 2.5.0
- pydantic-settings >= 2.1.0

## 📝 License

MIT License
