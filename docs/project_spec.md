# Project Specification: BrandWise AutoDoc

This document outlines the vision and requirements for the **BrandWise AutoDoc** system, a self-improving, brand-aware document creation agentic suite.

## Core Objective
To develop a suite of interconnected AI agents capable of autonomously creating and refining documents while possessing the ability to learn and adapt over time, ensuring all generated content strictly adheres to predefined brand guidelines.

## 1. Agent Architecture (The "Mesh")
We will implement a multi-agent system where roles are clearly decoupled:
- **The Strategist:** Document structuring and task decomposition.
- **The Wordsmith:** Core content generation and stylistic execution.
- **The Brand Guardian:** Compliance monitoring and tone enforcement.
- **The Researcher:** External data gathering (inspired by `autoresearch`).
- **The Evaluator:** Improvement loop driver and feedback synthesizer.

## 2. Self-Improvement Mechanism
- **RLAIF (Reinforcement Learning from AI Feedback):** The Evaluator critiques the Wordsmith and Brand Guardian.
- **Case-Based Reasoning:** System stores past successful and failed document attempts in a "Experience Buffer" (Vector DB).
- **Skill Evolution:** Dynamic updates to agent "Skills" (inspired by `skills.sh`).

## 3. Brand Awareness
- **Knowledge Ingestion:** Dynamic ingestion of PDFs and style guides.
- **Tone-of-Voice Embedding:** Using semantic analysis to ensure the latent vector of the content aligns with the brand vector.
- **Prohibited Terminology Filters:** Automated red-teaming.

## 4. Technical Stack
- **Language:** Python 3.10+
- **Orchestration:** LangGraph (for stateful, cyclic agent workflows).
- **LLMs:** Gemini 1.5 Pro / GPT-4o.
- **Vector Database:** Pinecone or ChromaDB.
- **Environment:** Dockerized microservices or a unified monorepo.

---

## Inspiration & Resources
- [karpathy/autoresearch](https://github.com/karpathy/autoresearch)
- [skills.sh](https://skills.sh/)
