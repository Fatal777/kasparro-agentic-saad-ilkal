pplied AI Engineer Challenge
Multi-Agent Content Generation System
🎯 Objective

Design and implement a modular agentic automation system that takes a small product dataset and automatically generates structured, machine-readable content pages.

This assignment evaluates your ability to design:

multi-agent workflows

automation graphs

reusable content logic

template-based generation

structured JSON output

system abstraction & documentation

You are NOT being tested on domain expertise — only engineering and system design ability.

📦 Product Data (The Only Input Allowed)

Use ONLY the following dataset.
You may not add new facts or research externally.

Product Name: GlowBoost Vitamin C Serum
Concentration: 10% Vitamin C
Skin Type: Oily, Combination
Key Ingredients: Vitamin C, Hyaluronic Acid
Benefits: Brightening, Fades dark spots
How to Use: Apply 2–3 drops in the morning before sunscreen
Side Effects: Mild tingling for sensitive skin
Price: ₹699


Your system must be able to operate on this type of data.

✅ Assignment Requirements
✔ 1. Parse & Understand Product Data

Convert it into a clean internal model.

✔ 2. Automatically Generate 15+ Categorized User Questions

Categories may include:
Informational, Safety, Usage, Purchase, Comparison, etc.

✔ 3. Define & Implement Your Own Templates

You must create templates for:

FAQ Page

Product Description Page

Comparison Page

✔ 4. Create Reusable “Content Logic Blocks”

Examples:

generate-benefits-block

extract-usage-block

compare-ingredients-block

These must be modular, reusable transformations.

✔ 5. Assemble 3 Pages Using the System

Agents must autonomously generate:

FAQ Page (min 5 Q&As)

Product Page

Comparison Page (GlowBoost vs fictional Product B — structured)

Product B must be fictional but include name, ingredients, benefits, price.

✔ 6. Output Pages as Machine-Readable JSON

Examples:

faq.json

product_page.json

comparison_page.json

✔ 7. Entire Pipeline Must Run via Agents

Not a monolithic script or direct prompting.

❌ What This Assignment Is NOT

Not a prompting assignment

Not “one big function calling GPT three times”

Not a content writing test

Not a UI/website challenge

This is a systems design + automation + agent orchestration challenge.

⚙️ System Requirements
1. Clear Agent Boundaries

Each agent must have:

single responsibility

defined input/output

no hidden global state

2. Automation Flow / Orchestration Graph

Examples:

DAG

step pipeline

state machine

message-passing

orchestrator → worker agents

3. Reusable Logic Blocks

Examples:

generate-benefits-block

extract-usage-block

compare-ingredients-block

4. Template Engine of Your Own Design

Each template should define:

fields

rules

formatting

dependencies on content blocks

5. Machine-Readable Output

All final pages must be strict JSON, not free text.

📁 Repository Requirements

GitHub repo name:

kasparro-ai-agentic-content-generation-system-<first_name-last_name>

Repo must include:
docs/
  projectdocumentation.md

docs/projectdocumentation.md MUST contain:

Problem Statement

Solution Overview

Scopes & Assumptions

System Design (MANDATORY — most important)

Optional: diagrams, flowcharts, sequence diagrams

Do not include file-by-file explanation or folder walkthrough.

📤 Submission

Share the GitHub repository link.

📊 Evaluation Criteria
1. Agentic System Design (45%)

clear responsibilities

modularity

extensibility

correctness of pipeline

2. Types & Quality of Agents (25%)

meaningful roles

correct boundaries

correct input/output

3. Content System Engineering (20%)

reusable templates

clean logic blocks

composability

4. Data & Output Structure (10%)

JSON correctness

clean mapping: data → logic → output

🧭 Purpose

This assignment measures your ability to design production-style agentic systems.