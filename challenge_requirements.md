# AI Agent Engineering Challenge – Production Incident Commander

## Overview
Modern production incidents require engineers to gather information from multiple systems, correlate evidence, form hypotheses, validate findings, and coordinate remediation efforts.
The objective of this challenge is to build an AI-powered Incident Commander capable of investigating production incidents and generating evidence-based recommendations.
This challenge is intended to evaluate:
* Agent design
* Planning and reasoning
* Tool orchestration
* Multi-step workflows
* Context management
* LLM utilization
* Software engineering practices
The focus is not UI development. The focus is on how the agent thinks, plans, investigates, and arrives at conclusions.

## Problem Statement
You are responsible for operating a large e-commerce platform consisting of multiple microservices.
Users are reporting issues such as:
* Checkout failures
* Slow page loads
* Order processing delays
* Payment failures
* Inventory inconsistencies
Your task is to build an AI Incident Commander that can investigate incidents and provide:
* Root cause hypotheses
* Supporting evidence
* Impact assessment
* Recommended remediation actions
* Confidence score
* Incident summary
The assistant should behave like a senior Site Reliability Engineer (SRE) or Incident Commander investigating production issues.

## Dataset
You will be provided with a folder containing operational data.
Example:
`data/`
- `architecture_overview.json`
- `service_dependencies.json`
- `metrics.json`
- `logs.json`
- `deployments.json`
- `incidents.json`
- `postmortems.json`
- `runbooks.json`
- `alerts.json`
- `customer_reports.json`

The datasets simulate information available to production engineering teams.
Some incidents may require correlating information across multiple datasets. The correct answer should not be obtainable from a single file.

## Tool Integration Requirement
The provided datasets should not be loaded directly into a single LLM prompt.
Your solution should expose them through a tool abstraction layer and allow the agent to retrieve information as needed during an investigation.
Example interfaces:
- `search_logs(service_name, query)`
- `get_service_metrics(service_name)`
- `get_recent_deployments(service_name)`
- `get_service_dependencies(service_name)`
- `search_past_incidents(query)`
- `get_runbook(service_name)`
- `get_alerts(service_name)`
- `search_customer_reports(query)`

You may implement the tool layer using:
* MCP
* Agent frameworks
* Any equivalent mechanism
The choice of technology is entirely up to you.
The focus of the evaluation is not the framework used, but how effectively the agent plans investigations, gathers evidence, and arrives at conclusions.

## Example Incident Requests
**Example 1**: "Checkout success rate dropped from 95% to 40%. Investigate."
**Example 2**: "Inventory overselling occurred during a flash sale. Analyze the likely cause."
**Example 3**: "Payment latency increased by 300%. Determine what changed."
**Example 4**: "Customer complaints regarding slow checkout have increased significantly over the last two hours. Investigate."

## Expected Agent Behavior
The assistant should not immediately provide an answer.
Instead, it should:
1. Form an investigation plan.
2. Identify required information.
3. Gather evidence using tools.
4. Generate multiple competing hypotheses.
5. Validate hypotheses using evidence.
6. Eliminate unlikely causes.
7. Correlate findings across systems.
8. Generate conclusions and recommendations.

Example workflow:
Incident -> Plan Investigation -> Gather Metrics -> Review Alerts -> Review Deployments -> Analyze Logs -> Check Service Dependencies -> Search Historical Incidents -> Consult Runbooks -> Validate Hypotheses -> Generate Findings -> Recommend Actions

## Hypothesis-Driven Investigation
A strong investigation should maintain multiple possible explanations until sufficient evidence is collected.
Example:
- Hypothesis 1: Recent deployment introduced a regression.
- Hypothesis 2: External payment provider degradation.
- Hypothesis 3: Database connection pool exhaustion.
- Hypothesis 4: Redis failover causing latency.

The agent should gather evidence to either strengthen or eliminate each hypothesis before arriving at a final conclusion.
Jumping directly to a root cause without evidence is discouraged.

## Historical Knowledge Utilization
The provided historical incidents, postmortems, and runbooks represent organizational knowledge accumulated from previous production issues.
The assistant should leverage this information to:
* Identify similar incidents
* Recognize recurring patterns
* Accelerate investigations
* Validate potential root causes
* Recommend proven mitigation strategies
The agent should explain when historical incidents influenced its reasoning.

## Explainability Requirements
All findings should include:
* Supporting evidence
* Relevant metrics
* Relevant log excerpts
* Related historical incidents (if applicable)
* Confidence level
* Reasoning summary

## Deliverables
1. **Working Prototype**: Any technology stack is acceptable.
2. **Design Document**: Describe Agent architecture, Tool architecture, Planning strategy, Investigation workflow, Reasoning approach, Limitations. Explain why specific design decisions were made.
3. **Demonstration**: Demonstrate at least three incident investigations. Show the investigation plan, evidence gathered, hypotheses considered, final conclusion, and recommended actions.

## Bonus Features
Optional enhancements:
* Planner / Executor architecture
* Reflection or critique step
* Human approval workflow
* MCP integration
* Memory across investigations
* Multi-agent design
* Incident timeline reconstruction
* Root-cause confidence scoring

## Evaluation Criteria
| Category | Weight |
|---|---|
| Agent Design | 20% |
| Investigation Strategy | 20% |
| Tool Usage & Orchestration | 20% |
| Hypothesis Generation & Validation | 15% |
| Root Cause Analysis Quality | 15% |
| Explainability & Evidence | 10% |

## What We Are Looking For
**Strong solutions typically:**
* Plan before acting
* Gather evidence incrementally
* Use tools strategically
* Maintain multiple hypotheses
* Validate assumptions with evidence
* Correlate information across datasets
* Leverage historical incidents and runbooks
* Explain reasoning clearly
* Produce actionable recommendations

**Weak solutions typically:**
* Load all data into a single prompt
* Jump directly to conclusions
* Ignore contradictory evidence
* Fail to explain reasoning
* Rely on a single source of information

We are less interested in UI polish and more interested in the quality of the investigation workflow, reasoning process, and agent behavior.

---

## Director's Feedback (Rejection Notice)

Hi Ray,

Thank you for sharing the implementation.

After reviewing the solution, I don't think it is fully aligned with what we were expecting from this exercise.

The intent of the challenge is to evaluate the overall agent design, investigation workflow, planning, reasoning, dynamic evidence gathering, and hypothesis-driven investigation rather than implementing a simple set of tool lookups around the datasets.

Some of the areas that need improvement are:
- The agent should investigate dynamically instead of relying on a few predefined lookups.
- The investigation should be hypothesis-driven, where multiple possible causes are considered and validated using evidence before arriving at a conclusion.
- The available datasets (metrics, logs, deployments, alerts, customer reports, runbooks, postmortems, dependencies, etc.) should be exposed through a proper tool abstraction and retrieved on demand during the investigation.
- The agent should correlate information across multiple data sources rather than relying primarily on keyword searches or individual dataset lookups.
- The reasoning process should be visible, including investigation planning, evidence collection, hypothesis validation, and final recommendations with supporting evidence.

The challenge document shared earlier already outlines the expected behavior, deliverables, and evaluation criteria. I'm attaching it again here for easy reference. Please review it carefully and align the implementation with the expectations described in the document.

Once you've revisited the design, please update the implementation and share it back for review
