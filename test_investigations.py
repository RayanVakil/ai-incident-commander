import asyncio
import sys
import os
import unittest

# Add src to the path so we can import the agent
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from agent import IncidentCommanderAgent

class TestIncidentCommander(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        # We initialize one agent to reuse across tests
        cls.commander = IncidentCommanderAgent()

    async def _run_and_validate_investigation(self, alert_message: str):
        print(f"\n[TEST] Starting investigation for: {alert_message}")
        result = await self.commander.investigate(alert_message)
        
        report = result.get("report", "").lower()
        thought_process = result.get("thought_process", [])
        
        # 1. Validate Tool Orchestration Requirements
        # Challenge requires agent to gather evidence using tools.
        tool_calls = [step for step in thought_process if "AGENT ACTION: Invoking" in step]
        self.assertGreater(len(tool_calls), 0, "Agent failed to orchestrate tools. No tools were invoked.")

        # 2. Validate Hypothesis-Driven Investigation Requirements
        # Challenge requires multiple hypotheses that are confirmed or eliminated.
        self.assertIn("hypothesis", report, "Report is missing hypothesis generation.")
        self.assertTrue("confirmed" in report or "eliminated" in report, "Report failed to confirm or eliminate hypotheses.")

        # 3. Validate Explainability Requirements
        # Challenge requires: Supporting evidence, Confidence level, Recommendations/Remediation, Summary
        self.assertIn("confidence score", report, "Report is missing the required Confidence Score.")
        self.assertIn("supporting evidence", report, "Report is missing the Supporting Evidence section.")
        self.assertIn("incident summary", report, "Report is missing the Incident Summary section.")
        
        # Check for remediation/prevention logic
        self.assertTrue(
            "remediation" in report or "prevention" in report, 
            "Report is missing actionable remediation or prevention recommendations."
        )

        print(f"[TEST PASS] Successfully validated challenge requirements for alert: {alert_message}")
        return result

    async def test_example_1_checkout_drop(self):
        await self._run_and_validate_investigation("Checkout success rate dropped from 95% to 40%. Investigate.")

    async def test_example_2_inventory_overselling(self):
        await self._run_and_validate_investigation("Inventory overselling occurred during a flash sale. Analyze the likely cause.")

    async def test_example_3_payment_latency(self):
        await self._run_and_validate_investigation("Payment latency increased by 300%. Determine what changed.")

    async def test_example_4_customer_complaints(self):
        await self._run_and_validate_investigation("Customer complaints regarding slow checkout have increased significantly over the last two hours. Investigate.")

if __name__ == "__main__":
    print("Starting automated tests for AI Incident Commander with MCP Server...")
    # Run tests sequentially
    unittest.main(verbosity=2)
