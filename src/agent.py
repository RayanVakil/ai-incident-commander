import os
import json
from dotenv import load_dotenv
from typing import List, Dict, Any

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import Tool
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent

# Import our custom data loader
from data_loader import ShopFabricDataLoader

# Load environment variables (e.g., GEMINI_API_KEY)
load_dotenv()

class IncidentCommanderAgent:
    """
    AI Agent that acts as a Production Incident Commander.
    It uses LangChain and Gemini to query system telemetry and historical data
    to diagnose incidents and recommend remediation steps.
    """
    
    def __init__(self):
        # 1. Initialize our data source
        self.data_loader = ShopFabricDataLoader()
        
        # 2. Define the LLM (Gemini 1.5 Pro or similar available via the API key)
        # Make sure you have set GEMINI_API_KEY in your .env file
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables. Please check your .env file.")
            
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            temperature=0.2, # Low temperature for more analytical/deterministic responses
            max_output_tokens=2048
        )
        
        # 3. Create Tools for the Agent
        # These tools wrap our Python functions so the LLM knows how and when to call them.
        self.tools = [
            Tool(
                name="Get_Service_Architecture",
                func=self._tool_get_service_architecture,
                description="Use this to look up a service's dependencies, owners, language, and tier. Input should be the exact service name (e.g., 'checkout-service')."
            ),
            Tool(
                name="Get_Active_Alerts",
                func=self._tool_get_active_alerts,
                description="Use this to check for active system alerts. Input can be 'CRITICAL' to filter, or 'ALL' to see all alerts."
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
            )
        ]
        
        # 4. Set up the Agent's Persona and Prompt
        system_message = """
        You are an Expert Site Reliability Engineer (SRE) and Production Incident Commander for the ShopFabric e-commerce platform.
        Your goal is to rapidly diagnose production incidents, identify the root cause, and propose remediation steps.
        
        Always follow this process:
        1. Check active alerts to see what is failing.
        2. Look up the architecture of the failing service to understand its dependencies.
        3. Check recent deployments to rule out bad code pushes.
        4. Search historical incidents to see if this is a known failure pattern.
        
        Provide a structured Incident Report at the end containing:
        - **Incident Summary**: What is happening and the business impact.
        - **Root Cause**: What technical component failed.
        - **Immediate Remediation**: Steps to stabilize the system right now.
        - **Prevention**: Long-term fixes to prevent recurrence.
        """
        
        # Initialize the LangGraph Agent (the modern LangChain v0.3 standard)
        self.agent_executor = create_react_agent(
            self.llm, 
            tools=self.tools,
            prompt=system_message
        )

    # --- Tool Wrapper Functions ---
    # These functions parse the LLM's string input and return a string output
    
    def _tool_get_service_architecture(self, query: str) -> str:
        service_name = query.strip()
        data = self.data_loader.get_service_architecture(service_name)
        return json.dumps(data, indent=2)
        
    def _tool_get_active_alerts(self, query: str) -> str:
        severity = query.strip().upper()
        if severity == 'ALL' or severity == '':
            severity = None
        data = self.data_loader.get_active_alerts(severity)
        return json.dumps(data, indent=2)
        
    def _tool_search_historical_incidents(self, query: str) -> str:
        pattern = query.strip()
        data = self.data_loader.search_historical_incidents(pattern)
        # Limit to top 3 to avoid exceeding token limits
        return json.dumps(data[:3], indent=2)
        
    def _tool_get_recent_deployments(self, query: str) -> str:
        service_name = query.strip()
        data = self.data_loader.get_recent_deployments(service_name)
        return json.dumps(data, indent=2)

    # --- Main Execution Loop ---
    
    def investigate(self, alert_message: str):
        """Triggers the agent to investigate an alert."""
        print(f"\n[INCIDENT COMMANDER ACTIVATED] Investigating alert: {alert_message}\n")
        response = self.agent_executor.invoke({"messages": [("user", alert_message)]})
        raw_content = response["messages"][-1].content
        if isinstance(raw_content, list):
            report = "\n".join(block.get("text", "") for block in raw_content if block.get("type") == "text")
        else:
            report = raw_content
            
        print(report)
        return report

# Test execution (will only run if this script is executed directly)
if __name__ == "__main__":
    commander = IncidentCommanderAgent()
    # Simulate an incoming PagerDuty alert
    simulated_alert = "PagerDuty Alert: checkout-service latency has spiked and payment authorizations are failing. Investigate immediately."
    commander.investigate(simulated_alert)
