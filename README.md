# Production Incident Commander - AI Agent

## Overview
This repository contains the implementation of an AI-powered "Production Incident Commander." The goal of this agent is to assist Site Reliability Engineers (SREs) by automatically ingesting, analyzing, and synthesizing telemetry data (logs, metrics, alerts, and historical incidents) to diagnose production issues and recommend remediation steps.

The agent operates against a simulated e-commerce microservices environment ("ShopFabric") and uses **LangGraph's ReAct (Reason + Act)** framework. By exposing raw data abstractions as tools, the agent dynamically investigates alerts, forms hypotheses, gathers evidence from logs and metrics, and correlates data to pinpoint root causes, instead of relying on a predefined checklist.

## Project Status & Log

We are documenting our development progress here step-by-step so reviewers can follow our thought process and implementation strategy.

### [Phase 1: Project Setup & Discovery] - Completed
- [x] Initialized the project directory.
- [x] Analyzed the provided dataset (`architecture_overview.json`, `incidents.json`, etc.) to understand the ShopFabric topology and historical failure modes.
- [x] Drafted initial project strategy and architecture for the AI Agent.
- [x] Initialize Git repository and `.gitignore`.
- [x] Set up Python virtual environment and `requirements.txt`.

### [Phase 2: Data Interface & Tool Creation] - Completed
- [x] Build a Python module to parse and load the JSON data files.
- [x] Create Python functions to query specific data (e.g., `search_logs(service_name, time_range)`, `get_service_dependencies(service)`).
- [x] Wrap these functions into LLM-compatible tools (using LangChain or direct function calling).

### [Phase 3: Agent Orchestration] - Completed
- [x] Define the System Prompt and Persona (Expert SRE / Incident Commander).
- [x] Implement the core agent loop using an LLM (OpenAI/Gemini).
- [x] Develop a CLI or simple interface to trigger the agent with a simulated alert.

### [Phase 4: Testing & Refinement] - Completed
- [x] Run the agent against a simulated active incident.
- [x] Evaluate the accuracy of the root cause analysis and remediation suggestions based on the provided data.
- [x] Refine prompts and tool logic to improve diagnostic accuracy.

### [Phase 5: Director Feedback & Refactoring] - Completed
- [x] Re-architected system prompt to enforce strict, visible **Hypothesis Resolution** before conclusions.
- [x] Eliminated all fabricated data and static lookups; agent now dynamically correlates real metrics, logs, and historical postmortems.
- [x] Enhanced **Auto-Remediator** to dynamically extract target services from the AI's unstructured text rather than relying on brittle fallbacks.
- [x] **Model Context Protocol (MCP)**: Decoupled the tool architecture by implementing a standalone `FastMCP` server, creating a highly modular and secure client-server abstraction layer for all telemetry data.

## Setup & Execution

### 1. Requirements
Ensure you have Python 3.10+ installed. This project uses `gemini-2.5-pro` (the absolute state-of-the-art model) so you will need a `.env` file containing your `GEMINI_API_KEY`.

### 2. Installation
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Running the AI Incident Commander Dashboard
To provide a premium experience, this project includes a **Web UI Dashboard** with an **Auto-Remediation Engine**.

1. Start the FastAPI backend server:
```bash
python src/api.py
```
2. Open your browser and navigate to: [http://localhost:8000](http://localhost:8000)
3. Use the dropdown menu to select between the **4 distinct production incidents** (as requested in the challenge deliverables).
4. Click "Initialize Investigation" to watch the LangGraph agent autonomously pull context from its tools, generate a Markdown report, and trigger the Auto-Remediator to simulate fixes!
