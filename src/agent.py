import os
import json
import asyncio
from dotenv import load_dotenv
from typing import List, Dict, Any
from pydantic import create_model, Field

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import StructuredTool
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage
from langgraph.prebuilt import create_react_agent

from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

# Load environment variables (e.g., GEMINI_API_KEY)
load_dotenv()

class IncidentCommanderAgent:
    """
    The IncidentCommanderAgent is a LangGraph-based ReAct agent designed to 
    autonomously investigate production incidents. It uses an MCP client to dynamically 
    pull telemetry data, form hypotheses, and generate a final root cause report.
    """
    
    def __init__(self):
        # 1. Define the LLM
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables. Please check your .env file.")
            
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            temperature=0.2, # Low temperature for more analytical/deterministic responses
            max_output_tokens=2048
        )
        
        # 2. Set up the Agent's Persona and Prompt
        self.system_message = """
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

    async def investigate(self, alert_message: str):
        """Triggers the agent to investigate an alert using MCP tools and captures its thought process."""
        print(f"\n[INCIDENT COMMANDER ACTIVATED] Investigating alert: {alert_message}\n")
        
        thought_process = []
        final_report = ""
        
        # Determine path to mcp_server.py
        server_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_server.py")
        
        # Set up MCP client to connect to our local server
        server_params = StdioServerParameters(
            command="python",
            args=[server_script]
        )

        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize the MCP session
                    await session.initialize()
                    
                    # Fetch available tools from the MCP server
                    mcp_tools_response = await session.list_tools()
                    
                    langchain_tools = []
                    for tool in mcp_tools_response.tools:
                        # Build a dynamic tool wrapper that forwards all arguments to the MCP server
                        def create_async_tool(tool_name):
                            async def mcp_tool_call(**kwargs) -> str:
                                result = await session.call_tool(tool_name, kwargs)
                                if result.isError:
                                    return f"Error: {result.content}"
                                return result.content[0].text if result.content else ""
                            return mcp_tool_call

                        # Build a Pydantic model from the MCP tool's input schema
                        # so LangGraph knows the exact parameter names and types
                        tool_schema = tool.inputSchema or {}
                        schema_props = tool_schema.get("properties", {})
                        required_fields = tool_schema.get("required", [])

                        # Dynamically create field annotations for the StructuredTool
                        field_definitions = {}
                        for prop_name, prop_info in schema_props.items():
                            prop_type = str  # MCP tools in this project all use string params
                            default = ... if prop_name in required_fields else ""
                            description = prop_info.get("description", "")
                            field_definitions[prop_name] = (prop_type, Field(default=default, description=description))
                        
                        args_schema = create_model(f"{tool.name}_Schema", **field_definitions)

                        langchain_tools.append(
                            StructuredTool.from_function(
                                coroutine=create_async_tool(tool.name),
                                name=tool.name,
                                description=tool.description,
                                args_schema=args_schema
                            )
                        )

                    # Initialize the LangGraph Agent with dynamically loaded MCP tools
                    agent_executor = create_react_agent(
                        self.llm, 
                        tools=langchain_tools,
                        prompt=self.system_message
                    )

                    # Execute the investigation via streaming to capture intermediate steps
                    events = agent_executor.astream({"messages": [("user", alert_message)]}, stream_mode="values")
                    
                    async for event in events:
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
                            content = last_message.content
                            if len(content) > 500:
                                content = content[:500] + "... [truncated]"
                            thought_process.append(f"TOOL RESULT ({last_message.name}): {content}")
                            
                        # If it's a final text response
                        if isinstance(last_message, AIMessage) and last_message.content and not last_message.tool_calls:
                            raw_content = last_message.content
                            if isinstance(raw_content, list):
                                final_report = "\n".join(block.get("text", "") for block in raw_content if block.get("type") == "text")
                            else:
                                final_report = raw_content
        except Exception as e:
            print(f"Error during MCP communication: {e}")
            raise

        print(final_report)
        return {
            "report": final_report,
            "thought_process": thought_process
        }

# Test execution (will only run if this script is executed directly)
if __name__ == "__main__":
    commander = IncidentCommanderAgent()
    simulated_alert = "Checkout success rate dropped from 95% to 40%. Investigate."
    
    # Run the async loop
    result = asyncio.run(commander.investigate(simulated_alert))
    
    print("\n--- Thought Process ---")
    for step in result["thought_process"]:
        print(step)
