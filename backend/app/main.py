"""
FastAPI main application for DynamicContractOps
Smart Legal Contract Collaboration Platform
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
import asyncio
from typing import Dict, Set

from app.core.config import settings
from app.core.database import init_db
from app.api.v1.router import api_router
from app.websocket.manager import ConnectionManager
from app.services.ai_service import AIService
from app.services.document_analyzer import DocumentAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# WebSocket connection manager
manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting DynamicContractOps backend...")
    await init_db()
    
    # Initialize AI services
    ai_service = AIService()
    doc_analyzer = DocumentAnalyzer()
    
    # Store services in app state
    app.state.ai_service = ai_service
    app.state.doc_analyzer = doc_analyzer
    app.state.connection_manager = manager
    
    yield
    
    # Shutdown
    logger.info("Shutting down DynamicContractOps backend...")
    await manager.disconnect_all()

app = FastAPI(
    title="DynamicContractOps API",
    description="Smart Legal Contract Collaboration Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# WebSocket endpoint for real-time collaboration
@app.websocket("/ws/{contract_id}")
async def websocket_endpoint(websocket: WebSocket, contract_id: int):
    """WebSocket endpoint for real-time contract collaboration"""
    await manager.connect(websocket, contract_id)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast_to_contract(contract_id, data, exclude=websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket, contract_id)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "DynamicContractOps"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )