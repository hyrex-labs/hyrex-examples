# AI Chatbot with Long-Term Memory

A chatbot that remembers conversations using Hyrex for async task processing, PostgreSQL with pgvector for semantic memory search, and OpenAI for chat completions.

## Prerequisites

- PostgreSQL with pgvector extension installed
- OpenAI API key
- Python 3.11+

## Setup

1. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your configuration:
```bash
cp .env.example .env
# Edit .env with your actual values
```

4. Set up the database:
```bash
cd scripts
python setup_db.py
cd ..
```

## Running the Application

You'll need three terminal windows:

### Terminal 1: Start the Hyrex worker
```bash
hyrex run-worker hyrex_app:app
```

### Terminal 2: Run the FastAPI server
```bash
python api.py
```
The API will be available at http://localhost:8000

### Terminal 3: Open the chat interface
```bash
open frontend/index.html
```
Or simply open `frontend/index.html` in your web browser.

## How It Works

- **Hyrex Worker**: Processes messages asynchronously, retrieves memories, and extracts new facts
- **API Server**: Handles HTTP requests and queues tasks for the worker
- **Frontend**: Simple HTML interface with polling for real-time message updates

The chatbot remembers facts about users across conversations using semantic search on embeddings stored in PostgreSQL.
