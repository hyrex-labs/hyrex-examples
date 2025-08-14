#!/usr/bin/env python
"""Run the memories migration."""

import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

def run_migration():
    """Run the add_memories.sql migration."""
    db_url = os.environ["CHAT_DATABASE_URL"]
    
    # Read migration file
    with open("add_memories.sql", "r") as f:
        migration_sql = f.read()
    
    # Connect and run migration
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cursor:
            cursor.execute(migration_sql)
            conn.commit()
    
    print("✅ Memory system migration completed successfully!")

if __name__ == "__main__":
    run_migration()