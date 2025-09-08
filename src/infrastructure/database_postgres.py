#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PostgreSQL database infrastructure for the Meeting Scheduler application
"""
import os
import json
import psycopg2
import psycopg2.extras
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from contextlib import contextmanager
from urllib.parse import urlparse


class PostgreSQLDatabaseManager:
    """Manages PostgreSQL database connections and operations"""
    
    def __init__(self, database_url: str):
        """Initialize database manager with PostgreSQL database URL"""
        self.database_url = database_url
        self.connection = None
        self._parse_database_url()
    
    def _parse_database_url(self):
        """Parse database URL to extract connection parameters"""
        if not self.database_url:
            raise ValueError("Database URL is required")
        
        parsed = urlparse(self.database_url)
        self.db_config = {
            'host': parsed.hostname,
            'port': parsed.port or 5432,
            'database': parsed.path[1:] if parsed.path else 'postgres',
            'user': parsed.username,
            'password': parsed.password,
        }
        
        # Handle Cloud SQL Unix socket connections
        if parsed.hostname and parsed.hostname.startswith('/cloudsql/'):
            self.db_config['host'] = parsed.hostname
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = psycopg2.connect(
                **self.db_config,
                cursor_factory=psycopg2.extras.RealDictCursor
            )
            return self.connection
        except psycopg2.Error as e:
            raise ConnectionError(f"Failed to connect to PostgreSQL: {e}")
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def is_connected(self) -> bool:
        """Check if database is connected"""
        return self.connection is not None and not self.connection.closed
    
    @contextmanager
    def transaction(self):
        """Context manager for database transactions"""
        if not self.is_connected():
            self.connect()
        
        # Start transaction
        self.connection.autocommit = False
        
        try:
            yield self.connection
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            self.connection.autocommit = True
    
    def initialize_database(self):
        """Initialize database with schema"""
        if not self.is_connected():
            self.connect()
        
        schema_sql = """
        -- Users table
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) UNIQUE NOT NULL,
            phone_number VARCHAR(20) UNIQUE,
            email VARCHAR(255) UNIQUE,
            calendar_id VARCHAR(255) NOT NULL,
            oauth_token TEXT,
            refresh_token TEXT,
            timezone VARCHAR(50) DEFAULT 'America/Los_Angeles',
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Calendar mappings
        CREATE TABLE IF NOT EXISTS calendar_mappings (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            calendar_name VARCHAR(255) NOT NULL,
            calendar_id VARCHAR(255) NOT NULL,
            is_primary BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Conversation contexts (for AI context)
        CREATE TABLE IF NOT EXISTS conversation_contexts (
            id SERIAL PRIMARY KEY,
            user1_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            user2_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            context_text TEXT,
            context_type VARCHAR(50) DEFAULT 'meeting_discussion',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP
        );

        -- Conversations table (groups messages between users)
        CREATE TABLE IF NOT EXISTS conversations (
            id SERIAL PRIMARY KEY,
            user1_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            user2_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            conversation_type VARCHAR(50) DEFAULT 'meeting_coordination',
            status VARCHAR(20) DEFAULT 'active',
            last_message_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user1_id, user2_id)
        );

        -- Messages table (for text/SMS integration)
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
            sender_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            recipient_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            message_text TEXT NOT NULL,
            message_type VARCHAR(20) DEFAULT 'text',
            direction VARCHAR(10) NOT NULL,
            status VARCHAR(20) DEFAULT 'sent',
            external_message_id VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            read_at TIMESTAMP
        );

        -- Meeting suggestions (AI-generated)
        CREATE TABLE IF NOT EXISTS meeting_suggestions (
            id SERIAL PRIMARY KEY,
            conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
            user1_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            user2_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            suggestion_data JSONB NOT NULL,
            status VARCHAR(20) DEFAULT 'pending',
            expires_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Script templates (for structured conversations)
        CREATE TABLE IF NOT EXISTS script_templates (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) UNIQUE NOT NULL,
            description TEXT,
            script_data JSONB NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Suggested friends table
        CREATE TABLE IF NOT EXISTS suggested_friends (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            suggested_user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            status VARCHAR(20) DEFAULT 'suggested',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, suggested_user_id)
        );

        -- Indexes for performance
        CREATE INDEX IF NOT EXISTS idx_users_name ON users(name);
        CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone_number);
        CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);
        CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages(sender_id);
        CREATE INDEX IF NOT EXISTS idx_messages_recipient ON messages(recipient_id);
        CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);
        CREATE INDEX IF NOT EXISTS idx_conversations_users ON conversations(user1_id, user2_id);
        CREATE INDEX IF NOT EXISTS idx_conversation_contexts_users ON conversation_contexts(user1_id, user2_id);
        CREATE INDEX IF NOT EXISTS idx_meeting_suggestions_conversation ON meeting_suggestions(conversation_id);
        CREATE INDEX IF NOT EXISTS idx_suggested_friends_user ON suggested_friends(user_id);
        CREATE INDEX IF NOT EXISTS idx_suggested_friends_suggested ON suggested_friends(suggested_user_id);
        
        -- JSONB indexes for better performance
        CREATE INDEX IF NOT EXISTS idx_meeting_suggestions_data ON meeting_suggestions USING GIN (suggestion_data);
        CREATE INDEX IF NOT EXISTS idx_script_templates_data ON script_templates USING GIN (script_data);
        """
        
        cursor = self.connection.cursor()
        cursor.execute(schema_sql)
        self.connection.commit()
        cursor.close()
    
    # User CRUD operations
    def create_user(self, name: str, calendar_id: str, phone_number: Optional[str] = None,
                   email: Optional[str] = None, oauth_token: Optional[str] = None,
                   refresh_token: Optional[str] = None, timezone: str = 'America/Los_Angeles') -> int:
        """Create a new user"""
        if not self.is_connected():
            self.connect()
        
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO users (name, phone_number, email, calendar_id, oauth_token, 
                             refresh_token, timezone)
            VALUES (%(name)s, %(phone_number)s, %(email)s, %(calendar_id)s, %(oauth_token)s, 
                    %(refresh_token)s, %(timezone)s)
            RETURNING id
        """, {
            'name': name,
            'phone_number': phone_number,
            'email': email,
            'calendar_id': calendar_id,
            'oauth_token': oauth_token,
            'refresh_token': refresh_token,
            'timezone': timezone
        })
        
        user_id = cursor.fetchone()['id']
        cursor.close()
        return user_id
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        if not self.is_connected():
            self.connect()
        
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %(user_id)s", {'user_id': user_id})
        row = cursor.fetchone()
        cursor.close()
        return dict(row) if row else None
    
    def get_user_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get user by name"""
        if not self.is_connected():
            self.connect()
        
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE name = %(name)s", {'name': name})
        row = cursor.fetchone()
        cursor.close()
        return dict(row) if row else None
    
    def get_user_by_phone(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """Get user by phone number"""
        if not self.is_connected():
            self.connect()
        
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE phone_number = %(phone_number)s", 
                      {'phone_number': phone_number})
        row = cursor.fetchone()
        cursor.close()
        return dict(row) if row else None
    
    def update_user(self, user_id: int, **kwargs) -> bool:
        """Update user information"""
        if not self.is_connected():
            self.connect()
        
        # Build dynamic update query
        valid_fields = ['name', 'phone_number', 'email', 'calendar_id', 
                       'oauth_token', 'refresh_token', 'timezone', 'is_active']
        
        update_fields = []
        values = {'user_id': user_id}
        
        for field, value in kwargs.items():
            if field in valid_fields:
                update_fields.append(f"{field} = %({field})s")
                values[field] = value
        
        if not update_fields:
            return False
        
        # Add updated_at timestamp
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        
        query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %(user_id)s"
        
        cursor = self.connection.cursor()
        cursor.execute(query, values)
        self.connection.commit()
        cursor.close()
        
        return cursor.rowcount > 0
    
    def delete_user(self, user_id: int) -> bool:
        """Delete a user"""
        if not self.is_connected():
            self.connect()
        
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM users WHERE id = %(user_id)s", {'user_id': user_id})
        self.connection.commit()
        cursor.close()
        
        return cursor.rowcount > 0
    
    def list_users(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """List all users"""
        if not self.is_connected():
            self.connect()
        
        cursor = self.connection.cursor()
        if active_only:
            cursor.execute("SELECT * FROM users WHERE is_active = TRUE ORDER BY name")
        else:
            cursor.execute("SELECT * FROM users ORDER BY name")
        
        rows = cursor.fetchall()
        cursor.close()
        return [dict(row) for row in rows]
    
    # Meeting suggestion operations
    def store_meeting_suggestion(self, conversation_id: int, user1_id: int, user2_id: int,
                               suggestion_data: Dict[str, Any], status: str = 'pending',
                               expires_at: Optional[datetime] = None) -> int:
        """Store meeting suggestion"""
        if not self.is_connected():
            self.connect()
        
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO meeting_suggestions (conversation_id, user1_id, user2_id, 
                                           suggestion_data, status, expires_at)
            VALUES (%(conversation_id)s, %(user1_id)s, %(user2_id)s, %(suggestion_data)s, 
                    %(status)s, %(expires_at)s)
            RETURNING id
        """, {
            'conversation_id': conversation_id,
            'user1_id': user1_id,
            'user2_id': user2_id,
            'suggestion_data': json.dumps(suggestion_data),
            'status': status,
            'expires_at': expires_at
        })
        
        suggestion_id = cursor.fetchone()['id']
        self.connection.commit()
        cursor.close()
        return suggestion_id
    
    def get_meeting_suggestion(self, suggestion_id: int) -> Optional[Dict[str, Any]]:
        """Get meeting suggestion by ID"""
        if not self.is_connected():
            self.connect()
        
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM meeting_suggestions WHERE id = %(suggestion_id)s", 
                      {'suggestion_id': suggestion_id})
        row = cursor.fetchone()
        cursor.close()
        
        if row:
            result = dict(row)
            result['suggestion_data'] = json.loads(result['suggestion_data'])
            return result
        return None
    
    def get_meeting_suggestions_for_conversation(self, conversation_id: int) -> List[Dict[str, Any]]:
        """Get all meeting suggestions for a conversation"""
        if not self.is_connected():
            self.connect()
        
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM meeting_suggestions 
            WHERE conversation_id = %(conversation_id)s 
            ORDER BY created_at DESC
        """, {'conversation_id': conversation_id})
        
        rows = cursor.fetchall()
        cursor.close()
        
        results = []
        for row in rows:
            result = dict(row)
            result['suggestion_data'] = json.loads(result['suggestion_data'])
            results.append(result)
        
        return results
    
    # Conversation operations
    def create_conversation(self, user1_id: int, user2_id: int, 
                          conversation_type: str = 'meeting_coordination') -> int:
        """Create a conversation between two users"""
        if not self.is_connected():
            self.connect()
        
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO conversations (user1_id, user2_id, conversation_type)
            VALUES (%(user1_id)s, %(user2_id)s, %(conversation_type)s)
            RETURNING id
        """, {
            'user1_id': user1_id,
            'user2_id': user2_id,
            'conversation_type': conversation_type
        })
        
        conversation_id = cursor.fetchone()['id']
        self.connection.commit()
        cursor.close()
        return conversation_id
    
    def get_conversation(self, user1_id: int, user2_id: int) -> Optional[Dict[str, Any]]:
        """Get conversation between two users"""
        if not self.is_connected():
            self.connect()
        
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM conversations 
            WHERE user1_id = %(user1_id)s AND user2_id = %(user2_id)s
        """, {'user1_id': user1_id, 'user2_id': user2_id})
        
        row = cursor.fetchone()
        cursor.close()
        return dict(row) if row else None
    
    # Conversation context operations
    def store_conversation_context(self, user1_id: int, user2_id: int, 
                                 context_text: str, context_type: str = 'meeting_discussion',
                                 expires_at: Optional[datetime] = None) -> int:
        """Store conversation context"""
        if not self.is_connected():
            self.connect()
        
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO conversation_contexts (user1_id, user2_id, context_text, 
                                             context_type, expires_at)
            VALUES (%(user1_id)s, %(user2_id)s, %(context_text)s, %(context_type)s, %(expires_at)s)
            RETURNING id
        """, {
            'user1_id': user1_id,
            'user2_id': user2_id,
            'context_text': context_text,
            'context_type': context_type,
            'expires_at': expires_at
        })
        
        context_id = cursor.fetchone()['id']
        self.connection.commit()
        cursor.close()
        return context_id
    
    def get_conversation_context(self, user1_id: int, user2_id: int) -> Optional[Dict[str, Any]]:
        """Get conversation context between two users"""
        if not self.is_connected():
            self.connect()
        
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM conversation_contexts 
            WHERE user1_id = %(user1_id)s AND user2_id = %(user2_id)s 
            ORDER BY created_at DESC LIMIT 1
        """, {'user1_id': user1_id, 'user2_id': user2_id})
        
        row = cursor.fetchone()
        cursor.close()
        return dict(row) if row else None
    
    # Suggested friends operations
    def add_suggested_friend(self, user_id: int, suggested_user_id: int) -> int:
        """Add a suggested friend relationship"""
        if not self.is_connected():
            self.connect()
        
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO suggested_friends (user_id, suggested_user_id, status)
            VALUES (%(user_id)s, %(suggested_user_id)s, 'suggested')
            RETURNING id
        """, {'user_id': user_id, 'suggested_user_id': suggested_user_id})
        
        friend_id = cursor.fetchone()['id']
        self.connection.commit()
        cursor.close()
        return friend_id
    
    def get_suggested_friends(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all suggested friends for a user"""
        if not self.is_connected():
            self.connect()
        
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT sf.*, u.name, u.email, u.phone_number
            FROM suggested_friends sf
            JOIN users u ON sf.suggested_user_id = u.id
            WHERE sf.user_id = %(user_id)s AND sf.status = 'suggested'
            ORDER BY sf.created_at DESC
        """, {'user_id': user_id})
        
        rows = cursor.fetchall()
        cursor.close()
        return [dict(row) for row in rows]
    
    def update_suggested_friend_status(self, user_id: int, suggested_user_id: int, status: str) -> bool:
        """Update the status of a suggested friend relationship"""
        if not self.is_connected():
            self.connect()
        
        cursor = self.connection.cursor()
        cursor.execute("""
            UPDATE suggested_friends 
            SET status = %(status)s, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %(user_id)s AND suggested_user_id = %(suggested_user_id)s
        """, {
            'status': status,
            'user_id': user_id,
            'suggested_user_id': suggested_user_id
        })
        
        self.connection.commit()
        cursor.close()
        return cursor.rowcount > 0


def get_database_manager():
    """Factory function to get the appropriate database manager"""
    database_url = os.getenv('DATABASE_URL')
    
    if database_url and database_url.startswith('postgresql://'):
        return PostgreSQLDatabaseManager(database_url)
    else:
        # Fallback to SQLite for development
        from .database import DatabaseManager
        db_path = os.getenv('DATABASE_URL', 'sqlite:///./meeting_scheduler.db')
        if db_path.startswith('sqlite:///'):
            db_path = db_path[10:]  # Remove 'sqlite:///' prefix
        return DatabaseManager(db_path)
