#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for database integration with user management
"""
import pytest
import tempfile
import os
import json
import sys
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from infrastructure.database import DatabaseManager
from api.user_management import UserManager
from core.meeting_scheduler import create_ai_prompt, format_events_for_ai


class TestDatabaseIntegrationUpdate:
    """Test database integration with user management"""
    
    def setup_method(self):
        """Set up test database and user manager"""
        self.db_path = ":memory:"
        self.db_manager = DatabaseManager(self.db_path)
        self.db_manager.initialize_database()
        self.user_manager = UserManager(self.db_manager)
        
        # Create test users
        with self.db_manager.transaction():
            self.user1_id = self.db_manager.create_user(
                name="alice",
                calendar_id="alice@gmail.com",
                phone_number="+1234567890",
                email="alice@example.com"
            )
            self.user2_id = self.db_manager.create_user(
                name="bob", 
                calendar_id="bob@gmail.com",
                phone_number="+1987654321",
                email="bob@example.com"
            )
    
    def teardown_method(self):
        """Clean up test database"""
        if hasattr(self, 'db_manager'):
            self.db_manager.close()
    
    def test_user_lookup_by_name(self):
        """Test looking up users by name"""
        alice = self.db_manager.get_user_by_name("alice")
        bob = self.db_manager.get_user_by_name("bob")
        
        assert alice is not None
        assert alice['name'] == "alice"
        assert alice['calendar_id'] == "alice@gmail.com"
        
        assert bob is not None
        assert bob['name'] == "bob"
        assert bob['calendar_id'] == "bob@gmail.com"
    
    def test_create_ai_prompt_with_user_names(self):
        """Test create_ai_prompt with dynamic user names"""
        # Sample events
        alice_events = [
            {
                "summary": "Morning Meeting",
                "start": {"dateTime": "2025-01-16T09:00:00Z"},
                "location": "Office"
            }
        ]
        bob_events = [
            {
                "summary": "Lunch Break",
                "start": {"dateTime": "2025-01-16T12:00:00Z"},
                "location": "Cafeteria"
            }
        ]
        
        # Test with custom user names
        prompt = create_ai_prompt(alice_events, bob_events, "alice", "bob")
        
        # Should contain user names in prompt
        assert "ALICE'S CALENDAR EVENTS:" in prompt
        assert "BOB'S CALENDAR EVENTS:" in prompt
        assert "alice" in prompt.lower()
        assert "bob" in prompt.lower()
        
        # Should contain the events
        assert "Morning Meeting" in prompt
        assert "Lunch Break" in prompt
    
    def test_format_events_with_dynamic_names(self):
        """Test format_events_for_ai with different user names"""
        events = [
            {
                "summary": "Test Event",
                "start": {"dateTime": "2025-01-16T10:00:00Z"},
                "location": "Test Location"
            }
        ]
        
        # Test with different names
        result1 = format_events_for_ai(events, "alice")
        result2 = format_events_for_ai(events, "bob")
        
        # Both should work and contain the event data
        assert "Test Event" in result1
        assert "Test Event" in result2
        # Names should be different in output (function includes user name)
        assert "alice" in result1.lower()
        assert "bob" in result2.lower()
        # But the event content should be the same
        assert "2025-01-16 (Thursday) 10:00 - Test Event @ Test Location" in result1
        assert "2025-01-16 (Thursday) 10:00 - Test Event @ Test Location" in result2
    
    def test_database_user_management(self):
        """Test complete user management workflow"""
        # Create a new user
        with self.db_manager.transaction():
            user_id = self.db_manager.create_user(
                name="charlie",
                calendar_id="charlie@gmail.com",
                phone_number="+1555123456"
            )
        
        # Verify user was created
        charlie = self.db_manager.get_user_by_name("charlie")
        assert charlie is not None
        assert charlie['name'] == "charlie"
        
        # Update user
        self.db_manager.update_user(user_id, email="charlie@newdomain.com")
        updated_charlie = self.db_manager.get_user_by_id(user_id)
        assert updated_charlie['email'] == "charlie@newdomain.com"
        
        # List all users
        users = self.db_manager.list_users()
        assert len(users) >= 3  # alice, bob, charlie
        
        # Delete user
        deleted = self.db_manager.delete_user(user_id)
        assert deleted is True
        
        # Verify deletion
        deleted_charlie = self.db_manager.get_user_by_name("charlie")
        assert deleted_charlie is None
    
    def test_conversation_context_storage(self):
        """Test conversation context storage and retrieval"""
        context_text = "We discussed meeting for coffee last week"
        
        # Store context
        context_id = self.db_manager.store_conversation_context(
            self.user1_id, self.user2_id, context_text, "meeting_discussion"
        )
        assert context_id is not None
        
        # Retrieve context
        context = self.db_manager.get_conversation_context(self.user1_id, self.user2_id)
        assert context is not None
        assert context['context_text'] == context_text
        assert context['context_type'] == "meeting_discussion"
    
    def test_meeting_suggestions_storage(self):
        """Test meeting suggestions storage"""
        # Create conversation first
        conv_id = self.db_manager.create_conversation(self.user1_id, self.user2_id)
        
        # Store meeting suggestion
        suggestion_data = {
            "suggestions": [
                {
                    "date": "2025-01-20",
                    "time": "14:00",
                    "duration": "1 hour",
                    "reasoning": "Both free at this time"
                }
            ]
        }
        
        suggestion_id = self.db_manager.store_meeting_suggestion(
            conv_id, self.user1_id, self.user2_id, suggestion_data
        )
        assert suggestion_id is not None
        
        # Retrieve suggestion
        suggestion = self.db_manager.get_meeting_suggestion(suggestion_id)
        assert suggestion is not None
        assert suggestion['suggestion_data']['suggestions'][0]['date'] == "2025-01-20"


def test_run_database_integration_update_tests():
    """Run all database integration update tests"""
    print("🧪 Testing database integration updates...")
    
    test_instance = TestDatabaseIntegrationUpdate()
    test_instance.setup_method()
    
    # Run all test methods
    test_instance.test_user_lookup_by_name()
    print("✅ User lookup test passed")
    
    test_instance.test_create_ai_prompt_with_user_names()
    print("✅ AI prompt with user names test passed")
    
    test_instance.test_format_events_with_dynamic_names()
    print("✅ Format events with dynamic names test passed")
    
    test_instance.test_database_user_management()
    print("✅ Database user management test passed")
    
    test_instance.test_conversation_context_storage()
    print("✅ Conversation context storage test passed")
    
    test_instance.test_meeting_suggestions_storage()
    print("✅ Meeting suggestions storage test passed")
    
    test_instance.teardown_method()
    print("🎉 All database integration update tests passed!")


if __name__ == "__main__":
    test_run_database_integration_update_tests()
