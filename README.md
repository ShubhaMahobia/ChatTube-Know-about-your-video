# ChatTube RAG API

A FastAPI-based REST API that enables users to ask questions about YouTube video content using Retrieval-Augmented Generation (RAG).

## Features

- 🎥 **YouTube Video Processing**: Automatically fetch and process YouTube video transcripts
- 🔍 **Intelligent Q&A**: Ask questions about video content and get contextual answers
- 📊 **Vector Search**: Uses FAISS for efficient similarity search
- 🤖 **OpenAI Integration**: Powered by GPT-4o-mini for accurate responses
- 📝 **Custom Logging**: Comprehensive logging with rotating file handlers
- 🌐 **CORS Support**: Ready for frontend integration
- 📚 **Auto Documentation**: Interactive API docs with Swagger UI

## Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd ChatTube-Know-about-your-video
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Quick Start

1. **Start the server**:
   ```bash
   python run_server.py
   ```
   
   Or alternatively:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Access the API**:
   - API Base URL: `http://localhost:8000`
   - Interactive Docs: `http://localhost:8000/docs`
   - ReDoc Documentation: `http://localhost:8000/redoc`

## API Endpoints

### Health Check
- **GET** `/` - Basic health check
- **GET** `/health` - Detailed health check
- **GET** `/status` - Service status and current video info

### Video Processing
- **POST** `/process-video` - Process a YouTube video for Q&A

### Chat
- **POST** `/chat` - Ask questions about the processed video

## Usage Examples

### 1. Process a YouTube Video

```bash
curl -X POST "http://localhost:8000/process-video" \
     -H "Content-Type: application/json" \
     -d '{"video_id": "Gfr50f6ZBvo"}'
```

**Response**:
```json
{
  "message": "Video processed successfully",
  "video_id": "Gfr50f6ZBvo",
  "chunks_count": 168,
  "status": "success"
}
```

### 2. Ask a Question

```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"question": "What is AlphaFold?"}'
```

**Response**:
```json
{
  "answer": "AlphaFold is a groundbreaking AI system developed by DeepMind that solved the protein folding problem...",
  "status": "success"
}
```

### 3. Check Service Status

```bash
curl -X GET "http://localhost:8000/status"
```

**Response**:
```json
{
  "service_status": "initialized",
  "current_video_id": "Gfr50f6ZBvo",
  "ready_for_questions": true
}
```

## API Schema

### Request Models

#### ProcessVideoRequest
```json
{
  "video_id": "string"  // YouTube video ID (11 characters)
}
```

#### ChatRequest
```json
{
  "question": "string",      // User's question (required)
  "video_id": "string"       // Optional: for future multi-video support
}
```

### Response Models

#### ProcessVideoResponse
```json
{
  "message": "string",
  "video_id": "string",
  "chunks_count": "integer",
  "status": "string"
}
```

#### ChatResponse
```json
{
  "answer": "string",
  "status": "string"
}
```

## Frontend Integration

### JavaScript/Fetch Example

```javascript
// Process a video
async function processVideo(videoId) {
  const response = await fetch('http://localhost:8000/process-video', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ video_id: videoId })
  });
  return await response.json();
}

// Ask a question
async function askQuestion(question) {
  const response = await fetch('http://localhost:8000/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ question: question })
  });
  return await response.json();
}
```

### React Example

```jsx
import React, { useState } from 'react';

function ChatTube() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question })
      });
      
      const data = await response.json();
      setAnswer(data.answer);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question about the video..."
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Loading...' : 'Ask'}
        </button>
      </form>
      {answer && <div className="answer">{answer}</div>}
    </div>
  );
}
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `LOG_LEVEL`: Logging level (default: INFO)
- `API_HOST`: Server host (default: 0.0.0.0)
- `API_PORT`: Server port (default: 8000)

### Logging

The application uses a custom logging configuration with:
- **File Logging**: Rotating log files (5MB max, 3 backups)
- **Console Logging**: Real-time console output
- **Log Location**: `logs/` directory
- **Format**: `[timestamp] logger_name - level - message`

## Error Handling

The API provides comprehensive error handling:

- **400 Bad Request**: Invalid input or video processing errors
- **404 Not Found**: Endpoint not found
- **500 Internal Server Error**: Server-side errors
- **503 Service Unavailable**: Service not ready

## Production Considerations

1. **Security**: 
   - Update CORS origins for production
   - Add authentication if needed
   - Use HTTPS

2. **Performance**:
   - Consider using Redis for caching
   - Implement rate limiting
   - Use a production WSGI server

3. **Monitoring**:
   - Set up proper logging aggregation
   - Add health check endpoints
   - Monitor API metrics

## Troubleshooting

### Common Issues

1. **"No video has been processed"**: Call `/process-video` first
2. **"Transcripts are disabled"**: Video doesn't have available transcripts
3. **OpenAI API errors**: Check your API key and quota

### Logs

Check the logs in the `logs/` directory for detailed error information.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.
