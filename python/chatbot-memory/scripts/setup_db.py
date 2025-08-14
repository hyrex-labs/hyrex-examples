#!/usr/bin/env python
"""Setup script to create database tables."""

import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

def setup_database():
    """Create all database tables from schema.sql."""
    db_url = os.environ["CHAT_DATABASE_URL"]
    
    # Read schema file
    with open("../chatbot/schema.sql", "r") as f:
        schema_sql = f.read()
    
    # Connect and create tables
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cursor:
            cursor.execute(schema_sql)
            conn.commit()
    
    print("✅ Database tables created successfully!")

if __name__ == "__main__":
    setup_database()