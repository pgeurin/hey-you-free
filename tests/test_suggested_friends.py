"""
Test suggested friends functionality for users
"""
import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from infrastructure.database import DatabaseManager
from api.user_management import UserManager


class TestSuggestedFriends:
    """Test suggested friends functionality"""
    
    def setup_method(self):
        """Set up test database"""
        self.db_manager = DatabaseManager(":memory:")
        self.db_manager.connect()
        self.db_manager.initialize_database()
        self.user_manager = UserManager(self.db_manager)
        
        # Create test users
        self.user_manager.create_user({
            "name": "Phil", 
            "email": "phil@example.com", 
            "calendar_id": "primary", 
            "phone_number": "+1234567890"
        })
        self.user_manager.create_user({
            "name": "Chris", 
            "email": "chris@example.com", 
            "calendar_id": "primary", 
            "phone_number": "+1234567891"
        })
        self.user_manager.create_user({
            "name": "Alex", 
            "email": "alex@example.com", 
            "calendar_id": "primary", 
            "phone_number": "+1234567892"
        })
        self.user_manager.create_user({
            "name": "Sam", 
            "email": "sam@example.com", 
            "calendar_id": "primary", 
            "phone_number": "+1234567893"
        })
    
    def teardown_method(self):
        """Clean up test database"""
        self.db_manager.close()
    
    def test_add_suggested_friend(self):
        """Test adding a suggested friend for a user"""
        # Add Chris as a suggested friend for Phil
        result = self.user_manager.add_suggested_friend("Phil", "Chris")
        assert result["success"] is True
        assert "Chris" in result["message"]
        
        # Verify the suggestion was added
        suggestions = self.user_manager.get_suggested_friends("Phil")
        assert len(suggestions) == 1
        assert suggestions[0]["name"] == "Chris"
        assert suggestions[0]["status"] == "suggested"
    
    def test_get_suggested_friends(self):
        """Test retrieving suggested friends for a user"""
        # Add multiple suggested friends
        self.user_manager.add_suggested_friend("Phil", "Chris")
        self.user_manager.add_suggested_friend("Phil", "Alex")
        
        suggestions = self.user_manager.get_suggested_friends("Phil")
        assert len(suggestions) == 2
        
        # Check that both friends are in the suggestions
        friend_names = [s["name"] for s in suggestions]
        assert "Chris" in friend_names
        assert "Alex" in friend_names
    
    def test_accept_suggested_friend(self):
        """Test accepting a suggested friend"""
        # Clear any existing suggestions first
        existing_suggestions = self.user_manager.get_suggested_friends("Phil")
        for suggestion in existing_suggestions:
            self.user_manager.remove_suggested_friend("Phil", suggestion["name"])
        
        # Add Chris as suggested friend
        self.user_manager.add_suggested_friend("Phil", "Chris")
        
        # Accept the suggestion
        result = self.user_manager.accept_suggested_friend("Phil", "Chris")
        assert result["success"] is True
        
        # Verify the suggestion is no longer in suggested list (moved to accepted)
        suggestions = self.user_manager.get_suggested_friends("Phil")
        assert len(suggestions) == 0
        
        # Verify Chris is now in the friends list
        friends = self.user_manager.get_friends("Phil")
        assert len(friends) == 1
        assert friends[0]["name"] == "Chris"
        assert friends[0]["status"] == "accepted"
    
    def test_remove_suggested_friend(self):
        """Test removing a suggested friend"""
        # Clear any existing suggestions first
        existing_suggestions = self.user_manager.get_suggested_friends("Phil")
        for suggestion in existing_suggestions:
            self.user_manager.remove_suggested_friend("Phil", suggestion["name"])
        
        # Add Chris as suggested friend
        self.user_manager.add_suggested_friend("Phil", "Chris")
        
        # Remove the suggestion
        result = self.user_manager.remove_suggested_friend("Phil", "Chris")
        assert result["success"] is True
        
        # Verify the suggestion is removed
        suggestions = self.user_manager.get_suggested_friends("Phil")
        assert len(suggestions) == 0
    
    def test_suggested_friend_does_not_exist(self):
        """Test handling when suggested friend doesn't exist"""
        result = self.user_manager.add_suggested_friend("Phil", "NonExistent")
        assert result["success"] is False
        assert "not found" in result["message"].lower()
    
    def test_duplicate_suggested_friend(self):
        """Test handling duplicate suggested friends"""
        # Add Chris as suggested friend
        self.user_manager.add_suggested_friend("Phil", "Chris")
        
        # Try to add Chris again
        result = self.user_manager.add_suggested_friend("Phil", "Chris")
        assert result["success"] is False
        assert "already" in result["message"].lower()
    
    def test_suggested_friends_bidirectional(self):
        """Test that suggested friends work bidirectionally"""
        # Clear any existing suggestions first
        for user_name in ["Phil", "Chris"]:
            existing_suggestions = self.user_manager.get_suggested_friends(user_name)
            for suggestion in existing_suggestions:
                self.user_manager.remove_suggested_friend(user_name, suggestion["name"])
        
        # Add Chris as suggested friend for Phil
        self.user_manager.add_suggested_friend("Phil", "Chris")
        
        # Phil should see Chris as suggested
        phil_suggestions = self.user_manager.get_suggested_friends("Phil")
        assert len(phil_suggestions) == 1
        assert phil_suggestions[0]["name"] == "Chris"
        
        # Chris should also see Phil as suggested (bidirectional)
        chris_suggestions = self.user_manager.get_suggested_friends("Chris")
        assert len(chris_suggestions) == 1
        assert chris_suggestions[0]["name"] == "Phil"
    
    def test_get_friends_list(self):
        """Test getting accepted friends list"""
        # Clear any existing suggestions and friends first
        existing_suggestions = self.user_manager.get_suggested_friends("Phil")
        for suggestion in existing_suggestions:
            self.user_manager.remove_suggested_friend("Phil", suggestion["name"])
        
        # Add and accept Chris as friend
        self.user_manager.add_suggested_friend("Phil", "Chris")
        self.user_manager.accept_suggested_friend("Phil", "Chris")
        
        # Get friends list
        friends = self.user_manager.get_friends("Phil")
        assert len(friends) == 1
        assert friends[0]["name"] == "Chris"
        assert friends[0]["status"] == "accepted"


def test_run_suggested_friends_tests():
    """Run all suggested friends tests"""
    test_instance = TestSuggestedFriends()
    test_instance.setup_method()
    
    try:
        test_instance.test_add_suggested_friend()
        test_instance.test_get_suggested_friends()
        test_instance.test_accept_suggested_friend()
        test_instance.test_remove_suggested_friend()
        test_instance.test_suggested_friend_does_not_exist()
        test_instance.test_duplicate_suggested_friend()
        test_instance.test_suggested_friends_bidirectional()
        test_instance.test_get_friends_list()
    finally:
        test_instance.teardown_method()
    
    return True
