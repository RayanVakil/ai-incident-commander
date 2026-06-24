import re
import time

class AutoRemediator:
    """
    Parses the AI Incident Commander's report and simulates 
    executing the recommended remediation steps against the cluster.
    """
    
    def __init__(self):
        pass

    def execute_remediation(self, incident_report: str) -> list[str]:
        """
        Parses the report for key remediation steps and returns a list of 
        simulated commands/logs.
        """
        execution_logs = []
        execution_logs.append("[SYSTEM] Initiating Auto-Remediation based on AI Report...")
        time.sleep(0.5)

        # Look for keywords in the report to trigger simulated actions
        if "increase database connection pool" in incident_report.lower() or "hikaricp" in incident_report.lower():
            execution_logs.append("[EXEC] Patching ConfigMap for payment-service to increase max-connections...")
            time.sleep(0.5)
            execution_logs.append("[SUCCESS] ConfigMap patched. Max connections increased by 50%.")
            
        if "scale up" in incident_report.lower() or "replicas" in incident_report.lower():
            # Find the service name using regex
            match = re.search(r"Scale Up `(.*?)`", incident_report, re.IGNORECASE)
            service = match.group(1) if match else "payment-service"
            execution_logs.append(f"[EXEC] kubectl scale deployment {service} --replicas=5")
            time.sleep(0.8)
            execution_logs.append(f"[SUCCESS] {service} successfully scaled to 5 replicas.")

        if "restart" in incident_report.lower() and "pods" in incident_report.lower():
            match = re.search(r"Restart `(.*?)`", incident_report, re.IGNORECASE)
            service = match.group(1) if match else "payment-service"
            execution_logs.append(f"[EXEC] kubectl rollout restart deployment/{service}")
            time.sleep(1.2)
            execution_logs.append(f"[SUCCESS] {service} rolling restart initiated and stabilized.")

        if len(execution_logs) == 1:
            execution_logs.append("[WARNING] No standard actionable keywords found in remediation plan. Manual review required.")
        else:
            execution_logs.append("[SYSTEM] Auto-Remediation completed successfully. Alert status mitigated.")

        return execution_logs

# Quick test if run directly
if __name__ == "__main__":
    test_report = "1. Increase Database Connection Pool\n2. Scale Up `payment-service`\n3. Restart `payment-service` Pods"
    remediator = AutoRemediator()
    logs = remediator.execute_remediation(test_report)
    for log in logs:
        print(log)
