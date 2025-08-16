import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import custom logger configuration
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger import configure_logger

# Import our models and services
from .models import (
    ChatRequest, ChatResponse, ProcessVideoRequest, 
    ProcessVideoResponse, HealthResponse
)
from .rag_service import RAGService

# Configure logging
configure_logger()
logger = logging.getLogger(__name__)

# Global RAG service instance
rag_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global rag_service
    
    # Startup
    logger.info("Starting ChatTube RAG API...")
    try:
        rag_service = RAGService()
        logger.info("RAG service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize RAG service: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down ChatTube RAG API...")

# Create FastAPI app
app = FastAPI(
    title="ChatTube RAG API",
    description="A RAG-based API for asking questions about YouTube video content",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error occurred"}
    )

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check"""
    logger.info("Health check requested")
    return HealthResponse(
        status="healthy",
        message="ChatTube RAG API is running successfully"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check endpoint"""
    logger.info("Detailed health check requested")
    
    try:
        global rag_service
        if rag_service is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="RAG service is not initialized"
            )
        
        return HealthResponse(
            status="healthy",
            message="All services are operational"
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service is not healthy"
        )

@app.post("/process-video", response_model=ProcessVideoResponse)
async def process_video(request: ProcessVideoRequest):
    """
    Process a YouTube video for RAG
    
    This endpoint fetches the transcript of a YouTube video,
    processes it into chunks, and creates a vector store for querying.
    """
    logger.info(f"Video processing requested for ID: {request.video_id}")
    
    try:
        global rag_service
        if rag_service is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="RAG service is not available"
            )
        
        # Process the video
        result = rag_service.process_video(request.video_id)
        
        response = ProcessVideoResponse(
            message=result["message"],
            video_id=result["video_id"],
            chunks_count=result["chunks_count"],
            status="success"
        )
        
        logger.info(f"Video processing completed successfully for: {request.video_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing video {request.video_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Ask a question about the processed video content
    
    This endpoint uses the RAG system to answer questions based on
    the previously processed video transcript.
    """
    logger.info(f"Chat request received: {request.question[:100]}...")
    
    try:
        global rag_service
        if rag_service is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="RAG service is not available"
            )
        
        if not rag_service.is_ready():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No video has been processed yet. Please process a video first using /process-video endpoint."
            )
        
        # Get answer from RAG service
        answer = rag_service.ask_question(request.question)
        
        response = ChatResponse(
            answer=answer,
            status="success"
        )
        
        logger.info("Chat request processed successfully")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process question: {str(e)}"
        )

@app.get("/status")
async def get_status():
    """Get current service status and processed video info"""
    logger.info("Status request received")
    
    try:
        global rag_service
        if rag_service is None:
            return {
                "service_status": "not_initialized",
                "current_video_id": None,
                "ready_for_questions": False
            }
        
        return {
            "service_status": "initialized",
            "current_video_id": rag_service.get_current_video_id(),
            "ready_for_questions": rag_service.is_ready()
        }
        
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get service status"
        )

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server directly...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
