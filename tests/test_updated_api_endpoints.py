#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for updated API endpoints with user management and flexible parameters
"""
import pytest
import json
import tempfile
import os
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from api.server import app
from api.models import MeetingSuggestionsResponse, MeetingSuggestion, UserCreate, UserUpdate
from infrastructure.database import DatabaseManager


class TestUpdatedAPIEndpoints:
    """Test updated API endpoints with user management"""
    
    def setup_method(self):
        """Set up test client and database"""
        # Create temporary database file
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name
        
        # Initialize database
        self.db_manager = DatabaseManager(self.db_path)
        self.db_manager.initialize_database()
        
        # Set up test client
        self.client = TestClient(app)
        
        # Create test users
        self.phil_id = self.db_manager.create_user(
            name='phil',
            phone_number='+1234567890',
            email='phil@example.com',
            calendar_id='phil@gmail.com',
            oauth_token='test_oauth_token'
        )
        
        self.chris_id = self.db_manager.create_user(
            name='chris',
            phone_number='+0987654321',
            email='chris@example.com',
            calendar_id='chris@gmail.com',
            oauth_token='test_oauth_token'
        )
    
    def teardown_method(self):
        """Clean up test database"""
        if hasattr(self, 'db_manager'):
            self.db_manager.close()
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
    
    def test_health_endpoint(self):
        """Test health check endpoint still works"""
        response = self.client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
    
    def test_get_users_endpoint(self):
        """Test GET /users endpoint"""
        response = self.client.get("/users")
        assert response.status_code == 200
        
        users = response.json()
        assert len(users) == 2
        
        user_names = [user['name'] for user in users]
        assert 'phil' in user_names
        assert 'chris' in user_names
    
    def test_get_user_by_name_endpoint(self):
        """Test GET /users/{name} endpoint"""
        response = self.client.get("/users/phil")
        assert response.status_code == 200
        
        user = response.json()
        assert user['name'] == 'phil'
        assert user['calendar_id'] == 'phil@gmail.com'
    
    def test_get_user_by_name_not_found(self):
        """Test GET /users/{name} with non-existent user"""
        response = self.client.get("/users/nonexistent")
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]
    
    def test_create_user_endpoint(self):
        """Test POST /users endpoint"""
        user_data = {
            "name": "alex",
            "phone_number": "+1111111111",
            "email": "alex@example.com",
            "calendar_id": "alex@gmail.com"
        }
        
        response = self.client.post("/users", json=user_data)
        assert response.status_code == 201
        
        created_user = response.json()
        assert created_user['name'] == 'alex'
        assert created_user['calendar_id'] == 'alex@gmail.com'
        assert 'id' in created_user
    
    def test_create_user_duplicate_name(self):
        """Test POST /users with duplicate name"""
        user_data = {
            "name": "phil",  # Already exists
            "calendar_id": "phil2@gmail.com"
        }
        
        response = self.client.post("/users", json=user_data)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]
    
    def test_update_user_endpoint(self):
        """Test PUT /users/{user_id} endpoint"""
        update_data = {
            "phone_number": "+9999999999",
            "email": "phil.updated@example.com"
        }
        
        response = self.client.put(f"/users/{self.phil_id}", json=update_data)
        assert response.status_code == 200
        
        updated_user = response.json()
        assert updated_user['phone_number'] == '+9999999999'
        assert updated_user['email'] == 'phil.updated@example.com'
    
    def test_update_user_not_found(self):
        """Test PUT /users/{user_id} with non-existent user"""
        update_data = {"phone_number": "+9999999999"}
        
        response = self.client.put("/users/99999", json=update_data)
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]
    
    def test_delete_user_endpoint(self):
        """Test DELETE /users/{user_id} endpoint"""
        response = self.client.delete(f"/users/{self.chris_id}")
        assert response.status_code == 200
        assert response.json() == {"message": "User deleted successfully"}
        
        # Verify user is deleted
        response = self.client.get(f"/users/{self.chris_id}")
        assert response.status_code == 404
    
    def test_delete_user_not_found(self):
        """Test DELETE /users/{user_id} with non-existent user"""
        response = self.client.delete("/users/99999")
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]
    
    @patch('api.server.get_meeting_suggestions_from_core')
    def test_meeting_suggestions_with_user_names(self, mock_get_suggestions):
        """Test POST /meeting-suggestions with user names"""
        mock_suggestions = {
            "suggestions": [
                {
                    "date": "2025-01-20",
                    "time": "14:00",
                    "duration": "1.5 hours",
                    "reasoning": "Both are free and have high energy",
                    "phil_energy": "High",
                    "chris_energy": "High",
                    "meeting_type": "Coffee"
                }
            ],
            "metadata": {
                "generated_at": "2025-01-15T10:30:00Z",
                "total_suggestions": 1,
                "user1": "phil",
                "user2": "chris"
            }
        }
        mock_get_suggestions.return_value = mock_suggestions
        
        request_data = {
            "user1_name": "phil",
            "user2_name": "chris"
        }
        
        response = self.client.post("/meeting-suggestions", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "suggestions" in data
        assert "metadata" in data
        assert data["metadata"]["user1"] == "phil"
        assert data["metadata"]["user2"] == "chris"
    
    @patch('api.server.get_meeting_suggestions_from_core')
    def test_meeting_suggestions_with_time_range(self, mock_get_suggestions):
        """Test POST /meeting-suggestions with custom time range"""
        mock_suggestions = {
            "suggestions": [],
            "metadata": {
                "generated_at": "2025-01-15T10:30:00Z",
                "time_range_analyzed": "2025-01-20 to 2025-02-10"
            }
        }
        mock_get_suggestions.return_value = mock_suggestions
        
        request_data = {
            "user1_name": "phil",
            "user2_name": "chris",
            "time_range_days": 21,
            "start_date": "2025-01-20",
            "end_date": "2025-02-10"
        }
        
        response = self.client.post("/meeting-suggestions", json=request_data)
        assert response.status_code == 200
        
        # Verify the core function was called with correct parameters
        mock_get_suggestions.assert_called_once()
        call_args = mock_get_suggestions.call_args
        assert call_args[1]['user1_name'] == 'phil'
        assert call_args[1]['user2_name'] == 'chris'
        assert call_args[1]['time_range_days'] == 21
        assert call_args[1]['start_date'] == '2025-01-20'
        assert call_args[1]['end_date'] == '2025-02-10'
    
    @patch('api.server.get_meeting_suggestions_from_core')
    def test_meeting_suggestions_with_conversation_context(self, mock_get_suggestions):
        """Test POST /meeting-suggestions with conversation context"""
        mock_suggestions = {
            "suggestions": [],
            "metadata": {
                "generated_at": "2025-01-15T10:30:00Z",
                "conversation_context_used": True
            }
        }
        mock_get_suggestions.return_value = mock_suggestions
        
        request_data = {
            "user1_name": "phil",
            "user2_name": "chris",
            "conversation_context": "We discussed meeting for coffee last week"
        }
        
        response = self.client.post("/meeting-suggestions", json=request_data)
        assert response.status_code == 200
        
        # Verify conversation context was passed
        call_args = mock_get_suggestions.call_args
        assert call_args[1]['conversation_context'] == "We discussed meeting for coffee last week"
    
    def test_meeting_suggestions_user_not_found(self):
        """Test POST /meeting-suggestions with non-existent user"""
        request_data = {
            "user1_name": "nonexistent",
            "user2_name": "chris"
        }
        
        response = self.client.post("/meeting-suggestions", json=request_data)
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]
    
    def test_meeting_suggestions_validation_error(self):
        """Test POST /meeting-suggestions with invalid data"""
        request_data = {
            "user1_name": "phil"
            # Missing user2_name
        }
        
        response = self.client.post("/meeting-suggestions", json=request_data)
        assert response.status_code == 422  # Validation error
    
    @patch('api.server.handle_text_chat_from_core')
    def test_text_chat_endpoint(self, mock_text_chat):
        """Test POST /text-chat endpoint"""
        mock_response = {
            "response": "Great! I found some good times for coffee. Let me check your calendars...",
            "suggestions_generated": True
        }
        mock_text_chat.return_value = mock_response
        
        request_data = {
            "user1_name": "phil",
            "user2_name": "chris",
            "message": "Hey, want to grab coffee sometime this week?",
            "script_context": "casual_coffee_invitation"
        }
        
        response = self.client.post("/text-chat", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "response" in data
        assert "suggestions_generated" in data
    
    def test_text_chat_user_not_found(self):
        """Test POST /text-chat with non-existent user"""
        request_data = {
            "user1_name": "nonexistent",
            "user2_name": "chris",
            "message": "Hello"
        }
        
        response = self.client.post("/text-chat", json=request_data)
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]
    
    def test_conversation_context_endpoint(self):
        """Test GET /conversation-context/{user1}/{user2} endpoint"""
        # Store some conversation context
        self.db_manager.store_conversation_context(
            user1_id=self.phil_id,
            user2_id=self.chris_id,
            context_text="We discussed meeting for coffee",
            context_type="meeting_discussion"
        )
        
        response = self.client.get("/conversation-context/phil/chris")
        assert response.status_code == 200
        
        context = response.json()
        assert context['context_text'] == "We discussed meeting for coffee"
        assert context['context_type'] == "meeting_discussion"
    
    def test_conversation_context_not_found(self):
        """Test GET /conversation-context/{user1}/{user2} with no context"""
        response = self.client.get("/conversation-context/phil/chris")
        assert response.status_code == 404
        assert "No conversation context found" in response.json()["detail"]


def test_run_updated_api_endpoints_test_suite():
    """Run the complete updated API endpoints test suite"""
    print("\n" + "="*80)
    print("🚀 RUNNING UPDATED API ENDPOINTS TEST SUITE")
    print("="*80)
    
    # Create test instance and run tests
    test_instance = TestUpdatedAPIEndpoints()
    
    try:
        test_instance.setup_method()
        
        test_instance.test_health_endpoint()
        print("✅ Health endpoint test passed")
        
        test_instance.test_get_users_endpoint()
        print("✅ Get users endpoint test passed")
        
        test_instance.test_get_user_by_name_endpoint()
        print("✅ Get user by name endpoint test passed")
        
        test_instance.test_get_user_by_name_not_found()
        print("✅ Get user by name not found test passed")
        
        test_instance.test_create_user_endpoint()
        print("✅ Create user endpoint test passed")
        
        test_instance.test_create_user_duplicate_name()
        print("✅ Create user duplicate name test passed")
        
        test_instance.test_update_user_endpoint()
        print("✅ Update user endpoint test passed")
        
        test_instance.test_update_user_not_found()
        print("✅ Update user not found test passed")
        
        test_instance.test_delete_user_endpoint()
        print("✅ Delete user endpoint test passed")
        
        test_instance.test_delete_user_not_found()
        print("✅ Delete user not found test passed")
        
        test_instance.test_meeting_suggestions_with_user_names()
        print("✅ Meeting suggestions with user names test passed")
        
        test_instance.test_meeting_suggestions_with_time_range()
        print("✅ Meeting suggestions with time range test passed")
        
        test_instance.test_meeting_suggestions_with_conversation_context()
        print("✅ Meeting suggestions with conversation context test passed")
        
        test_instance.test_meeting_suggestions_user_not_found()
        print("✅ Meeting suggestions user not found test passed")
        
        test_instance.test_meeting_suggestions_validation_error()
        print("✅ Meeting suggestions validation error test passed")
        
        test_instance.test_text_chat_endpoint()
        print("✅ Text chat endpoint test passed")
        
        test_instance.test_text_chat_user_not_found()
        print("✅ Text chat user not found test passed")
        
        test_instance.test_conversation_context_endpoint()
        print("✅ Conversation context endpoint test passed")
        
        test_instance.test_conversation_context_not_found()
        print("✅ Conversation context not found test passed")
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        raise
    finally:
        test_instance.teardown_method()
    
    print("\n" + "="*80)
    print("🎯 UPDATED API ENDPOINTS TEST SUITE COMPLETE")
    print("="*80)


if __name__ == "__main__":
    test_run_updated_api_endpoints_test_suite()
