from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)