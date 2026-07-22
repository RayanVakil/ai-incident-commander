import asyncio
import sys
import os

sys.path.append(os.path.join(os.getcwd(), "src"))
from agent import IncidentCommanderAgent

async def test():
    c = IncidentCommanderAgent()
    r = await c.investigate("Payment latency increased by 300%. Determine what changed.")
    report = r["report"].lower()
    steps = r["thought_process"]
    
    tool_calls = [s for s in steps if "AGENT ACTION" in s]
    print(f"Tools called: {len(tool_calls)}")
    for tc in tool_calls:
        print(f"  {tc}")
    
    checks = {
        "hypothesis": "hypothesis" in report,
        "confirmed/eliminated": "confirmed" in report or "eliminated" in report,
        "confidence": "confidence" in report,
        "evidence": "evidence" in report,
        "remediation": "remediation" in report or "prevention" in report,
    }
    print()
    for k, v in checks.items():
        status = "PASS" if v else "FAIL"
        print(f"[{status}] {k}")
    
    all_pass = all(checks.values()) and len(tool_calls) > 0
    result = "PASS" if all_pass else "FAIL"
    print(f"\nOVERALL: {result}")

asyncio.run(test())
