import os
from contextlib import contextmanager
from typing import List, Dict, Optional
import numpy as np
import psycopg
from psycopg.rows import dict_row
from pgvector.psycopg import register_vector


class ChatDatabase:
    def __init__(self):
        self.connection_string = os.environ["CHAT_DATABASE_URL"]
    
    @contextmanager
    def get_cursor(self):
        with psycopg.connect(self.connection_string) as conn:
            # Register pgvector extension
            register_vector(conn)
            with conn.cursor(row_factory=dict_row) as cursor:
                yield cursor
                conn.commit()
    
    def create_conversation(self) -> int:
        """Create a new conversation and return its ID."""
        with self.get_cursor() as cursor:
            cursor.execute(
                "INSERT INTO conversations DEFAULT VALUES RETURNING id"
            )
            return cursor.fetchone()["id"]
    
    def add_message(self, conversation_id: int, role: str, content: str) -> int:
        """Add a message to a conversation."""
        with self.get_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO messages (conversation_id, role, content)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (conversation_id, role, content)
            )
            message_id = cursor.fetchone()["id"]
            
            # Update conversation's updated_at
            cursor.execute(
                "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = %s",
                (conversation_id,)
            )
            
            return message_id
    
    def get_conversation_history(self, conversation_id: int, limit: Optional[int] = None) -> List[Dict]:
        """Get messages in a conversation, optionally limited to most recent."""
        with self.get_cursor() as cursor:
            if limit:
                # Get the most recent N messages
                cursor.execute(
                    """
                    SELECT * FROM (
                        SELECT id, role, content, created_at
                        FROM messages
                        WHERE conversation_id = %s
                        ORDER BY created_at DESC
                        LIMIT %s
                    ) AS recent_messages
                    ORDER BY created_at ASC
                    """,
                    (conversation_id, limit)
                )
            else:
                cursor.execute(
                    """
                    SELECT id, role, content, created_at
                    FROM messages
                    WHERE conversation_id = %s
                    ORDER BY created_at ASC
                    """,
                    (conversation_id,)
                )
            return cursor.fetchall()
    
    def get_recent_conversations(self, limit: int = 10) -> List[Dict]:
        """Get recent conversations with message count."""
        with self.get_cursor() as cursor:
            cursor.execute(
                """
                SELECT 
                    c.id,
                    c.created_at,
                    c.updated_at,
                    COUNT(m.id) as message_count,
                    MAX(m.content) FILTER (WHERE m.role = 'user') as last_user_message
                FROM conversations c
                LEFT JOIN messages m ON c.id = m.conversation_id
                GROUP BY c.id
                ORDER BY c.updated_at DESC
                LIMIT %s
                """,
                (limit,)
            )
            return cursor.fetchall()
    
    def add_memory(self, conversation_id: int, fact: str, embedding: List[float]) -> int:
        """Add a memory with its embedding."""
        with self.get_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO memories (conversation_id, fact, embedding)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (conversation_id, fact, embedding)
            )
            return cursor.fetchone()["id"]
    
    def search_memories(self, query_embedding: List[float], conversation_id: Optional[int] = None, limit: int = 5) -> List[Dict]:
        """Search for similar memories using cosine similarity."""
        with self.get_cursor() as cursor:
            if conversation_id:
                # Search within a specific conversation
                cursor.execute(
                    """
                    SELECT id, fact, conversation_id,
                           1 - (embedding <=> %s::vector) as similarity
                    FROM memories
                    WHERE conversation_id = %s
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                    """,
                    (query_embedding, conversation_id, query_embedding, limit)
                )
            else:
                # Search across all memories
                cursor.execute(
                    """
                    SELECT id, fact, conversation_id,
                           1 - (embedding <=> %s::vector) as similarity
                    FROM memories
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                    """,
                    (query_embedding, query_embedding, limit)
                )
            return cursor.fetchall()
    
    def get_conversation_memories(self, conversation_id: int) -> List[Dict]:
        """Get all memories for a conversation."""
        with self.get_cursor() as cursor:
            cursor.execute(
                """
                SELECT id, fact, created_at
                FROM memories
                WHERE conversation_id = %s
                ORDER BY created_at ASC
                """,
                (conversation_id,)
            )
            return cursor.fetchall()
    
    def get_random_memories(self, conversation_id: Optional[int] = None, limit: int = 2) -> List[Dict]:
        """Get random memories using TABLESAMPLE for performance."""
        with self.get_cursor() as cursor:
            # First check if we have enough memories
            if conversation_id:
                cursor.execute(
                    "SELECT COUNT(*) as count FROM memories WHERE conversation_id = %s",
                    (conversation_id,)
                )
            else:
                cursor.execute("SELECT COUNT(*) as count FROM memories")
            
            count = cursor.fetchone()["count"]
            
            if count == 0:
                return []
            
            # For small tables, just use ORDER BY RANDOM()
            # For larger tables, TABLESAMPLE would be more efficient
            if conversation_id:
                cursor.execute(
                    """
                    SELECT id, fact, conversation_id
                    FROM memories
                    WHERE conversation_id = %s
                    ORDER BY RANDOM()
                    LIMIT %s
                    """,
                    (conversation_id, limit)
                )
            else:
                cursor.execute(
                    """
                    SELECT id, fact, conversation_id
                    FROM memories
                    ORDER BY RANDOM()
                    LIMIT %s
                    """,
                    (limit,)
                )
            
            return cursor.fetchall()
    
    def delete_memory(self, memory_id: int) -> bool:
        """Delete a memory by ID."""
        with self.get_cursor() as cursor:
            cursor.execute(
                "DELETE FROM memories WHERE id = %s",
                (memory_id,)
            )
            return cursor.rowcount > 0