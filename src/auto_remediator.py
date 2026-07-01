import re
import time

class AutoRemediator:
    """
    Parses the AI Incident Commander's report and simulates 
    executing the recommended remediation steps against the cluster.
    """
    
    def __init__(self):
        pass

    def _extract_service(self, text: str) -> str:
        services = ["payment-service", "checkout-service", "inventory-service", "order-service", "product-service", "user-service", "api-gateway"]
        mentions = {svc: text.count(svc) for svc in services if text.count(svc) > 0}
        return max(mentions, key=mentions.get) if mentions else "payment-service"

    def execute_remediation(self, incident_report: str) -> list[str]:
        """
        Parses the report for key remediation steps and returns a list of 
        simulated commands/logs.
        """
        execution_logs = []
        execution_logs.append("[SYSTEM] Initiating Auto-Remediation based on AI Report...")
        time.sleep(0.5)

        target_service = self._extract_service(incident_report)

        # Look for keywords in the report to trigger simulated actions
        if "increase database connection pool" in incident_report.lower() or "hikaricp" in incident_report.lower() or "max_connections" in incident_report.lower():
            execution_logs.append(f"[EXEC] Patching ConfigMap for {target_service} to increase max-connections...")
            time.sleep(0.5)
            execution_logs.append("[SUCCESS] ConfigMap patched. Max connections increased by 50%.")
            
        if "scale" in incident_report.lower() or "replicas" in incident_report.lower():
            execution_logs.append(f"[EXEC] kubectl scale deployment {target_service} --replicas=5")
            time.sleep(0.8)
            execution_logs.append(f"[SUCCESS] {target_service} successfully scaled to 5 replicas.")

        if "restart" in incident_report.lower() and "pods" in incident_report.lower():
            execution_logs.append(f"[EXEC] kubectl rollout restart deployment/{target_service}")
            time.sleep(1.2)
            execution_logs.append(f"[SUCCESS] {target_service} rolling restart initiated and stabilized.")

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
