# Chatbot Architecture Flow

## System Architecture

```mermaid
graph TB
    subgraph "Frontend"
        HTML[index.html<br/>Single Page App]
        POLL[Polling Loop<br/>Every 2 seconds]
    end
    
    subgraph "API Layer"
        FAST[FastAPI Server<br/>Port 8000]
    end
    
    subgraph "Task Queue"
        HYREX[Hyrex Task Queue]
        WORKER[Worker Process]
    end
    
    subgraph "External Services"
        OPENAI[OpenAI API]
        EMBED[Embeddings API<br/>text-embedding-ada-002]
        GPT5[GPT-5 Model]
        GPT4[GPT-4 Model]
    end
    
    subgraph "Database"
        PG[(PostgreSQL)]
        CONV[conversations table]
        MSG[messages table]
        MEM[memories table<br/>with pgvector]
    end
    
    HTML -->|POST message| FAST
    FAST -->|Queue task| HYREX
    FAST -->|Store message| MSG
    HYREX -->|Process| WORKER
    WORKER -->|Embeddings| EMBED
    WORKER -->|Search similar| MEM
    WORKER -->|Get history| MSG
    WORKER -->|Generate response| GPT5
    WORKER -->|Store response| MSG
    WORKER -->|Extract facts| GPT4
    WORKER -->|Store memories| MEM
    POLL -->|GET messages| FAST
    FAST -->|Query| MSG
```

## Message Processing Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant DB
    participant Hyrex
    participant Worker
    participant OpenAI
    
    User->>Frontend: Type message & Send
    Frontend->>Frontend: Show user message
    Frontend->>Frontend: Show "Working..."
    Frontend->>API: POST /conversations/{id}/messages
    API->>DB: store user message
    API->>Hyrex: process_message.send()
    API-->>Frontend: 200 OK (immediate)
    
    Note over Frontend: Start polling every 2s
    
    Hyrex->>Worker: Dequeue task
    Worker->>OpenAI: Generate embedding
    OpenAI-->>Worker: Return embedding
    Worker->>DB: Search memories (vector similarity)
    DB-->>Worker: 3 relevant + 2 random memories
    Worker->>DB: Get last 10 messages
    DB-->>Worker: Conversation history
    Worker->>OpenAI: Call GPT-5 with context
    OpenAI-->>Worker: Assistant response
    Worker->>DB: Store assistant message
    Worker->>Hyrex: extract_memories.send()
    
    Frontend->>API: GET /conversations/{id}/messages
    API->>DB: Query messages
    DB-->>API: All messages
    API-->>Frontend: Messages JSON
    Frontend->>Frontend: Remove "Working..."
    Frontend->>Frontend: Show assistant response
    
    Note over Hyrex,Worker: Async memory extraction
    Hyrex->>Worker: Dequeue memory task
    Worker->>OpenAI: Extract facts (GPT-4)
    OpenAI-->>Worker: User facts
    Worker->>OpenAI: Generate embeddings
    OpenAI-->>Worker: Fact embeddings
    Worker->>DB: Store memories + vectors
```

## Memory Search Flow

```mermaid
graph LR
    subgraph "Memory Retrieval"
        UMSG[User Message]
        UMSG -->|text-embedding-ada-002| EMBED[Generate Embedding]
        EMBED --> VEC[1536-dim vector]
        
        VEC -->|Cosine similarity| SEARCH[Vector Search]
        SEARCH -->|IVFFlat index| MEM[(memories table)]
        
        MEM -->|Top 3| REL[Relevant Memories]
        MEM -->|ORDER BY RANDOM| RND[2 Random Memories]
        
        REL --> PROMPT[GPT-5 System Prompt]
        RND --> PROMPT
    end
```

## Key Characteristics

- **Non-blocking**: API returns immediately after queuing
- **Async Processing**: Hyrex handles all heavy computation
- **Polling-based Updates**: Frontend discovers completion via polling
- **Dual Memory Selection**: Semantic search + random for serendipity
- **Parallel Tasks**: Memory extraction happens independently
- **Vector Search**: pgvector with IVFFlat indexing for fast similarity
- **Global Memory Bank**: Memories shared across all conversations