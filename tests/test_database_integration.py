#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for database integration functionality
"""
import pytest
import sqlite3
import tempfile
import os
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from infrastructure.database import DatabaseManager, User, Conversation, MeetingSuggestion


class TestDatabaseIntegration:
    """Test database integration functionality"""
    
    def setup_method(self):
        """Set up test database"""
        self.db_path = ":memory:"
        
        # Initialize database manager
        self.db_manager = DatabaseManager(self.db_path)
        self.db_manager.initialize_database()
    
    def teardown_method(self):
        """Clean up test database"""
        if hasattr(self, 'db_manager'):
            self.db_manager.close()
    
    def test_database_initialization(self):
        """Test that database initializes with correct schema"""
        # Check that all tables exist using the database manager's connection
        if not self.db_manager.is_connected():
            self.db_manager.connect()
        
        cursor = self.db_manager.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = [
            'users', 'calendar_mappings', 'conversation_contexts',
            'messages', 'conversations', 'meeting_suggestions', 'script_templates'
        ]
        
        for table in expected_tables:
            assert table in tables, f"Table {table} should exist"
    
    def test_user_creation(self):
        """Test creating a new user"""
        user_data = {
            'name': 'phil',
            'phone_number': '+1234567890',
            'email': 'phil@example.com',
            'calendar_id': 'phil@gmail.com',
            'oauth_token': 'test_oauth_token',
            'refresh_token': 'test_refresh_token',
            'timezone': 'America/Los_Angeles'
        }
        
        user_id = self.db_manager.create_user(**user_data)
        assert user_id is not None
        assert isinstance(user_id, int)
        
        # Verify user was created
        user = self.db_manager.get_user_by_name('phil')
        assert user is not None
        assert user['name'] == 'phil'
        assert user['phone_number'] == '+1234567890'
        assert user['calendar_id'] == 'phil@gmail.com'
    
    def test_user_retrieval(self):
        """Test retrieving users by various criteria"""
        # Create test users
        phil_id = self.db_manager.create_user(
            name='phil2',
            phone_number='+1234567891',
            email='phil2@example.com',
            calendar_id='phil2@gmail.com'
        )
        
        chris_id = self.db_manager.create_user(
            name='chris2',
            phone_number='+0987654322',
            email='chris2@example.com',
            calendar_id='chris2@gmail.com'
        )
        
        # Test retrieval by name
        phil = self.db_manager.get_user_by_name('phil2')
        assert phil is not None
        assert phil['id'] == phil_id
        
        # Test retrieval by phone
        chris = self.db_manager.get_user_by_phone('+0987654322')
        assert chris is not None
        assert chris['id'] == chris_id
        
        # Test retrieval by ID
        user = self.db_manager.get_user_by_id(phil_id)
        assert user is not None
        assert user['name'] == 'phil2'
    
    def test_user_update(self):
        """Test updating user information"""
        # Create user
        user_id = self.db_manager.create_user(
            name='phil5',
            phone_number='+1234567895',
            email='phil5@example.com',
            calendar_id='phil5@gmail.com'
        )
        
        # Update user
        update_data = {
            'phone_number': '+1111111111',
            'email': 'phil.new@example.com',
            'oauth_token': 'new_oauth_token'
        }
        
        success = self.db_manager.update_user(user_id, **update_data)
        assert success is True
        
        # Verify update
        user = self.db_manager.get_user_by_id(user_id)
        assert user['phone_number'] == '+1111111111'
        assert user['email'] == 'phil.new@example.com'
        assert user['oauth_token'] == 'new_oauth_token'
    
    def test_user_deletion(self):
        """Test deleting a user"""
        # Create user
        user_id = self.db_manager.create_user(
            name='phil6',
            phone_number='+1234567896',
            email='phil6@example.com',
            calendar_id='phil6@gmail.com'
        )
        
        # Verify user exists
        user = self.db_manager.get_user_by_id(user_id)
        assert user is not None
        
        # Delete user
        success = self.db_manager.delete_user(user_id)
        assert success is True
        
        # Verify user is deleted
        user = self.db_manager.get_user_by_id(user_id)
        assert user is None
    
    def test_conversation_context_storage(self):
        """Test storing and retrieving conversation context"""
        # Create users
        phil_id = self.db_manager.create_user(
            name='phil3',
            calendar_id='phil3@gmail.com'
        )
        chris_id = self.db_manager.create_user(
            name='chris3',
            calendar_id='chris3@gmail.com'
        )
        
        # Store conversation context
        context_data = {
            'user1_id': phil_id,
            'user2_id': chris_id,
            'context_text': 'We discussed meeting for coffee last week',
            'context_type': 'meeting_discussion'
        }
        
        context_id = self.db_manager.store_conversation_context(**context_data)
        assert context_id is not None
        
        # Retrieve conversation context
        context = self.db_manager.get_conversation_context(phil_id, chris_id)
        assert context is not None
        assert context['context_text'] == 'We discussed meeting for coffee last week'
        assert context['context_type'] == 'meeting_discussion'
    
    def test_meeting_suggestion_storage(self):
        """Test storing and retrieving meeting suggestions"""
        # Create users and conversation
        phil_id = self.db_manager.create_user(
            name='phil4',
            calendar_id='phil4@gmail.com'
        )
        chris_id = self.db_manager.create_user(
            name='chris4',
            calendar_id='chris4@gmail.com'
        )
        
        conversation_id = self.db_manager.create_conversation(phil_id, chris_id)
        
        # Store meeting suggestion
        suggestion_data = {
            'conversation_id': conversation_id,
            'user1_id': phil_id,
            'user2_id': chris_id,
            'suggestion_data': {
                'suggestions': [
                    {
                        'date': '2025-01-20',
                        'time': '14:00',
                        'duration': '1.5 hours',
                        'reasoning': 'Both are free and have high energy',
                        'phil_energy': 'High',
                        'chris_energy': 'High',
                        'meeting_type': 'Coffee'
                    }
                ],
                'metadata': {
                    'generated_at': '2025-01-15T10:30:00Z',
                    'total_suggestions': 1
                }
            },
            'status': 'pending'
        }
        
        suggestion_id = self.db_manager.store_meeting_suggestion(**suggestion_data)
        assert suggestion_id is not None
        
        # Retrieve meeting suggestion
        suggestion = self.db_manager.get_meeting_suggestion(suggestion_id)
        assert suggestion is not None
        assert suggestion['status'] == 'pending'
        assert len(suggestion['suggestion_data']['suggestions']) == 1
    
    def test_database_connection_management(self):
        """Test database connection management"""
        # Test connection
        assert self.db_manager.is_connected() is True
        
        # Test closing connection
        self.db_manager.close()
        assert self.db_manager.is_connected() is False
        
        # Test reconnection
        self.db_manager.connect()
        assert self.db_manager.is_connected() is True
    
    def test_database_error_handling(self):
        """Test database error handling"""
        # Test invalid user ID
        user = self.db_manager.get_user_by_id(99999)
        assert user is None
        
        # Test duplicate user creation
        self.db_manager.create_user(
            name='phil7',
            calendar_id='phil7@gmail.com'
        )
        
        # Should raise exception for duplicate name
        with pytest.raises(Exception):
            self.db_manager.create_user(
                name='phil7',
                calendar_id='phil7_duplicate@gmail.com'
            )
    
    def test_database_transactions(self):
        """Test database transaction handling"""
        # Test rollback on error
        try:
            with self.db_manager.transaction():
                self.db_manager.create_user(
                    name='phil8',
                    calendar_id='phil8@gmail.com'
                )
                # Force an error
                raise Exception("Test error")
        except Exception:
            pass
        
        # User should not exist due to rollback
        user = self.db_manager.get_user_by_name('phil8')
        assert user is None


def test_run_database_integration_test_suite():
    """Run the complete database integration test suite"""
    print("\n" + "="*80)
    print("🚀 RUNNING DATABASE INTEGRATION TEST SUITE")
    print("="*80)
    
    # Create test instance and run tests
    test_instance = TestDatabaseIntegration()
    
    try:
        test_instance.setup_method()
        
        test_instance.test_database_initialization()
        print("✅ Database initialization test passed")
        
        test_instance.test_user_creation()
        print("✅ User creation test passed")
        
        test_instance.test_user_retrieval()
        print("✅ User retrieval test passed")
        
        test_instance.test_user_update()
        print("✅ User update test passed")
        
        test_instance.test_user_deletion()
        print("✅ User deletion test passed")
        
        test_instance.test_conversation_context_storage()
        print("✅ Conversation context storage test passed")
        
        test_instance.test_meeting_suggestion_storage()
        print("✅ Meeting suggestion storage test passed")
        
        test_instance.test_database_connection_management()
        print("✅ Database connection management test passed")
        
        test_instance.test_database_error_handling()
        print("✅ Database error handling test passed")
        
        test_instance.test_database_transactions()
        print("✅ Database transactions test passed")
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        raise
    finally:
        test_instance.teardown_method()
    
    print("\n" + "="*80)
    print("🎯 DATABASE INTEGRATION TEST SUITE COMPLETE")
    print("="*80)


if __name__ == "__main__":
    test_run_database_integration_test_suite()
