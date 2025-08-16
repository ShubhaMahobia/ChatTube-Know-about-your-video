# ChatTube RAG API Setup Guide

This guide will help you set up and run the ChatTube RAG API on your local machine or server.

## Prerequisites

- Python 3.10 or higher
- OpenAI API key
- Git (for cloning the repository)

## Installation Steps

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd ChatTube-Know-about-your-video
```

### 2. Create a Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the root directory:

```bash
# Create .env file
touch .env
```

Add your OpenAI API key to the `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 5. Test the Installation

```bash
# Test the basic imports
python -c "import fastapi, uvicorn; print('✅ Dependencies installed successfully')"
```

## Running the API

### Method 1: Using the Startup Script (Recommended)

```bash
python run_server.py
```

### Method 2: Using Uvicorn Directly

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Method 3: Using Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build and run manually
docker build -t chattube-api .
docker run -p 8000:8000 -e OPENAI_API_KEY=your_key_here chattube-api
```

## Verification

Once the server is running, you can verify it's working:

1. **Open your browser** and go to: `http://localhost:8000`
2. **Check the interactive docs**: `http://localhost:8000/docs`
3. **Run the example client**:
   ```bash
   python example_client.py
   ```

## API Endpoints Overview

- `GET /` - Health check
- `GET /health` - Detailed health check  
- `GET /status` - Service status
- `POST /process-video` - Process a YouTube video
- `POST /chat` - Ask questions about the video

## Quick Test

### 1. Process a Video

```bash
curl -X POST "http://localhost:8000/process-video" \
     -H "Content-Type: application/json" \
     -d '{"video_id": "Gfr50f6ZBvo"}'
```

### 2. Ask a Question

```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"question": "What is this video about?"}'
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you're in the correct virtual environment
2. **OpenAI API Errors**: Verify your API key is correct and has sufficient credits
3. **Port Already in Use**: Change the port in `run_server.py` or kill the process using port 8000
4. **YouTube Transcript Errors**: Some videos don't have transcripts available

### Checking Logs

Logs are stored in the `logs/` directory. Check the latest log file for detailed error information:

```bash
# View the latest log file
ls -la logs/
tail -f logs/[latest_log_file].log
```

### Environment Variables

If you're having issues with environment variables, you can set them directly:

```bash
# On Windows
set OPENAI_API_KEY=your_key_here
python run_server.py

# On macOS/Linux
export OPENAI_API_KEY=your_key_here
python run_server.py
```

## Development

### Project Structure

```
ChatTube-Know-about-your-video/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   ├── models.py        # Pydantic models
│   └── rag_service.py   # RAG logic
├── logs/                # Log files
├── experiment.ipynb     # Original notebook
├── logger.py           # Custom logger
├── run_server.py       # Server startup script
├── example_client.py   # Example usage
├── requirements.txt    # Dependencies
└── README.md
```

### Adding New Features

1. **New Endpoints**: Add them to `app/main.py`
2. **New Models**: Define them in `app/models.py`
3. **RAG Logic**: Modify `app/rag_service.py`
4. **Logging**: Use the configured logger: `logger = logging.getLogger(__name__)`

### Running in Development Mode

For development, use the reload flag:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

This will automatically restart the server when you make changes to the code.

## Production Deployment

### Security Considerations

1. **Update CORS settings** in `app/main.py`
2. **Use HTTPS** in production
3. **Add authentication** if needed
4. **Set proper environment variables**

### Performance Optimizations

1. **Use a production WSGI server** like Gunicorn
2. **Add caching** with Redis
3. **Implement rate limiting**
4. **Use a reverse proxy** like Nginx

### Example Production Command

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Support

If you encounter any issues:

1. Check the logs in the `logs/` directory
2. Verify your OpenAI API key is working
3. Make sure all dependencies are installed
4. Check the GitHub issues page

## Next Steps

After successfully setting up the API:

1. **Build a frontend** using the API endpoints
2. **Add more video sources** beyond YouTube
3. **Implement user authentication**
4. **Add video metadata storage**
5. **Create batch processing** for multiple videos

Happy coding! 🚀
