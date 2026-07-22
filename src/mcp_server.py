import json
from mcp.server.fastmcp import FastMCP
from data_loader import ShopFabricDataLoader

# Initialize the MCP server
mcp = FastMCP("IncidentCommanderServer")

# Initialize the data loader (in-memory store over static JSON)
data_loader = ShopFabricDataLoader()

# ---------------------------------------------------------------------------
# Tools: Each tool uses properly typed parameters so that the MCP schema
# accurately describes the expected inputs. This allows any MCP client to
# discover and invoke these tools without relying on JSON-string hacks.
# ---------------------------------------------------------------------------

@mcp.tool()
def get_service_architecture(service_name: str) -> str:
    """Retrieve architectural details (dependencies, databases, owner team) for a specific service.
    
    Args:
        service_name: The name of the service (e.g. 'checkout-service', 'payment-service').
    """
    return json.dumps(data_loader.get_service_architecture(service_name.strip()), indent=2)

@mcp.tool()
def get_active_alerts(severity: str = "ALL") -> str:
    """Retrieve active PagerDuty/Prometheus alerts, optionally filtered by severity.
    
    Args:
        severity: Alert severity filter. Use 'CRITICAL', 'WARNING', or 'ALL' for unfiltered.
    """
    sev = severity.strip().upper()
    return json.dumps(data_loader.get_active_alerts(None if sev in ("ALL", "") else sev), indent=2)

@mcp.tool()
def search_historical_incidents(pattern: str) -> str:
    """Search past incidents to find how similar issues were resolved.
    
    Args:
        pattern: A service name or failure pattern (e.g. 'redis_outage', 'payment-service').
    """
    return json.dumps(data_loader.search_historical_incidents(pattern.strip())[:3], indent=2)

@mcp.tool()
def get_recent_deployments(service_name: str) -> str:
    """Check if a recent code deployment might have caused the issue.
    
    Args:
        service_name: The name of the service to check deployments for.
    """
    return json.dumps(data_loader.get_recent_deployments(service_name.strip()), indent=2)

@mcp.tool()
def get_service_metrics(service_name: str) -> str:
    """Retrieve performance and health metrics (CPU, memory, latency, error rate) for a service.
    
    Args:
        service_name: The name of the service to retrieve metrics for.
    """
    return json.dumps(data_loader.get_service_metrics(service_name.strip()), indent=2)

@mcp.tool()
def search_logs(service_name: str, query: str = "") -> str:
    """Search application logs for a specific service. Supports ' OR ' logic for multiple keywords.
    
    Args:
        service_name: The service whose logs to search (e.g. 'checkout-service').
        query: Optional keyword filter (e.g. 'error', 'timeout OR redis'). Leave empty for all logs.
    """
    return json.dumps(data_loader.search_logs(service_name.strip(), query.strip()), indent=2)

@mcp.tool()
def search_customer_reports(keyword: str) -> str:
    """Search recent customer reports and complaints for keywords.
    
    Args:
        keyword: The keyword to search for (e.g. 'checkout', 'payment', 'slow').
    """
    return json.dumps(data_loader.search_customer_reports(keyword.strip()), indent=2)

@mcp.tool()
def get_runbook(service_name: str) -> str:
    """Retrieve the runbook (troubleshooting steps) for a specific service or error type.
    
    Args:
        service_name: The service name or error type to find a runbook for.
    """
    return json.dumps(data_loader.get_runbook(service_name.strip()), indent=2)

@mcp.tool()
def get_postmortems(query: str) -> str:
    """Search past postmortems for lessons learned and known root causes.
    
    Args:
        query: A keyword describing the issue (e.g. 'dns', 'connection pool', 'redis').
    """
    return json.dumps(data_loader.get_postmortems(query.strip()), indent=2)

@mcp.tool()
def get_service_dependencies(service_name: str) -> str:
    """Retrieve upstream and downstream dependencies for a service.
    
    Args:
        service_name: The name of the service to map dependencies for.
    """
    return json.dumps(data_loader.get_service_dependencies(service_name.strip()), indent=2)


if __name__ == "__main__":
    mcp.run()
