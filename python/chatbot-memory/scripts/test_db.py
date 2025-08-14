#!/usr/bin/env python
"""Test script to check if messages are being saved correctly."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from chatbot import ChatDatabase

load_dotenv()

db = ChatDatabase()

# Get the most recent conversation
conversations = db.get_recent_conversations(1)
if conversations:
    conv_id = conversations[0]['id']
    print(f"Checking conversation {conv_id}")
    
    # Get all messages
    messages = db.get_conversation_history(conv_id)
    print(f"\nFound {len(messages)} messages:")
    for msg in messages:
        print(f"  [{msg['role']}]: {msg['content'][:50]}...")
else:
    print("No conversations found")