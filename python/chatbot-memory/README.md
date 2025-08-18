# AI Chatbot with Long-Term Memory

A chatbot that remembers conversations using Hyrex for async task processing, PostgreSQL with pgvector for semantic memory search, and OpenAI for chat completions.

## Quick Start with Docker Compose

The easiest way to run the entire application is with Docker Compose:

1. **Clone the repository and navigate to the project directory**

2. **Set up your environment file:**
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

3. **Start all services with one command:**
```bash
docker-compose up --build
```

4. **Access the chatbot:**
   - Open http://localhost:8000/frontend/ in your browser
   - The API is available at http://localhost:8000

5. **Stop the application:**
   - Press `Ctrl+C` to stop
   - Run `docker-compose down` to remove containers
   - Run `docker-compose down -v` to also remove data volumes

Docker Compose will automatically:
- Set up PostgreSQL with pgvector extension
- Create the necessary databases (chatbot_db and hyrex)
- Initialize the database schema
- Start the API server on port 8000
- Start the Hyrex worker for background tasks
- Mount the frontend for serving via the API

## Manual Setup

If you prefer to run the services manually without Docker:

### Prerequisites

- PostgreSQL with pgvector extension installed
- OpenAI API key
- Python 3.11+

### Setup

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

### Running the Application

You'll need three terminal windows:

#### Terminal 1: Start the Hyrex worker
```bash
hyrex run-worker hyrex_app:app
```

#### Terminal 2: Run the FastAPI server
```bash
python api.py
```
The API will be available at http://localhost:8000

#### Terminal 3: Open the chat interface
```bash
open frontend/index.html
```
Or simply open `frontend/index.html` in your web browser.

## How It Works

- **Hyrex Worker**: Processes messages asynchronously, retrieves memories, and extracts new facts
- **API Server**: Handles HTTP requests and queues tasks for the worker
- **Frontend**: Simple HTML interface with polling for real-time message updates

The chatbot remembers facts about users across conversations using semantic search on embeddings stored in PostgreSQL.
