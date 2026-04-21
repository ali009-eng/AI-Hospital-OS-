"""
FastAPI Server for AI Triage Assistant
Main REST API with WebSocket support for real-time updates
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field, validator

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config
from langchain_integration.triage_agent import TriageAgent
from auth.security import get_current_user, create_access_token
from auth.user_manager import user_manager
from auth.models import UserLogin, Token, User

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Ensure directories exist
Config.ensure_directories()

# Initialize FastAPI app
app = FastAPI(
    title=Config.API_TITLE,
    version=Config.API_VERSION,
    description="AI-powered Emergency Department Triage Assistant API"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Triage Agent with lazy loading and caching
agent = None
_agent_lock = False

def get_agent():
    """Get or initialize triage agent (singleton pattern)"""
    global agent, _agent_lock
    
    if agent is not None:
        return agent
    
    if _agent_lock:
        # Wait for initialization
        import time
        while _agent_lock:
            time.sleep(0.1)
        return agent
    
    _agent_lock = True
    try:
        logger.info("Initializing Triage Agent...")
        agent = TriageAgent()
        logger.info("Triage Agent initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing Triage Agent: {e}")
        agent = None
    finally:
        _agent_lock = False
    
    return agent

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()

# Pydantic Models
class PatientData(BaseModel):
    """Patient data model for triage classification"""
    patient_id: str = Field(..., description="Unique patient identifier")
    age: Optional[int] = Field(None, ge=0, le=150, description="Patient age")
    gender: Optional[str] = Field(None, description="Patient gender")
    chief_complaint: Optional[str] = Field(None, description="Chief complaint")
    heart_rate: Optional[int] = Field(None, ge=30, le=300, description="Heart rate (bpm)")
    respiratory_rate: Optional[int] = Field(None, ge=5, le=60, description="Respiratory rate")
    oxygen_saturation: Optional[float] = Field(None, ge=0, le=100, description="O2 saturation (%)")
    temperature: Optional[float] = Field(None, ge=30, le=45, description="Temperature (°C)")
    blood_pressure: Optional[str] = Field(None, description="Blood pressure (e.g., '120/80')")
    pain_level: Optional[int] = Field(None, ge=0, le=10, description="Pain level (0-10)")
    
    @validator('gender')
    def validate_gender(cls, v):
        if v and v.upper() not in ['M', 'F', 'MALE', 'FEMALE', 'OTHER']:
            raise ValueError('Gender must be M, F, Male, Female, or Other')
        return v.upper() if v else None

class TriageResponse(BaseModel):
    """Triage classification response"""
    patient_id: str
    triage_level: int
    esi_level: str
    reasoning: str
    risk_factors: List[str]
    recommendations: List[str]
    confidence: float
    retrieved_cases: int
    classification_method: str
    timestamp: str

class BatchTriageRequest(BaseModel):
    """Batch triage request"""
    patients: List[PatientData]
    async_processing: bool = False

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": Config.API_TITLE,
        "version": Config.API_VERSION,
        "status": "operational" if agent else "degraded",
        "endpoints": {
            "health": "/health",
            "triage": "/triage",
            "dashboard": "/dashboard",
            "surveillance": "/surveillance",
            "websocket": "/ws",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    agent = get_agent()
    status_info = {
        "status": "healthy" if agent else "degraded",
        "timestamp": datetime.now().isoformat(),
        "agent_available": agent is not None,
        "config": {
            "model_name": Config.MODEL_NAME,
            "api_version": Config.API_VERSION
        }
    }
    
    if agent:
        try:
            agent_status = agent.get_agent_status()
            status_info["agent_status"] = agent_status
        except Exception as e:
            logger.error(f"Error getting agent status: {e}")
            status_info["agent_status"] = {"error": str(e)}
    
    return status_info

@app.post("/auth/login", response_model=Token)
async def login(login_data: UserLogin):
    """Login endpoint for authentication"""
    if not Config.ENABLE_AUTH:
        # Return dummy token if auth disabled
        return Token(access_token="disabled", token_type="bearer")
    
    user = user_manager.authenticate_user(login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    return Token(access_token=access_token, token_type="bearer")


@app.get("/auth/me", response_model=User)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    user = user_manager.get_user(current_user["username"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/triage", response_model=TriageResponse)
async def classify_patient(
    patient: PatientData,
    current_user: dict = Depends(get_current_user)
):
    """
    Classify a single patient's triage level
    
    Returns ESI level (1-5) with reasoning and recommendations
    """
    if not agent:
        raise HTTPException(
            status_code=503,
            detail="Triage agent not available"
        )
    
    try:
        # Validate patient data
        if not patient.patient_id:
            raise HTTPException(
                status_code=400,
                detail="patient_id is required"
            )
        
        # Convert Pydantic model to dict
        patient_dict = patient.dict(exclude_none=True)
        
        # Validate at least some patient data is provided
        required_fields = ['patient_id']
        vital_fields = ['heart_rate', 'respiratory_rate', 'oxygen_saturation', 
                       'temperature', 'blood_pressure', 'pain_level', 'chief_complaint']
        
        if not any(patient_dict.get(field) is not None for field in vital_fields):
            logger.warning(f"Patient {patient.patient_id} has minimal data - only patient_id provided")
        
        # Process patient
        logger.info(f"Processing patient: {patient.patient_id}")
        result = agent.process_patient(patient_dict)
        
        # Extract triage result
        if 'triage_result' in result:
            triage_data = result['triage_result']
        else:
            # Fallback if structure is different
            triage_data = {
                'triage_level': 3,
                'esi_level': 'Medium',
                'reasoning': 'Classification completed',
                'risk_factors': [],
                'recommendations': [],
                'confidence': 0.5,
                'retrieved_cases': 0,
                'classification_method': 'default'
            }
        
        # Broadcast update to WebSocket clients
        await manager.broadcast({
            "type": "patient_classified",
            "data": {
                "patient_id": patient.patient_id,
                "triage_level": triage_data.get('triage_level', 3),
                "timestamp": datetime.now().isoformat()
            }
        })
        
        return TriageResponse(
            patient_id=patient.patient_id,
            triage_level=triage_data.get('triage_level', 3),
            esi_level=triage_data.get('esi_level', Config.ESI_LEVELS.get(3, 'Unknown')),
            reasoning=triage_data.get('reasoning', ''),
            risk_factors=triage_data.get('risk_factors', []),
            recommendations=triage_data.get('recommendations', []),
            confidence=triage_data.get('confidence', 0.5),
            retrieved_cases=triage_data.get('retrieved_cases', 0),
            classification_method=triage_data.get('classification_method', 'unknown'),
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error classifying patient: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error classifying patient: {str(e)}"
        )

@app.post("/triage/batch")
async def batch_classify(request: BatchTriageRequest):
    """Classify multiple patients in batch"""
    if not agent:
        raise HTTPException(
            status_code=503,
            detail="Triage agent not available"
        )
    
    try:
        patients_dict = [p.dict(exclude_none=True) for p in request.patients]
        results = agent.batch_process_patients(patients_dict)
        
        return {
            "processed": len(results),
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in batch classification: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error in batch classification: {str(e)}"
        )

@app.get("/dashboard")
async def get_dashboard_data(current_user: dict = Depends(get_current_user)):
    """Get dashboard data including patient queue and statistics"""
    agent = get_agent()
    if not agent:
        raise HTTPException(
            status_code=503,
            detail="Triage agent not available"
        )
    
    try:
        dashboard_data = agent.get_dashboard_data()
        return dashboard_data
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error getting dashboard data: {str(e)}"
        )

@app.get("/surveillance")
async def get_surveillance_data(current_user: dict = Depends(get_current_user)):
    """Get surveillance data including alerts and trends"""
    agent = get_agent()
    if not agent:
        raise HTTPException(
            status_code=503,
            detail="Triage agent not available"
        )
    
    try:
        surveillance_data = agent.get_surveillance_data()
        return surveillance_data
    except Exception as e:
        logger.error(f"Error getting surveillance data: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error getting surveillance data: {str(e)}"
        )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    
    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_text()
            # Echo back or handle client messages
            await websocket.send_json({
                "type": "acknowledgment",
                "message": "Message received",
                "timestamp": datetime.now().isoformat()
            })
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# Serve static files (dashboard)
dashboard_path = Path(__file__).parent.parent / "dashboard" / "static"
if dashboard_path.exists():
    app.mount("/dashboard", StaticFiles(directory=str(dashboard_path), html=True), name="dashboard")

@app.get("/dashboard/index.html", response_class=HTMLResponse)
async def dashboard_page():
    """Serve dashboard HTML"""
    dashboard_file = dashboard_path / "index.html"
    if dashboard_file.exists():
        return dashboard_file.read_text()
    return HTMLResponse(content="<h1>Dashboard not found</h1>", status_code=404)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.server:app",
        host=Config.API_HOST,
        port=Config.API_PORT,
        reload=Config.API_RELOAD
    )
