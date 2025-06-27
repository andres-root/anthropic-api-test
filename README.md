# AioPy - AsyncIO and FastAPI with Anthropic Claude Integration

A Python project demonstrating asyncio patterns, FastAPI web development, and real-time AI chat completions using Anthropic's Claude API.

## Project Setup

### Prerequisites
- Conda or Anaconda installed
- Python 3.11+ recommended

### Installation

1. **Create and activate conda environment:**
   ```bash
   conda create -n aiopy python=3 -y
   conda activate aiopy
   ```

2. **Install dependencies:**
   ```bash
   pip install fastapi uvicorn black pre-commit pytest httpx anthropic python-dotenv pytest-asyncio
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your ANTHROPIC_API_KEY
   ```

4. **Optional: Set up pre-commit hooks:**
   ```bash
   pre-commit install
   ```

## Running the Project

### AsyncIO Examples

Run the basic asyncio examples:
```bash
# Basic asyncio patterns
python async1.py

# Advanced task orchestration with cancellation
python async2.py
```

### FastAPI Web Server

**Prerequisites:** Make sure you have your `.env` file configured with your Anthropic API key:
```bash
cp .env.example .env
# Edit .env and add: ANTHROPIC_API_KEY=your_actual_api_key_here
```

Start the FastAPI development server:
```bash
# Basic development server
uvicorn app:app --reload

# With custom host and port
uvicorn app:app --host 0.0.0.0 --port 8080 --reload

# Production mode (no reload)
uvicorn app:app --host 0.0.0.0 --port 8000
```

The API will be available at:
- **Main API**: http://localhost:8000
- **Interactive docs**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc

### Available Endpoints

#### General Endpoints
- `GET /` - Welcome message
- `GET /health` - Health check
- `GET /async-demo` - Demonstrates concurrent async tasks
- `GET /users/{user_id}` - Get user by ID
- `POST /echo` - Echo back JSON data

#### AI Chat Endpoints
- `POST /chat/completions` - Create chat completions with Anthropic Claude
  - Supports both streaming and non-streaming responses
  - Compatible with OpenAI-style chat format
  - Requires `ANTHROPIC_API_KEY` environment variable

#### Example Chat Request
```bash
curl -X POST "http://localhost:8000/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hello, how are you?"}
    ],
    "stream": true
  }'
```

## Testing

Run the test suite:
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/integration/test_basic_api.py

# Run chat API tests
pytest tests/integration/test_chat_api.py

# Run tests with coverage
pytest --cov=app
```

## Code Quality

Format code with Black:
```bash
# Format all Python files
black .

# Check formatting without making changes
black --check .
```

Run pre-commit hooks:
```bash
# Run on all files
pre-commit run --all-files

# Run on staged files only
pre-commit run
```

## Project Structure

```
aiopy/
├── async1.py        # Basic asyncio examples
├── async2.py        # Advanced asyncio orchestration
├── app.py           # FastAPI application
├── test_app.py      # Test suite for FastAPI
├── README.md        # Project documentation
└── CLAUDE.md        # Claude Code guidance
```

## Development Notes

- All commands assume the `aiopy` conda environment is activated
- The FastAPI server runs with auto-reload enabled for development
- Tests use FastAPI's TestClient for endpoint testing
- Code is formatted using Black with default settings