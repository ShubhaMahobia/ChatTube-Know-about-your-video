from pydantic import BaseModel, Field
from typing import List, Optional

class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    question: str = Field(..., description="User's question about the video", min_length=1)
    video_id: Optional[str] = Field(None, description="YouTube video ID (optional for future use)")

class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    answer: str = Field(..., description="AI-generated answer based on video content")
    status: str = Field(..., description="Response status")
    
class ProcessVideoRequest(BaseModel):
    """Request model for processing a new video"""
    video_id: str = Field(..., description="YouTube video ID", min_length=11, max_length=11)
    
class ProcessVideoResponse(BaseModel):
    """Response model for video processing"""
    message: str = Field(..., description="Processing status message")
    video_id: str = Field(..., description="Processed video ID")
    chunks_count: int = Field(..., description="Number of text chunks created")
    status: str = Field(..., description="Processing status")

class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(..., description="API health status")
    message: str = Field(..., description="Health check message")
