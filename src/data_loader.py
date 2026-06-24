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
        for incident in self.incidents.get('incidents', []):
            pattern = incident.get('pattern', '').lower()
            services = [s.lower() for s in incident.get('affected_services', [])]
            
            if pattern_or_service.lower() in pattern or pattern_or_service.lower() in services:
                results.append(incident)
        return results

    def get_recent_deployments(self, service_name: str) -> List[Dict[str, Any]]:
        """Get recent deployments for a specific service."""
        results = []
        for deploy in self.deployments.get('deployments', []):
            if deploy.get('service') == service_name:
                results.append(deploy)
        return results

# Example usage (can be removed later):
if __name__ == "__main__":
    loader = ShopFabricDataLoader()
    print("DataLoader Initialized successfully.")
    print(f"Loaded {len(loader.architecture['services'])} services.")
    print(f"Loaded {len(loader.incidents['incidents'])} historical incidents.")
