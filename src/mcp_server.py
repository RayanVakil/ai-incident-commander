import json
from mcp.server.fastmcp import FastMCP
from data_loader import ShopFabricDataLoader

# Initialize the MCP server
mcp = FastMCP("IncidentCommanderServer")

# Initialize the data loader
data_loader = ShopFabricDataLoader()

@mcp.tool()
def get_service_architecture(query: str) -> str:
    """Input: service name (e.g. 'checkout-service'). Returns its dependencies, databases, and owner team."""
    return json.dumps(data_loader.get_service_architecture(query.strip()), indent=2)

@mcp.tool()
def get_active_alerts(query: str) -> str:
    """Input: severity (e.g. 'CRITICAL' or 'ALL'). Returns active PagerDuty/Prometheus alerts."""
    severity = query.strip().upper()
    if severity == 'ALL' or severity == '':
        severity = None
    return json.dumps(data_loader.get_active_alerts(severity), indent=2)

@mcp.tool()
def search_historical_incidents(query: str) -> str:
    """Use this to find past incidents to see how they were fixed. Input should be a service name or failure pattern (e.g., 'redis_outage' or 'payment-service')."""
    return json.dumps(data_loader.search_historical_incidents(query.strip())[:3], indent=2)

@mcp.tool()
def get_recent_deployments(query: str) -> str:
    """Use this to check if a recent code deployment might have caused the issue. Input should be the service name."""
    return json.dumps(data_loader.get_recent_deployments(query.strip()), indent=2)

@mcp.tool()
def get_service_metrics(query: str) -> str:
    """Use this to retrieve performance and health metrics for a specific service. Input should be the service name."""
    return json.dumps(data_loader.get_service_metrics(query.strip()), indent=2)

@mcp.tool()
def search_logs(query: str) -> str:
    """Use this to search logs for a specific service. Input should be a JSON string like {"service": "checkout-service", "query": "error"}."""
    try:
        params = json.loads(query)
        service = params.get("service", "")
        q = params.get("query", "")
        return json.dumps(data_loader.search_logs(service, q), indent=2)
    except Exception as e:
        return json.dumps(data_loader.search_logs(query.strip()), indent=2)

@mcp.tool()
def search_customer_reports(query: str) -> str:
    """Use this to search recent customer reports for keywords. Input should be the keyword (e.g., 'checkout')."""
    return json.dumps(data_loader.search_customer_reports(query.strip()), indent=2)

@mcp.tool()
def get_runbook(query: str) -> str:
    """Use this to retrieve the runbook (troubleshooting steps) for a specific service. Input should be the service name."""
    return json.dumps(data_loader.get_runbook(query.strip()), indent=2)

@mcp.tool()
def get_postmortems(query: str) -> str:
    """Use this to search past postmortems for lessons learned. Input should be a query string."""
    return json.dumps(data_loader.get_postmortems(query.strip()), indent=2)

@mcp.tool()
def get_service_dependencies(query: str) -> str:
    """Use this to retrieve upstream and downstream dependencies for a service. Input should be the service name."""
    return json.dumps(data_loader.get_service_dependencies(query.strip()), indent=2)

if __name__ == "__main__":
    mcp.run()
