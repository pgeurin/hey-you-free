#!/usr/bin/env python3
"""
Add oauth_states table to existing database
Run this script to migrate existing databases
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from infrastructure.database_postgres import get_database_manager

def add_oauth_states_table():
    """Add oauth_states table to database"""
    try:
        db = get_database_manager()
        
        if not db.is_connected():
            db.connect()
        
        cursor = db.connection.cursor()
        
        # Create oauth_states table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS oauth_states (
            state_key VARCHAR(255) PRIMARY KEY,
            state_data TEXT NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        cursor.execute(create_table_sql)
        print("✅ Created oauth_states table")
        
        # Create index
        create_index_sql = """
        CREATE INDEX IF NOT EXISTS idx_oauth_states_expires ON oauth_states(expires_at);
        """
        
        cursor.execute(create_index_sql)
        print("✅ Created oauth_states index")
        
        db.connection.commit()
        cursor.close()
        
        print("✅ OAuth states table migration completed successfully")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    add_oauth_states_table()
