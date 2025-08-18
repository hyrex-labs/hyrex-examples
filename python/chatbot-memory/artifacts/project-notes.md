# Technical Project Log

## 2025-08-08

### Initial Setup
- Created Python virtual environment
- Installed Hyrex with `pip install hyrex`
- Ran `hyrex init` to create sample app
- Tested worker with example ETL tasks
- Created project documentation structure
- Established append-only log format for tracking design decisions and technical implementations

### Database Setup
- Created minimal Postgres schema with conversations and messages tables
- Built ChatDatabase class using psycopg3 with required CHAT_DATABASE_URL env var
- Schema includes conversation tracking with updated_at timestamps
- Added methods for creating conversations, adding messages, and retrieving history

### Code Organization
- Moved chatbot functionality into dedicated chatbot/ subdirectory
- Created __init__.py for clean imports
- Relocated db.py and schema.sql to chatbot/

### Database Instantiation
- Created scripts/ directory for utility scripts
- Added setup_db.py to create database tables from schema
- Successfully ran setup script with CHAT_DATABASE_URL from .env
- Tables created: conversations and messages with proper indexes

### Frontend & API
- Created FastAPI backend with endpoints for conversations and messages
- Added process_message Hyrex task
- Frontend sends user message to DB then triggers Hyrex task
- Single HTML file with sidebar for chat list, main area for messages
- Frontend polls every 2 seconds for new messages
- API at localhost:8000, serves CORS for frontend
- Added "Working..." loading animation

### ChatGPT Integration
- Added OpenAI library to requirements
- Updated process_message task to call ChatGPT API
- Limited conversation context to last 10 messages for performance
- Uses gpt-5 model without max_completion_tokens
- System prompt instructs concise responses
- Requires OPENAI_API_KEY environment variable
- Simple error message if response generation fails

### Memory System
- Added pgvector extension and memories table to store facts with embeddings
- Memory extraction focuses on facts ABOUT THE USER only
- Extracts user preferences, personal info, goals from each message
- Uses OpenAI text-embedding-ada-002 for generating 1536-dim embeddings
- Global memory bank shared across all conversations
- Retrieves 3 semantically similar + 2 random memories per query
- Memories labeled as "relevant" vs "random" in system prompt
- IVFFlat index with 100 lists for efficient similarity search
- Random selection uses ORDER BY RANDOM()
- Asynchronous extraction triggered after each assistant response
- Created migration script for adding pgvector to existing databases

### Performance Optimizations
- Moved OpenAI client and DB initialization to module level (not per-message)
- Database query limits conversation history to recent messages only
- Frontend shows "Working..." indicator while processing
- Removed unnecessary GPT-4 fallback calls
- Parallelized memory retrieval using Hyrex .send() and .wait()
  - Semantic search and random memory fetch run concurrently
  - Two new tasks: search_semantic_memories and get_random_memories
  - Reduces latency by running database queries in parallel

### Memory Consolidation System
- Added cron job that runs every 10 minutes to consolidate memories
- Samples 5 random memories and compares all pairs for duplicates
- Uses GPT-5 with structured outputs (Pydantic models) for analysis
- MemoryAction enum: KEEP_BOTH, CONSOLIDATE, DELETE_FIRST, DELETE_SECOND
- Automatically merges related memories into single, improved facts
- Deletes redundant or outdated memories to keep system clean
- Added delete_memory() method to ChatDatabase class
- Prevents memory bloat while maintaining important information

---
