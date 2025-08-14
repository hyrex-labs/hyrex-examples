-- Migration to add memory system

-- Enable pgvector extension for embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- Memories table for storing facts with embeddings
CREATE TABLE IF NOT EXISTS memories (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    fact TEXT NOT NULL,
    embedding vector(1536), -- OpenAI embeddings are 1536 dimensions
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for vector similarity searches (using ivfflat for approximate search)
CREATE INDEX IF NOT EXISTS idx_memories_embedding ON memories USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_memories_conversation_id ON memories(conversation_id);