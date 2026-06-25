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
- `Get_Service_Architecture`: Queries `architecture_overview.json` and `service_dependencies.json`.
- `Get_Active_Alerts`: Queries `alerts.json`.
- `Get_Recent_Deployments`: Queries `deployments.json`.
- `Search_Historical_Incidents`: Queries `incidents.json`, `postmortems.json`, and `runbooks.json`.

This allows the agent to dynamically query the environment exactly like a human SRE would, pulling only the necessary context into its context window at any given time.

## 3. Investigation Workflow & Planning Strategy
The agent is explicitly instructed via its System Prompt to follow a strict diagnostic methodology:
1. **Plan & Triage**: Read the incoming alert to identify the failing component.
2. **Gather Alert Context**: Call `Get_Active_Alerts` to see if there are correlating failures across the stack.
3. **Map Dependencies**: Call `Get_Service_Architecture` to understand upstream/downstream impact.
4. **Rule out Regressions**: Call `Get_Recent_Deployments` to check if a bad code push caused the issue.
5. **Leverage Organizational Knowledge**: Call `Search_Historical_Incidents` to see if this failure pattern is a known issue (e.g., connection pool exhaustion) and identify proven mitigation strategies.
6. **Conclude**: Generate a final report detailing Root Cause, Confidence, Evidence, and Remediation.

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
