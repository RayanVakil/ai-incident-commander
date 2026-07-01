import os
import json
from dotenv import load_dotenv
from typing import List, Dict, Any

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import Tool
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage
from langgraph.prebuilt import create_react_agent

# Import our custom data loader
from data_loader import ShopFabricDataLoader

# Load environment variables (e.g., GEMINI_API_KEY)
load_dotenv()

class IncidentCommanderAgent:
    """
    The IncidentCommanderAgent is a LangGraph-based ReAct agent designed to 
    autonomously investigate production incidents. It uses tools to dynamically 
    pull telemetry data, form hypotheses, and generate a final root cause report.
    """
    
    def __init__(self):
        # 1. Initialize our data source (the abstraction over raw JSON files)
        self.data_loader = ShopFabricDataLoader()
        
        # 2. Define the LLM
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables. Please check your .env file.")
            
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            temperature=0.2, # Low temperature for more analytical/deterministic responses
            max_output_tokens=2048
        )
        
        # Define the tools available to the LLM for gathering evidence
        self.tools = [
            Tool(
                name="Get_Service_Architecture",
                func=self._tool_get_service_architecture,
                description="Input: service name (e.g. 'checkout-service'). Returns its dependencies, databases, and owner team."
            ),
            Tool(
                name="Get_Active_Alerts",
                func=self._tool_get_active_alerts,
                description="Input: severity (e.g. 'CRITICAL' or 'ALL'). Returns active PagerDuty/Prometheus alerts."
            ),
            Tool(
                name="Search_Historical_Incidents",
                func=self._tool_search_historical_incidents,
                description="Use this to find past incidents to see how they were fixed. Input should be a service name or failure pattern (e.g., 'redis_outage' or 'payment-service')."
            ),
            Tool(
                name="Get_Recent_Deployments",
                func=self._tool_get_recent_deployments,
                description="Use this to check if a recent code deployment might have caused the issue. Input should be the service name."
            ),
            Tool(
                name="Get_Service_Metrics",
                func=self._tool_get_service_metrics,
                description="Use this to retrieve performance and health metrics for a specific service. Input should be the service name."
            ),
            Tool(
                name="Search_Logs",
                func=self._tool_search_logs,
                description="Use this to search logs for a specific service. Input should be a JSON string like {\"service\": \"checkout-service\", \"query\": \"error\"}."
            ),
            Tool(
                name="Search_Customer_Reports",
                func=self._tool_search_customer_reports,
                description="Use this to search recent customer reports for keywords. Input should be the keyword (e.g., 'checkout')."
            ),
            Tool(
                name="Get_Runbook",
                func=self._tool_get_runbook,
                description="Use this to retrieve the runbook (troubleshooting steps) for a specific service. Input should be the service name."
            ),
            Tool(
                name="Get_Postmortems",
                func=self._tool_get_postmortems,
                description="Use this to search past postmortems for lessons learned. Input should be a query string."
            ),
            Tool(
                name="Get_Service_Dependencies",
                func=self._tool_get_service_dependencies,
                description="Use this to retrieve upstream and downstream dependencies for a service. Input should be the service name."
            )
        ]
        
        # 4. Set up the Agent's Persona and Prompt
        system_message = """
        You are an Expert Site Reliability Engineer (SRE) and Production Incident Commander for the ShopFabric e-commerce platform.
        Your goal is to rapidly diagnose production incidents, identify the root cause, and propose remediation steps.
        
        CRITICAL INVESTIGATION WORKFLOW:
        You must investigate dynamically instead of relying on a predefined checklist. 
        - The investigation MUST be hypothesis-driven. Form multiple possible causes initially.
        - Actively validate or eliminate your hypotheses by retrieving evidence across multiple datasets (metrics, logs, alerts, deployments, customer reports).
        - Correlate information across these data sources to find the true root cause. Do not rely on a single source of truth.
        - Leverage historical incidents and runbooks to inform your reasoning and recommendations.
        
        Provide a structured Incident Report at the end containing:
        - **Incident Summary**: What is happening and the business impact.
        - **Root Cause**: What technical component failed, with a Confidence Score (e.g., 95%).
        - **Supporting Evidence**: Explicitly list the metrics, logs, or correlations that prove your hypothesis.
        - **Immediate Remediation**: Actionable steps to stabilize the system right now.
        - **Prevention**: Long-term fixes to prevent recurrence.
        
        REFLECTION STEP:
        Before writing your final Incident Report, you MUST include a "Hypothesis Resolution" section where you explicitly list the hypotheses you considered and whether they are confirmed or eliminated. 
        Your output MUST strictly start with this exact markdown format:
        
        # Hypothesis Resolution
        1. [Hypothesis 1] - [CONFIRMED/ELIMINATED] - Evidence: [Your reasoning]
        2. [Hypothesis 2] - [CONFIRMED/ELIMINATED] - Evidence: [Your reasoning]
        ...
        
        # Incident Report
        [Your final report goes here...]
        
        CRITICAL RULES:
        1. When invoking tools, just invoke the tools. DO NOT output conversational filler like "Okay, I'm on it" or "Let's check the logs". 
        2. Once you have enough evidence, your final response must ONLY be the markdown Incident Report. Do not include any other text.
        3. Search tools only support SIMPLE substring matches or basic ' OR ' logic. Do NOT use complex boolean queries.
        """
        
        # Initialize the LangGraph Agent (the modern LangChain v0.3 standard)
        self.agent_executor = create_react_agent(
            self.llm, 
            tools=self.tools,
            prompt=system_message
        )

    # --- Tool Wrapper Functions ---
    def _tool_get_service_architecture(self, query: str) -> str:
        return json.dumps(self.data_loader.get_service_architecture(query.strip()), indent=2)
        
    def _tool_get_active_alerts(self, query: str) -> str:
        severity = query.strip().upper()
        if severity == 'ALL' or severity == '':
            severity = None
        return json.dumps(self.data_loader.get_active_alerts(severity), indent=2)
        
    def _tool_search_historical_incidents(self, query: str) -> str:
        return json.dumps(self.data_loader.search_historical_incidents(query.strip())[:3], indent=2)
        
    def _tool_get_recent_deployments(self, query: str) -> str:
        return json.dumps(self.data_loader.get_recent_deployments(query.strip()), indent=2)

    def _tool_get_service_metrics(self, query: str) -> str:
        return json.dumps(self.data_loader.get_service_metrics(query.strip()), indent=2)

    def _tool_search_logs(self, query: str) -> str:
        try:
            params = json.loads(query)
            service = params.get("service", "")
            q = params.get("query", "")
            return json.dumps(self.data_loader.search_logs(service, q), indent=2)
        except (json.JSONDecodeError, Exception) as e:
            # Fallback if the LLM doesn't pass JSON
            return json.dumps(self.data_loader.search_logs(query.strip()), indent=2)

    def _tool_search_customer_reports(self, query: str) -> str:
        return json.dumps(self.data_loader.search_customer_reports(query.strip()), indent=2)

    def _tool_get_runbook(self, query: str) -> str:
        return json.dumps(self.data_loader.get_runbook(query.strip()), indent=2)

    def _tool_get_postmortems(self, query: str) -> str:
        return json.dumps(self.data_loader.get_postmortems(query.strip()), indent=2)

    def _tool_get_service_dependencies(self, query: str) -> str:
        return json.dumps(self.data_loader.get_service_dependencies(query.strip()), indent=2)

    # --- Main Execution Loop ---
    
    def investigate(self, alert_message: str):
        """Triggers the agent to investigate an alert and captures its thought process."""
        print(f"\n[INCIDENT COMMANDER ACTIVATED] Investigating alert: {alert_message}\n")
        
        # We will capture the stream to get intermediate steps (Tool calls and Tool responses)
        thought_process = []
        final_report = ""

        # Using stream to capture intermediate events
        events = self.agent_executor.stream({"messages": [("user", alert_message)]}, stream_mode="values")
        
        for event in events:
            messages = event.get("messages", [])
            if not messages:
                continue
            
            last_message = messages[-1]
            
            # If the agent is calling tools
            if isinstance(last_message, AIMessage) and last_message.tool_calls:
                for tc in last_message.tool_calls:
                    tool_name = tc.get("name")
                    tool_args = tc.get("args")
                    thought_process.append(f"AGENT ACTION: Invoking '{tool_name}' with arguments: {tool_args}")
                    
            # If a tool is returning results
            elif isinstance(last_message, ToolMessage):
                # Truncate long responses for UI readability
                content = last_message.content
                if len(content) > 500:
                    content = content[:500] + "... [truncated]"
                thought_process.append(f"TOOL RESULT ({last_message.name}): {content}")
                
            # If it's a final text response (and not just empty text alongside a tool call)
            if isinstance(last_message, AIMessage) and last_message.content and not last_message.tool_calls:
                raw_content = last_message.content
                if isinstance(raw_content, list):
                    final_report = "\n".join(block.get("text", "") for block in raw_content if block.get("type") == "text")
                else:
                    final_report = raw_content

        print(final_report)
        return {
            "report": final_report,
            "thought_process": thought_process
        }

# Test execution (will only run if this script is executed directly)
if __name__ == "__main__":
    commander = IncidentCommanderAgent()
    simulated_alert = "Checkout success rate dropped from 95% to 40%. Investigate."
    result = commander.investigate(simulated_alert)
    print("\n--- Thought Process ---")
    for step in result["thought_process"]:
        print(step)
