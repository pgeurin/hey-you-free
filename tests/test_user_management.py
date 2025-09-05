#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for user management functionality
"""
import pytest
import tempfile
import os
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from infrastructure.database import DatabaseManager
from api.user_management import UserManager, UserValidationError


class TestUserManagement:
    """Test user management functionality"""
    
    def setup_method(self):
        """Set up test database and user manager"""
        # Create temporary database file
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = ":memory:"
        
        # Initialize database and user manager
        self.db_manager = DatabaseManager(self.db_path)
        self.db_manager.initialize_database()
        self.user_manager = UserManager(self.db_manager)
    
    def teardown_method(self):
        """Clean up test database"""
        if hasattr(self, 'db_manager'):
            self.db_manager.close()
    
    def test_user_validation(self):
        """Test user data validation"""
        # Valid user data
        valid_user = {
            'name': 'phil',
            'phone_number': '+1234567890',
            'email': 'phil@example.com',
            'calendar_id': 'phil@gmail.com'
        }
        
        # Should not raise exception
        self.user_manager.validate_user_data(valid_user)
        
        # Invalid user data - missing required fields
        invalid_user = {
            'name': 'phil'
            # Missing calendar_id
        }
        
        with pytest.raises(UserValidationError):
            self.user_manager.validate_user_data(invalid_user)
    
    def test_phone_number_validation(self):
        """Test phone number validation"""
        # Valid phone numbers
        valid_phones = [
            '+1234567890',
            '+1-234-567-8900',
            '(123) 456-7890',
            '123-456-7890'
        ]
        
        for phone in valid_phones:
            assert self.user_manager.validate_phone_number(phone) is True
        
        # Invalid phone numbers
        invalid_phones = [
            '123',  # Too short
            'abc-def-ghij',  # Non-numeric
            '',  # Empty
            None  # None
        ]
        
        for phone in invalid_phones:
            assert self.user_manager.validate_phone_number(phone) is False
    
    def test_email_validation(self):
        """Test email validation"""
        # Valid emails
        valid_emails = [
            'phil@example.com',
            'phil.test@example.co.uk',
            'phil+test@example.com'
        ]
        
        for email in valid_emails:
            assert self.user_manager.validate_email(email) is True
        
        # Invalid emails
        invalid_emails = [
            'phil@',  # Missing domain
            '@example.com',  # Missing local part
            'phil.example.com',  # Missing @
            '',  # Empty
            None  # None
        ]
        
        for email in invalid_emails:
            assert self.user_manager.validate_email(email) is False
    
    def test_create_user_with_validation(self):
        """Test creating user with validation"""
        user_data = {
            'name': 'phil_user_mgmt',
            'phone_number': '+1234567890',
            'email': 'phil_user_mgmt@example.com',
            'calendar_id': 'phil_user_mgmt@gmail.com'
        }
        
        user_id = self.user_manager.create_user(user_data)
        assert user_id is not None
        
        # Verify user was created
        user = self.user_manager.get_user_by_name('phil_user_mgmt')
        assert user is not None
        assert user['name'] == 'phil_user_mgmt'
    
    def test_create_user_duplicate_name(self):
        """Test creating user with duplicate name"""
        user_data = {
            'name': 'phil_duplicate',
            'calendar_id': 'phil_duplicate@gmail.com'
        }
        
        # Create first user
        self.user_manager.create_user(user_data)
        
        # Try to create second user with same name
        with pytest.raises(UserValidationError):
            self.user_manager.create_user(user_data)
    
    def test_update_user_oauth_tokens(self):
        """Test updating user OAuth tokens"""
        # Create user
        user_data = {
            'name': 'phil_oauth',
            'calendar_id': 'phil_oauth@gmail.com'
        }
        user_id = self.user_manager.create_user(user_data)
        
        # Update OAuth tokens
        oauth_data = {
            'oauth_token': 'new_oauth_token',
            'refresh_token': 'new_refresh_token'
        }
        
        success = self.user_manager.update_user_oauth_tokens(user_id, oauth_data)
        assert success is True
        
        # Verify tokens were updated
        user = self.user_manager.get_user_by_id(user_id)
        assert user['oauth_token'] == 'new_oauth_token'
        assert user['refresh_token'] == 'new_refresh_token'
    
    def test_get_user_calendar_info(self):
        """Test getting user calendar information"""
        # Create user with calendar info
        user_data = {
            'name': 'phil_calendar',
            'calendar_id': 'phil_calendar@gmail.com',
            'oauth_token': 'test_token',
            'timezone': 'America/Los_Angeles'
        }
        user_id = self.user_manager.create_user(user_data)
        
        # Get calendar info
        calendar_info = self.user_manager.get_user_calendar_info('phil_calendar')
        assert calendar_info is not None
        assert calendar_info['calendar_id'] == 'phil_calendar@gmail.com'
        assert calendar_info['oauth_token'] == 'test_token'
        assert calendar_info['timezone'] == 'America/Los_Angeles'
    
    def test_list_all_users(self):
        """Test listing all users"""
        # Create multiple users
        users_data = [
            {'name': 'phil_list', 'calendar_id': 'phil_list@gmail.com'},
            {'name': 'chris_list', 'calendar_id': 'chris_list@gmail.com'},
            {'name': 'alex_list', 'calendar_id': 'alex_list@gmail.com'}
        ]
        
        for user_data in users_data:
            self.user_manager.create_user(user_data)
        
        # List all users
        users = self.user_manager.list_all_users()
        # Should have at least 3 users (may have more from previous tests)
        assert len(users) >= 3
        
        user_names = [user['name'] for user in users]
        assert 'phil_list' in user_names
        assert 'chris_list' in user_names
        assert 'alex_list' in user_names
    
    def test_user_search(self):
        """Test searching for users"""
        # Create users
        users_data = [
            {'name': 'phil_search', 'email': 'phil_search@example.com', 'calendar_id': 'phil_search@gmail.com'},
            {'name': 'chris_search', 'email': 'chris_search@example.com', 'calendar_id': 'chris_search@gmail.com'},
            {'name': 'alex_search', 'email': 'alex_search@example.com', 'calendar_id': 'alex_search@gmail.com'}
        ]
        
        for user_data in users_data:
            self.user_manager.create_user(user_data)
        
        # Search by name
        results = self.user_manager.search_users('phil_search')
        assert len(results) == 1
        assert results[0]['name'] == 'phil_search'
        
        # Search by email
        results = self.user_manager.search_users('chris_search@example.com')
        assert len(results) == 1
        assert results[0]['name'] == 'chris_search'
        
        # Search with no results
        results = self.user_manager.search_users('nonexistent')
        assert len(results) == 0
    
    def test_user_deactivation(self):
        """Test deactivating a user"""
        # Create user
        user_data = {
            'name': 'phil_deactivate',
            'calendar_id': 'phil_deactivate@gmail.com'
        }
        user_id = self.user_manager.create_user(user_data)
        
        # Deactivate user
        success = self.user_manager.deactivate_user(user_id)
        assert success is True
        
        # Verify user is deactivated
        user = self.user_manager.get_user_by_id(user_id)
        assert user["is_active"] == 0
    
    def test_user_reactivation(self):
        """Test reactivating a user"""
        # Create and deactivate user
        user_data = {
            'name': 'phil_reactivate',
            'calendar_id': 'phil_reactivate@gmail.com'
        }
        user_id = self.user_manager.create_user(user_data)
        self.user_manager.deactivate_user(user_id)
        
        # Reactivate user
        success = self.user_manager.activate_user(user_id)
        assert success is True
        
        # Verify user is active
        user = self.user_manager.get_user_by_id(user_id)
        assert user["is_active"] == 1
    
    def test_user_statistics(self):
        """Test getting user statistics"""
        # Create users
        users_data = [
            {'name': 'phil_stats', 'calendar_id': 'phil_stats@gmail.com'},
            {'name': 'chris_stats', 'calendar_id': 'chris_stats@gmail.com'},
            {'name': 'alex_stats', 'calendar_id': 'alex_stats@gmail.com'}
        ]
        
        for user_data in users_data:
            self.user_manager.create_user(user_data)
        
        # Deactivate one user
        alex = self.user_manager.get_user_by_name('alex_stats')
        self.user_manager.deactivate_user(alex['id'])
        
        # Get statistics
        stats = self.user_manager.get_user_statistics()
        assert stats["total_users"] >= 3
        assert stats["active_users"] >= 2
        assert stats["inactive_users"] >= 1


def test_run_user_management_test_suite():
    """Run the complete user management test suite"""
    print("\n" + "="*80)
    print("🚀 RUNNING USER MANAGEMENT TEST SUITE")
    print("="*80)
    
    # Create test instance and run tests
    test_instance = TestUserManagement()
    
    try:
        test_instance.setup_method()
        
        test_instance.test_user_validation()
        print("✅ User validation test passed")
        
        test_instance.test_phone_number_validation()
        print("✅ Phone number validation test passed")
        
        test_instance.test_email_validation()
        print("✅ Email validation test passed")
        
        test_instance.test_create_user_with_validation()
        print("✅ Create user with validation test passed")
        
        test_instance.test_create_user_duplicate_name()
        print("✅ Create user duplicate name test passed")
        
        test_instance.test_update_user_oauth_tokens()
        print("✅ Update user OAuth tokens test passed")
        
        test_instance.test_get_user_calendar_info()
        print("✅ Get user calendar info test passed")
        
        test_instance.test_list_all_users()
        print("✅ List all users test passed")
        
        test_instance.test_user_search()
        print("✅ User search test passed")
        
        test_instance.test_user_deactivation()
        print("✅ User deactivation test passed")
        
        test_instance.test_user_reactivation()
        print("✅ User reactivation test passed")
        
        test_instance.test_user_statistics()
        print("✅ User statistics test passed")
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        raise
    finally:
        test_instance.teardown_method()
    
    print("\n" + "="*80)
    print("🎯 USER MANAGEMENT TEST SUITE COMPLETE")
    print("="*80)


if __name__ == "__main__":
    test_run_user_management_test_suite()
