#!/usr/bin/env python3
"""
ChatTube RAG API Server Startup Script

This script starts the FastAPI server for the ChatTube RAG application.
"""

import uvicorn
import logging
from logger import configure_logger

# Configure logging
configure_logger()
logger = logging.getLogger(__name__)

def main():
    """Main function to start the server"""
    logger.info("Starting ChatTube RAG API Server...")
    
    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        raise

if __name__ == "__main__":
    main()
