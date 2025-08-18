# System Architecture

## Overview
This chatbot system uses a microservices architecture with Docker Compose orchestration, async task processing, and vector-based memory storage.

## Architecture Diagram

```mermaid
graph TB
    subgraph "Docker Compose Environment"
        subgraph "PostgreSQL Container"
            DB[(PostgreSQL<br/>+ pgvector)]
            DB --> |stores| CONV[Conversations]
            DB --> |stores| MSG[Messages]
            DB --> |stores| MEM[Memories<br/>+ Embeddings]
        end
        
        subgraph "API Container"
            API[FastAPI Server<br/>Port 8000]
            API --> |reads/writes| DB
        end
        
        subgraph "Worker Container"
            WORKER[Hyrex Worker]
            WORKER --> |processes tasks| DB
        end
        
        API --> |enqueues tasks| HYREX[(Hyrex Queue<br/>in PostgreSQL)]
        WORKER --> |consumes tasks| HYREX
    end
    
    CLIENT[Web Browser<br/>Frontend]
    CLIENT --> |HTTP/REST| API
    
    WORKER --> |API calls| OPENAI[OpenAI API<br/>GPT-4/GPT-5<br/>Embeddings]
    
    CLIENT -.-> |serves static files| FRONTEND[/frontend<br/>index.html]
    API --> |mounts| FRONTEND
    
    style DB fill:#4A90E2
    style API fill:#50C878
    style WORKER fill:#FFB347
    style CLIENT fill:#DDA0DD
    style OPENAI fill:#FF6B6B
    style HYREX fill:#4A90E2
```

## Components

### 1. PostgreSQL Database
- **Technology**: PostgreSQL with pgvector extension
- **Purpose**: Persistent storage for all application data
- **Stores**:
  - Conversations (chat sessions)
  - Messages (user and assistant messages)
  - Memories (extracted facts with vector embeddings)

### 2. FastAPI Server
- **Port**: 8000
- **Responsibilities**:
  - REST API endpoints for CRUD operations
  - Serves static frontend files
  - Enqueues async tasks to Hyrex
  - Real-time message retrieval

### 3. Hyrex Worker
- **Purpose**: Async task processing
- **Tasks**:
  - Process user messages with OpenAI
  - Extract and store memories
  - Semantic memory search
  - Memory consolidation (scheduled)

### 4. Web Frontend
- **Technology**: Vanilla JavaScript, HTML, CSS
- **Features**:
  - Chat interface
  - Conversation management
  - Memory bank viewer
  - Real-time updates via polling

### 5. External Services
- **OpenAI API**:
  - GPT-4/GPT-5 for chat completions
  - Ada-002 for text embeddings
  - Structured output for memory analysis

## Data Flow

1. **User sends message** → Web Frontend
2. **Frontend calls API** → POST /api/conversations/{id}/messages
3. **API stores message** → PostgreSQL
4. **API enqueues task** → Hyrex Queue
5. **Worker picks up task** → Processes with OpenAI
6. **Worker stores response** → PostgreSQL
7. **Frontend polls for updates** → GET /api/conversations/{id}/messages
8. **Memory extraction** → Async task extracts facts from conversation
9. **Memory search** → Vector similarity search for relevant context

## Key Features

- **Async Processing**: Non-blocking message handling
- **Vector Search**: Semantic memory retrieval using embeddings
- **Memory Persistence**: Facts survive conversation deletion
- **Containerization**: Easy deployment and scaling
- **Task Queue**: Reliable background job processing