# AI Agent Engineering Challenge – Production Incident Commander

## Overview
Modern production incidents require engineers to gather information from multiple systems, correlate evidence, form hypotheses, validate findings, and coordinate remediation efforts.
The objective of this challenge is to build an AI-powered Incident Commander capable of investigating production incidents and generating evidence-based recommendations.

This challenge is intended to evaluate:
- Agent design
- Planning and reasoning
- Tool orchestration
- Multi-step workflows
- Context management
- LLM utilization
- Software engineering practices

**The focus is not UI development. The focus is on how the agent thinks, plans, investigates, and arrives at conclusions.**

## Problem Statement
You are responsible for operating a large e-commerce platform consisting of multiple microservices.
Users are reporting issues such as Checkout failures, Slow page loads, Order processing delays, Payment failures, Inventory inconsistencies.

Your task is to build an AI Incident Commander that can investigate incidents and provide:
- Root cause hypotheses
- Supporting evidence
- Impact assessment
- Recommended remediation actions
- Confidence score
- Incident summary

The assistant should behave like a senior Site Reliability Engineer (SRE) or Incident Commander investigating production issues.

## Dataset
You will be provided with a folder containing operational data (`architecture_overview.json`, `service_dependencies.json`, `metrics.json`, `logs.json`, etc.)
The datasets simulate information available to production engineering teams. Some incidents may require correlating information across multiple datasets. The correct answer should not be obtainable from a single file.

## Tool Integration Requirement
The provided datasets should not be loaded directly into a single LLM prompt. Your solution should expose them through a tool abstraction layer and allow the agent to retrieve information as needed during an investigation.
Examples: `search_logs`, `get_service_metrics`, `search_past_incidents`, etc.
The choice of technology is entirely up to you (FastAPI, LangGraph, etc.).

## Expected Agent Behavior
The assistant should not immediately provide an answer. Instead, it should:
- Form an investigation plan.
- Identify required information.
- Gather evidence using tools.
- Generate multiple competing hypotheses.
- Validate hypotheses using evidence.
- Eliminate unlikely causes.
- Correlate findings across systems.
- Generate conclusions and recommendations.

## Deliverables
1. **Working Prototype**: Any technology stack is acceptable (e.g. FastAPI, LangGraph).
2. **Design Document**: Describe Agent architecture, Tool architecture, Planning strategy, Investigation workflow, Reasoning approach, Limitations. Explain why specific design decisions were made.
3. **Demonstration**: Demonstrate at least three incident investigations. Show the investigation plan, evidence gathered, hypotheses considered, final conclusion, and recommended actions for each.

## Bonus Features
Optional enhancements: Planner / Executor architecture, Reflection or critique step, Human approval workflow, MCP integration, Memory across investigations, Multi-agent design, Incident timeline reconstruction, Root-cause confidence scoring.
