#!/usr/bin/env python3
"""Clear all data from the database for testing purposes."""

import os
import sys
from pathlib import Path

# Add parent directory to path to import chatbot module
sys.path.insert(0, str(Path(__file__).parent.parent))

from chatbot import ChatDatabase

def clear_database():
    """Clear all data from the database."""
    db = ChatDatabase()
    
    with db.get_cursor() as cursor:
        print("Clearing database...")
        
        # Delete all memories first (due to foreign key constraints)
        cursor.execute("DELETE FROM memories")
        count = cursor.rowcount
        print(f"  Deleted {count} memories")
        
        # Delete all messages
        cursor.execute("DELETE FROM messages")
        count = cursor.rowcount
        print(f"  Deleted {count} messages")
        
        # Delete all conversations
        cursor.execute("DELETE FROM conversations")
        count = cursor.rowcount
        print(f"  Deleted {count} conversations")
        
        # Reset the auto-increment sequences
        cursor.execute("ALTER SEQUENCE conversations_id_seq RESTART WITH 1")
        cursor.execute("ALTER SEQUENCE messages_id_seq RESTART WITH 1")
        cursor.execute("ALTER SEQUENCE memories_id_seq RESTART WITH 1")
        print("  Reset ID sequences")
        
        print("\nDatabase cleared successfully!")

if __name__ == "__main__":
    response = input("This will DELETE ALL DATA from the database. Are you sure? (yes/no): ")
    if response.lower() == 'yes':
        clear_database()
    else:
        print("Cancelled.")