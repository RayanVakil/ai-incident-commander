# Production Incident Commander - AI Agent

## Overview
This repository contains the implementation of an AI-powered "Production Incident Commander." The goal of this agent is to assist Site Reliability Engineers (SREs) by automatically ingesting, analyzing, and synthesizing telemetry data (logs, metrics, alerts, and historical incidents) to diagnose production issues and recommend remediation steps.

The agent operates against a simulated e-commerce microservices environment ("ShopFabric") and uses a large language model equipped with tools to query system state and historical context.

## Project Status & Log

We are documenting our development progress here step-by-step so reviewers can follow our thought process and implementation strategy.

### [Phase 1: Project Setup & Discovery] - In Progress
- [x] Initialized the project directory.
- [x] Analyzed the provided dataset (`architecture_overview.json`, `incidents.json`, etc.) to understand the ShopFabric topology and historical failure modes.
- [x] Drafted initial project strategy and architecture for the AI Agent.
- [ ] Initialize Git repository and `.gitignore`.
- [ ] Set up Python virtual environment and `requirements.txt`.

### [Phase 2: Data Interface & Tool Creation] - Pending
- [ ] Build a Python module to parse and load the JSON data files.
- [ ] Create Python functions to query specific data (e.g., `search_logs(service_name, time_range)`, `get_service_dependencies(service)`).
- [ ] Wrap these functions into LLM-compatible tools (using LangChain or direct function calling).

### [Phase 3: Agent Orchestration] - Pending
- [ ] Define the System Prompt and Persona (Expert SRE / Incident Commander).
- [ ] Implement the core agent loop using an LLM (OpenAI/Gemini).
- [ ] Develop a CLI or simple interface to trigger the agent with a simulated alert.

### [Phase 4: Testing & Refinement] - Pending
- [ ] Run the agent against a simulated active incident.
- [ ] Evaluate the accuracy of the root cause analysis and remediation suggestions based on the provided data.
- [ ] Refine prompts and tool logic to improve diagnostic accuracy.

## How to Run (Placeholder)
*(Instructions on how to execute the code will be added here once implementation is complete.)*
