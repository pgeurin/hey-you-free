#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database infrastructure for the Meeting Scheduler application
"""
import sqlite3
import json
import os
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from contextlib import contextmanager


class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self, db_path: str):
        """Initialize database manager with SQLite database path"""
        self.db_path = db_path
        self.connection = None
    
    def connect(self):
        """Establish database connection"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row  # Enable dict-like access
        return self.connection
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def is_connected(self) -> bool:
        """Check if database is connected"""
        return self.connection is not None
    
    @contextmanager
    def transaction(self):
        """Context manager for database transactions"""
        if not self.connection:
            self.connect()
        
        # Start transaction
        self.connection.execute("BEGIN TRANSACTION")
        
        try:
            yield self.connection
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
    
    def initialize_database(self):
        """Initialize database with schema"""
        if not self.connection:
            self.connect()
        
        schema_sql = """
        -- Users table
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            calendar_name VARCHAR(255) NOT NULL,
            calendar_id VARCHAR(255) NOT NULL,
            is_primary BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Conversation contexts (for AI context)
        CREATE TABLE IF NOT EXISTS conversation_contexts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user1_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            user2_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            context_text TEXT,
            context_type VARCHAR(50) DEFAULT 'meeting_discussion',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP
        );

        -- Messages table (for text/SMS integration)
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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

        -- Conversations table (groups messages between users)
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user1_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            user2_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            conversation_type VARCHAR(50) DEFAULT 'meeting_coordination',
            status VARCHAR(20) DEFAULT 'active',
            last_message_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user1_id, user2_id)
        );

        -- Meeting suggestions (AI-generated)
        CREATE TABLE IF NOT EXISTS meeting_suggestions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
            user1_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            user2_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            suggestion_data JSON NOT NULL,
            status VARCHAR(20) DEFAULT 'pending',
            expires_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Script templates (for structured conversations)
        CREATE TABLE IF NOT EXISTS script_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) UNIQUE NOT NULL,
            description TEXT,
            script_data JSON NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
        """
        
        cursor = self.connection.cursor()
        cursor.executescript(schema_sql)
        self.connection.commit()
    
    # User CRUD operations
    def create_user(self, name: str, calendar_id: str, phone_number: Optional[str] = None,
                   email: Optional[str] = None, oauth_token: Optional[str] = None,
                   refresh_token: Optional[str] = None, timezone: str = 'America/Los_Angeles') -> int:
        """Create a new user"""
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO users (name, phone_number, email, calendar_id, oauth_token, 
                             refresh_token, timezone)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, phone_number, email, calendar_id, oauth_token, refresh_token, timezone))
        
        # Don't commit here - let the transaction context manager handle it
        return cursor.lastrowid
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_user_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get user by name"""
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE name = ?", (name,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_user_by_phone(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """Get user by phone number"""
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE phone_number = ?", (phone_number,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def update_user(self, user_id: int, **kwargs) -> bool:
        """Update user information"""
        if not self.connection:
            self.connect()
        
        # Build dynamic update query
        valid_fields = ['name', 'phone_number', 'email', 'calendar_id', 
                       'oauth_token', 'refresh_token', 'timezone', 'is_active']
        
        update_fields = []
        values = []
        
        for field, value in kwargs.items():
            if field in valid_fields:
                update_fields.append(f"{field} = ?")
                values.append(value)
        
        if not update_fields:
            return False
        
        # Add updated_at timestamp
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        values.append(user_id)
        
        query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
        
        cursor = self.connection.cursor()
        cursor.execute(query, values)
        self.connection.commit()
        
        return cursor.rowcount > 0
    
    def delete_user(self, user_id: int) -> bool:
        """Delete a user"""
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        self.connection.commit()
        
        return cursor.rowcount > 0
    
    def list_users(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """List all users"""
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor()
        if active_only:
            cursor.execute("SELECT * FROM users WHERE is_active = TRUE ORDER BY name")
        else:
            cursor.execute("SELECT * FROM users ORDER BY name")
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    # Conversation context operations
    def store_conversation_context(self, user1_id: int, user2_id: int, 
                                 context_text: str, context_type: str = 'meeting_discussion',
                                 expires_at: Optional[datetime] = None) -> int:
        """Store conversation context"""
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO conversation_contexts (user1_id, user2_id, context_text, 
                                             context_type, expires_at)
            VALUES (?, ?, ?, ?, ?)
        """, (user1_id, user2_id, context_text, context_type, expires_at))
        
        self.connection.commit()
        return cursor.lastrowid
    
    def get_conversation_context(self, user1_id: int, user2_id: int) -> Optional[Dict[str, Any]]:
        """Get conversation context between two users"""
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM conversation_contexts 
            WHERE user1_id = ? AND user2_id = ? 
            ORDER BY created_at DESC LIMIT 1
        """, (user1_id, user2_id))
        
        row = cursor.fetchone()
        return dict(row) if row else None
    
    # Conversation operations
    def create_conversation(self, user1_id: int, user2_id: int, 
                          conversation_type: str = 'meeting_coordination') -> int:
        """Create a conversation between two users"""
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO conversations (user1_id, user2_id, conversation_type)
            VALUES (?, ?, ?)
        """, (user1_id, user2_id, conversation_type))
        
        self.connection.commit()
        return cursor.lastrowid
    
    def get_conversation(self, user1_id: int, user2_id: int) -> Optional[Dict[str, Any]]:
        """Get conversation between two users"""
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM conversations 
            WHERE user1_id = ? AND user2_id = ?
        """, (user1_id, user2_id))
        
        row = cursor.fetchone()
        return dict(row) if row else None
    
    # Meeting suggestion operations
    def store_meeting_suggestion(self, conversation_id: int, user1_id: int, user2_id: int,
                               suggestion_data: Dict[str, Any], status: str = 'pending',
                               expires_at: Optional[datetime] = None) -> int:
        """Store meeting suggestion"""
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO meeting_suggestions (conversation_id, user1_id, user2_id, 
                                           suggestion_data, status, expires_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (conversation_id, user1_id, user2_id, json.dumps(suggestion_data), status, expires_at))
        
        self.connection.commit()
        return cursor.lastrowid
    
    def get_meeting_suggestion(self, suggestion_id: int) -> Optional[Dict[str, Any]]:
        """Get meeting suggestion by ID"""
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM meeting_suggestions WHERE id = ?", (suggestion_id,))
        row = cursor.fetchone()
        
        if row:
            result = dict(row)
            result['suggestion_data'] = json.loads(result['suggestion_data'])
            return result
        return None
    
    def get_meeting_suggestions_for_conversation(self, conversation_id: int) -> List[Dict[str, Any]]:
        """Get all meeting suggestions for a conversation"""
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM meeting_suggestions 
            WHERE conversation_id = ? 
            ORDER BY created_at DESC
        """, (conversation_id,))
        
        rows = cursor.fetchall()
        results = []
        for row in rows:
            result = dict(row)
            result['suggestion_data'] = json.loads(result['suggestion_data'])
            results.append(result)
        
        return results


# Data model classes for type hints
class User:
    """User data model"""
    def __init__(self, id: int, name: str, calendar_id: str, **kwargs):
        self.id = id
        self.name = name
        self.calendar_id = calendar_id
        self.phone_number = kwargs.get('phone_number')
        self.email = kwargs.get('email')
        self.oauth_token = kwargs.get('oauth_token')
        self.refresh_token = kwargs.get('refresh_token')
        self.timezone = kwargs.get('timezone', 'America/Los_Angeles')
        self.is_active = kwargs.get('is_active', True)


class Conversation:
    """Conversation data model"""
    def __init__(self, id: int, user1_id: int, user2_id: int, **kwargs):
        self.id = id
        self.user1_id = user1_id
        self.user2_id = user2_id
        self.conversation_type = kwargs.get('conversation_type', 'meeting_coordination')
        self.status = kwargs.get('status', 'active')


class MeetingSuggestion:
    """Meeting suggestion data model"""
    def __init__(self, id: int, conversation_id: int, user1_id: int, user2_id: int, 
                 suggestion_data: Dict[str, Any], **kwargs):
        self.id = id
        self.conversation_id = conversation_id
        self.user1_id = user1_id
        self.user2_id = user2_id
        self.suggestion_data = suggestion_data
        self.status = kwargs.get('status', 'pending')
