import json
import os
from typing import Dict, Any, List

# Define the path to the data directory relative to the current script
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

def load_json(filename: str) -> Any:
    """Utility function to load a JSON file from the data directory."""
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Data file not found: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

class ShopFabricDataLoader:
    """
    A class to load and interface with the ShopFabric telemetry and historical data.
    This acts as the primary data source tool for our AI Incident Commander.
    """
    
    def __init__(self):
        # Load all datasets into memory upon initialization
        self.architecture = load_json('architecture_overview.json')
        self.incidents = load_json('incidents.json')
        self.alerts = load_json('alerts.json')
        self.metrics = load_json('metrics.json')
        self.logs = load_json('logs.json')
        self.runbooks = load_json('runbooks.json')
        self.deployments = load_json('deployments.json')
        self.customer_reports = load_json('customer_reports.json')
        self.postmortems = load_json('postmortems.json')
        self.service_dependencies = load_json('service_dependencies.json')
    def get_service_architecture(self, service_name: str) -> Dict[str, Any]:
        """Retrieve architectural details for a specific service."""
        for service in self.architecture.get('services', []):
            if service['name'] == service_name:
                return service
        return {"error": f"Service '{service_name}' not found in architecture overview."}

    def get_active_alerts(self, severity: str = None) -> List[Dict[str, Any]]:
        """Retrieve active alerts, optionally filtered by severity (e.g., 'CRITICAL')."""
        active_alerts = self.alerts.get('alerts', [])
        if severity:
            active_alerts = [a for a in active_alerts if a.get('severity') == severity]
        return active_alerts

    def search_historical_incidents(self, pattern_or_service: str) -> List[Dict[str, Any]]:
        """Search historical incidents for matching patterns or affected services."""
        results = []
        keywords = [k.strip().lower() for k in pattern_or_service.split(" OR ")] if pattern_or_service else []
        for incident in self.incidents.get('incidents', []):
            pattern = incident.get('pattern', '').lower()
            services = [s.lower() for s in incident.get('affected_services', [])]
            
            match = False
            for k in keywords:
                if k in pattern or k in services:
                    match = True
                    break
                    
            if not pattern_or_service or match:
                results.append(incident)
        return results

    def get_recent_deployments(self, service_name: str) -> List[Dict[str, Any]]:
        """Get recent deployments for a specific service."""
        results = []
        for deploy in self.deployments.get('deployments', []):
            if deploy.get('service') == service_name:
                results.append(deploy)
        return results

    def get_service_metrics(self, service_name: str) -> List[Dict[str, Any]]:
        """Retrieve performance and health metrics for a specific service."""
        results = []
        for metric in self.metrics.get('metrics', []):
            if metric.get('service') == service_name:
                results.append(metric)
        # Limit to recent metrics if there are too many, but for now return all matched
        return results[-10:] if len(results) > 10 else results

    def search_logs(self, service_name: str, query: str = "") -> List[Dict[str, Any]]:
        """Search logs for a specific service, optionally filtering by a query string (e.g., 'error' or 'timeout'). Supports ' OR '."""
        results = []
        keywords = [k.strip().lower() for k in query.split(" OR ")] if query else []
        for log in self.logs.get('logs', []):
            if log.get('service') == service_name:
                if not query or any(k in log.get('message', '').lower() for k in keywords):
                    results.append(log)
        return results[-20:] if len(results) > 20 else results

    def search_customer_reports(self, query: str = "") -> List[Dict[str, Any]]:
        """Search recent customer reports for keywords (e.g., 'checkout', 'payment')."""
        results = []
        for report in self.customer_reports.get('reports', []):
            if not query or query.lower() in report.get('message', '').lower() or query.lower() in ' '.join(report.get('tags', [])).lower():
                results.append(report)
        return results[-10:] if len(results) > 10 else results

    def get_runbook(self, service_name: str) -> Dict[str, Any]:
        """Retrieve the runbook (troubleshooting steps) for a specific service."""
        for runbook in self.runbooks.get('runbooks', []):
            if service_name in runbook.get('applies_to', []):
                return runbook
        return {"error": f"No runbook found for {service_name}"}

    def get_postmortems(self, query: str) -> List[Dict[str, Any]]:
        """Search past postmortems for lessons learned and previous root causes."""
        results = []
        for pm in self.postmortems.get('postmortems', []):
            if query.lower() in pm.get('title', '').lower() or query.lower() in pm.get('root_cause', '').lower():
                results.append(pm)
        return results

    def get_service_dependencies(self, service_name: str) -> Dict[str, Any]:
        """Retrieve upstream and downstream dependencies for a service."""
        for dep in self.service_dependencies.get('services', []):
            if dep.get('service') == service_name:
                return dep
        return {"error": f"No dependencies found for {service_name}"}
# Example usage (can be removed later):
if __name__ == "__main__":
    loader = ShopFabricDataLoader()
    print("DataLoader Initialized successfully.")
    print(f"Loaded {len(loader.architecture['services'])} services.")
    print(f"Loaded {len(loader.incidents['incidents'])} historical incidents.")
