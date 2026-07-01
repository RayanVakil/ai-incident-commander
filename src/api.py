import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn

# Import our backend modules
from agent import IncidentCommanderAgent
from auto_remediator import AutoRemediator

app = FastAPI(title="AI Incident Commander API")

# Initialize our agent and remediator (singletons for the server lifecycle)
commander = IncidentCommanderAgent()
remediator = AutoRemediator()

# Define the expected request body for the /investigate endpoint
class AlertRequest(BaseModel):
    alert_message: str

@app.post("/api/investigate")
def investigate_alert(request: AlertRequest):
    """
    Takes an incoming alert, runs the LangGraph AI Agent to generate an 
    Incident Report, and then triggers the Auto-Remediator to simulate fixes.
    """
    try:
        # 1. Run the AI Agent to get the Incident Report
        investigation_result = commander.investigate(request.alert_message)
        incident_report = investigation_result["report"]
        thought_process = investigation_result["thought_process"]
        
        # 2. Run the Auto-Remediator to simulate execution based on the report
        remediation_logs = remediator.execute_remediation(incident_report)
        
        return {
            "status": "success",
            "report": incident_report,
            "thought_process": thought_process,
            "remediation_logs": remediation_logs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount the static directory to serve the frontend UI
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def serve_index():
    """Serves the main frontend dashboard."""
    return FileResponse(os.path.join(static_dir, "index.html"))

if __name__ == "__main__":
    print("Starting AI Incident Commander Server on http://localhost:8000")
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
