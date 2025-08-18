from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import os

from chatbot import ChatDatabase
from tasks import process_message

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = ChatDatabase()

class MessageRequest(BaseModel):
    message: str

@app.get("/")
def root():
    """Redirect root to frontend."""
    return RedirectResponse(url="/frontend/")

@app.post("/api/conversations")
def create_conversation():
    """Create a new conversation."""
    conversation_id = db.create_conversation()
    return {"conversation_id": conversation_id}

@app.get("/api/conversations")
def get_conversations():
    """Get recent conversations."""
    conversations = db.get_recent_conversations()
    return conversations

@app.get("/api/conversations/{conversation_id}/messages")
def get_messages(conversation_id: int):
    """Get all messages in a conversation."""
    messages = db.get_conversation_history(conversation_id)
    return messages

@app.post("/api/conversations/{conversation_id}/messages")
def send_message(conversation_id: int, request: MessageRequest):
    """Send a message and trigger processing."""
    # Add user message to database
    db.add_message(conversation_id, "user", request.message)
    
    # Send task to process the message
    process_message.send(conversation_id, request.message)
    
    return {"status": "processing"}

@app.get("/api/memories")
def get_all_memories():
    """Get all memories across all conversations."""
    with db.get_cursor() as cursor:
        cursor.execute(
            """
            SELECT m.id, m.fact, m.created_at, m.conversation_id,
                   c.created_at as conversation_created_at
            FROM memories m
            LEFT JOIN conversations c ON m.conversation_id = c.id
            ORDER BY m.created_at DESC
            """
        )
        return cursor.fetchall()

@app.delete("/api/memories/{memory_id}")
def delete_memory(memory_id: int):
    """Delete a specific memory."""
    success = db.delete_memory(memory_id)
    if success:
        return {"status": "deleted"}
    else:
        raise HTTPException(status_code=404, detail="Memory not found")

@app.delete("/api/conversations/{conversation_id}")
def delete_conversation(conversation_id: int):
    """Delete a conversation and all its messages."""
    with db.get_cursor() as cursor:
        # Check if conversation exists
        cursor.execute("SELECT id FROM conversations WHERE id = %s", (conversation_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Delete all messages in the conversation
        cursor.execute("DELETE FROM messages WHERE conversation_id = %s", (conversation_id,))
        
        # Keep memories - they persist across conversations
        # cursor.execute("DELETE FROM memories WHERE conversation_id = %s", (conversation_id,))
        
        # Delete the conversation itself
        cursor.execute("DELETE FROM conversations WHERE id = %s", (conversation_id,))
        
        # Commit is handled by the context manager
        
    return {"status": "deleted"}

# Mount static files at the end, after all API routes
app.mount("/frontend", StaticFiles(directory="/app/frontend", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)