# AI Agent Engineering Challenge - Design Document
**Project**: Production Incident Commander  
**Author**: Ray Vakil

## 1. Agent Architecture
The Incident Commander is built on top of **LangGraph**, utilizing the **ReAct (Reason + Act)** framework. The core LLM driving the reasoning engine is **Gemini 2.5 Pro**, configured with a low temperature (`0.2`) to ensure highly analytical, deterministic, and evidence-based outputs.

LangGraph was chosen over a standard LangChain `AgentExecutor` or standard API calls because it inherently supports cyclical, multi-step reasoning loops. It allows the agent to:
- Formulate an execution plan
- Call a tool to gather evidence
- Observe the output
- *Critique* its current hypothesis
- Either conclude or call another tool to gather more evidence

This architecture satisfies the requirement for the agent to maintain multiple competing hypotheses until sufficient evidence is gathered to eliminate them.

## 2. Tool Architecture
To satisfy the constraint that data must not be loaded into a single prompt, a bespoke `ShopFabricDataLoader` class was built to act as the abstraction layer over the raw JSON telemetry datasets. 

These data loader methods are wrapped into LangChain `Tool` objects and provided to the agent:
- `Get_Service_Architecture`: Queries `architecture_overview.json` and `service_dependencies.json` to map out dependencies.
- `Get_Active_Alerts`: Queries `alerts.json`.
- `Get_Recent_Deployments`: Queries `deployments.json` to check for recent code pushes.
- `Search_Logs`: Queries `logs.json` for specific services and supports logical `OR` parsing (e.g. `error OR deadlock`) to simulate real logging backends like Splunk/Datadog.
- `Get_Service_Metrics`: Queries `metrics.json` for CPU, memory, and latency metrics.
- `Search_Customer_Reports`: Queries `customer_reports.json`.
- `Get_Runbook` / `Get_Postmortems`: Pulls relevant documentation based on service or error patterns.

This comprehensive tool suite allows the agent to dynamically query the environment exactly like a human SRE would, pulling only the necessary context into its context window on an on-demand basis.

## 3. Investigation Workflow & Planning Strategy
The agent is explicitly instructed via its System Prompt to follow a strict, dynamic diagnostic methodology rather than relying on predefined lookups:
1. **Hypothesize**: Read the incoming alert to identify the failing component and form an initial theory.
2. **Gather Evidence**: Dynamically invoke tools (`Get_Active_Alerts`, `Get_Service_Metrics`) to validate or invalidate the theory.
3. **Correlate Data**: Map dependencies (`Get_Service_Architecture`) and cross-reference metrics with actual logs (`Search_Logs`).
4. **Historical Context**: Pull `Search_Historical_Incidents` or `Get_Postmortems` to correlate current symptoms with known past failure modes.
5. **Conclude**: Generate a final structured Markdown report detailing Root Cause, Confidence, Evidence, and Remediation.

## 4. Reasoning Approach
The agent employs a **Hypothesis-Driven** reasoning approach. For example, if checkout is failing, it does not immediately assume the checkout-service is broken. It gathers evidence:
- *Are downstream payment services failing?*
- *Is the database saturated?*
- *Did a recent deployment introduce a bug?*

By pulling historical postmortems, the agent can correlate symptoms (e.g., `HikariPool timeout`) with known root causes (e.g., Database connection pool exhaustion), dramatically increasing diagnostic accuracy and confidence.

## 5. Automated Remediation Engine (Bonus Feature)
As a "Bonus Feature", this project includes an **Auto-Remediator** module. Once the LangGraph agent produces its Markdown-formatted diagnosis, the Auto-Remediator parses the report for specific, actionable Kubernetes mitigation steps. 
It simulates executing `kubectl` commands (like scaling up deployments or patching config maps) to close the loop on the incident entirely autonomously.

## 6. Limitations
- **Read-Only Telemetry**: Currently, the abstraction layer is built over static JSON files. In a true production environment, these tools would be swapped out with API calls to Datadog, PagerDuty, and Kubernetes.
- **Synchronous Execution**: The agent investigates sequentially. A future enhancement could utilize a multi-agent architecture where a "Triage Agent" delegates log scraping to parallel worker subagents to speed up the investigation.
