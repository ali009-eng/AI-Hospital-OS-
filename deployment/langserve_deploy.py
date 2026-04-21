"""
LangServe deployment for AI Triage Assistant
Alternative deployment using LangServe framework
"""
from fastapi import FastAPI
from langserve import add_routes
from langchain.schema.runnable import RunnableLambda
import uvicorn
import logging
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_integration.triage_agent import TriageAgent
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure directories exist
Config.ensure_directories()

app = FastAPI(title=Config.API_TITLE, version=Config.API_VERSION)

# Initialize agent
try:
    agent = TriageAgent()
    logger.info("Triage Agent initialized for LangServe")
except Exception as e:
    logger.error(f"Error initializing agent: {e}")
    agent = None

# Wrapper functions for LangServe
def process_patient_wrapper(input_data):
    """Wrapper for process_patient"""
    if agent is None:
        return {"error": "Agent not available"}
    if isinstance(input_data, dict):
        return agent.process_patient(input_data)
    return {"error": "Invalid input format"}

def analyze_surveillance_wrapper(input_data):
    """Wrapper for analyze_surveillance"""
    if agent is None:
        return {"error": "Agent not available"}
    if isinstance(input_data, dict):
        return agent.analyze_surveillance(input_data)
    return {"error": "Invalid input format"}

def update_dashboard_wrapper(input_data):
    """Wrapper for update_dashboard"""
    if agent is None:
        return {"error": "Agent not available"}
    if isinstance(input_data, dict):
        patient_data = input_data.get('patient_data', {})
        triage_result = input_data.get('triage_result', {})
        return agent.update_dashboard(patient_data, triage_result)
    return {"error": "Invalid input format"}

# Add LangServe routes
if agent:
    add_routes(
        app,
        RunnableLambda(process_patient_wrapper),
        path="/triage",
        description="Classify patient triage level"
    )
    
    add_routes(
        app,
        RunnableLambda(analyze_surveillance_wrapper),
        path="/surveillance",
        description="Analyze surveillance patterns"
    )
    
    add_routes(
        app,
        RunnableLambda(update_dashboard_wrapper),
        path="/dashboard",
        description="Update dashboard with patient data"
    )

@app.get("/health")
def health():
    """Health check endpoint"""
    return {
        "status": "healthy" if agent else "degraded",
        "agent_available": agent is not None
    }

if __name__ == "__main__":
    uvicorn.run(
        "deployment.langserve_deploy:app",
        host=Config.API_HOST,
        port=Config.API_PORT,
        reload=Config.API_RELOAD
    )