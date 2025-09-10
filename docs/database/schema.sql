-- AI-Powered Event Scheduling Application Database Schema
-- Version: 1.0
-- Last Updated: 2025-01-15

-- Users table
CREATE TABLE users (
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
CREATE TABLE calendar_mappings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    calendar_name VARCHAR(255) NOT NULL,
    calendar_id VARCHAR(255) NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Conversation contexts (for AI context)
CREATE TABLE conversation_contexts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user1_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    user2_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    context_text TEXT,
    context_type VARCHAR(50) DEFAULT 'meeting_discussion', -- meeting_discussion, coffee_chat, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

-- Messages table (for text/SMS integration)
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
    sender_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    recipient_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    message_text TEXT NOT NULL,
    message_type VARCHAR(20) DEFAULT 'text', -- text, sms, ai_response
    direction VARCHAR(10) NOT NULL, -- inbound, outbound
    status VARCHAR(20) DEFAULT 'sent', -- sent, delivered, read, failed
    external_message_id VARCHAR(255), -- Twilio message ID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP
);

-- Conversations table (groups messages between users)
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user1_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    user2_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    conversation_type VARCHAR(50) DEFAULT 'meeting_coordination',
    status VARCHAR(20) DEFAULT 'active', -- active, completed, archived
    last_message_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user1_id, user2_id)
);

-- Meeting suggestions (AI-generated)
CREATE TABLE meeting_suggestions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
    user1_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    user2_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    suggestion_data JSON NOT NULL, -- Full AI response
    status VARCHAR(20) DEFAULT 'pending', -- pending, accepted, declined, expired
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Script templates (for structured conversations)
CREATE TABLE script_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    script_data JSON NOT NULL, -- Conversation flow structure
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Suggested friends table
CREATE TABLE suggested_friends (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    suggested_user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'suggested', -- suggested, accepted, declined, removed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, suggested_user_id)
);

-- OAuth states table (for secure OAuth flow)
CREATE TABLE oauth_states (
    state_key VARCHAR(255) PRIMARY KEY,
    state_data TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_users_name ON users(name);
CREATE INDEX idx_users_phone ON users(phone_number);
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_sender ON messages(sender_id);
CREATE INDEX idx_messages_recipient ON messages(recipient_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_conversations_users ON conversations(user1_id, user2_id);
CREATE INDEX idx_conversation_contexts_users ON conversation_contexts(user1_id, user2_id);
CREATE INDEX idx_meeting_suggestions_conversation ON meeting_suggestions(conversation_id);
CREATE INDEX idx_suggested_friends_user ON suggested_friends(user_id);
CREATE INDEX idx_suggested_friends_suggested ON suggested_friends(suggested_user_id);
CREATE INDEX idx_oauth_states_expires ON oauth_states(expires_at);
