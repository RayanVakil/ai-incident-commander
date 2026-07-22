# AI Agent Engineering Challenge - Design Document
**Project**: Production Incident Commander  
**Author**: Ray Vakil

## 1. Agent Architecture
The Incident Commander is built on top of **LangGraph**, utilizing the **ReAct (Reason + Act)** framework. The core LLM driving the reasoning engine is **Gemini 2.5 Pro**, configured with a low temperature (`0.2`) to ensure highly analytical, deterministic, and evidence-based outputs.

**Why LangGraph over LangChain AgentExecutor?**
LangGraph was chosen over a standard LangChain `AgentExecutor` or raw API calls because production incidents require stateful, cyclical, multi-step reasoning. `AgentExecutor` is largely a black-box that is difficult to audit and extend, whereas LangGraph models the agent as a state machine. This allows the agent to formulate an execution plan, call a tool, observe the output, *critique* its current hypothesis, and loop back iteratively until the root cause is confirmed.

**Why ReAct over Plan-and-Execute?**
While a Plan-and-Execute architecture is excellent for long-horizon tasks, incident response is highly dynamic. An initial plan ("I will check the database") might instantly become obsolete if the first tool call reveals a network partition. The ReAct (Reason + Act) pattern allows the agent to pivot its investigation strategy immediately after every observation, which is crucial for minimizing MTTR (Mean Time to Resolution).

**Why Gemini 2.5 Pro?**
Gemini 2.5 Pro was selected for its exceptional needle-in-a-haystack retrieval capabilities and massive context window (up to 2M tokens). When parsing through concatenated tool results containing hundreds of log lines and metric points, Gemini 2.5 Pro maintains high recall, ensuring it doesn't suffer from the "lost in the middle" phenomenon that plagues other models during intense data analysis.

## 2. Trade-offs Considered: Memory vs. Vector Store
To satisfy the constraint that data must not be loaded into a single prompt, a bespoke `ShopFabricDataLoader` class was built to act as the abstraction layer over the raw JSON telemetry datasets. 

A significant trade-off was deciding whether to load the static JSON into memory or ingest it into a Vector Database (like ChromaDB) for RAG (Retrieval-Augmented Generation). 
- **The decision:** For the scope of this simulation (~5.5MB of logs), loading the data into memory and using Python-based keyword search (with boolean OR logic) was chosen for simplicity, determinism, and speed. 
- **The trade-off:** Keyword search lacks semantic understanding (e.g., matching "sluggish" to "latency"). In a true production environment scaling to gigabytes of telemetry, pushing logs and runbooks to a Vector DB or directly querying Elasticsearch/Splunk via APIs would be strictly necessary.

## 3. Tool Architecture & Model Context Protocol (MCP)
To build a highly decoupled, scalable system, the data access layer was implemented using the **Model Context Protocol (MCP)** via a standalone `FastMCP` server. Instead of coupling data loaders directly into the agent's logic, the MCP server securely exposes telemetry APIs over `stdio`. The LangGraph agent acts as an MCP client, dynamically discovering and converting these schemas into LangChain `Tool` objects on initialization.

The MCP server exposes the following capabilities:
- `Get_Service_Architecture`: Queries `architecture_overview.json` and `service_dependencies.json` to map out dependencies.
- `Get_Active_Alerts`: Queries `alerts.json`.
- `Get_Recent_Deployments`: Queries `deployments.json` to check for recent code pushes.
- `Search_Logs`: Queries `logs.json` for specific services and supports logical `OR` parsing (e.g. `error OR deadlock`) to simulate real logging backends like Splunk/Datadog.
- `Get_Service_Metrics`: Queries `metrics.json` for CPU, memory, and latency metrics.
- `Search_Customer_Reports`: Queries `customer_reports.json`.
- `Get_Runbook` / `Get_Postmortems`: Pulls relevant documentation based on service or error patterns.

This comprehensive tool suite allows the agent to dynamically query the environment exactly like a human SRE would, pulling only the necessary context into its context window on an on-demand basis.

## 4. Investigation Workflow & Planning Strategy
The agent is explicitly instructed via its System Prompt to follow a strict, dynamic diagnostic methodology rather than relying on predefined lookups:
1. **Hypothesize**: Read the incoming alert to identify the failing component and form an initial theory.
2. **Gather Evidence**: Dynamically invoke tools (`Get_Active_Alerts`, `Get_Service_Metrics`) to validate or invalidate the theory.
3. **Correlate Data**: Map dependencies (`Get_Service_Architecture`) and cross-reference metrics with actual logs (`Search_Logs`).
4. **Historical Context**: Pull `Search_Historical_Incidents` or `Get_Postmortems` to correlate current symptoms with known past failure modes.
5. **Hypothesis Resolution**: Explicitly list all considered hypotheses, state whether they were confirmed or eliminated, and cite the exact evidence used to make that determination.
6. **Conclude**: Generate a final structured Markdown report detailing Root Cause, Confidence, Evidence, and Remediation.

## 5. Reasoning Approach
The agent employs a **Hypothesis-Driven** reasoning approach. For example, if checkout is failing, it does not immediately assume the checkout-service is broken. It gathers evidence:
- *Are downstream payment services failing?*
- *Is the database saturated?*
- *Did a recent deployment introduce a bug?*

By pulling historical postmortems, the agent can correlate symptoms (e.g., `HikariPool timeout`) with known root causes (e.g., Database connection pool exhaustion), dramatically increasing diagnostic accuracy and confidence.

## 6. Automated Remediation Engine (Bonus Feature)
As a "Bonus Feature", this project includes an **Auto-Remediator** module. Once the LangGraph agent produces its Markdown-formatted diagnosis, the Auto-Remediator parses the report for specific, actionable Kubernetes mitigation steps. 
It dynamically extracts the name of the failing service from the AI's unstructured text and simulates executing `kubectl` commands (like scaling up deployments or patching config maps) against that specific service to close the loop on the incident entirely autonomously.

## 7. Limitations & Future Work
- **Read-Only Telemetry**: Currently, the MCP server exposes static JSON files. In a true production environment, the MCP tools would be swapped to hit live APIs (Datadog, PagerDuty, Splunk, Kubernetes) — the decoupled MCP architecture makes this a drop-in replacement with zero changes to the agent client.
- **Single-Agent Architecture**: While the agent now runs fully asynchronously via `asyncio`, it still operates as a single reasoning loop. A future enhancement could utilize a multi-agent architecture where a "Triage Agent" delegates log scraping to parallel MCP-connected worker subagents.
