#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
User management functionality for the Meeting Scheduler application
"""
import re
from typing import Dict, List, Optional, Any
from infrastructure.database import DatabaseManager


class UserValidationError(Exception):
    """Exception raised for user validation errors"""
    pass


class UserManager:
    """Manages user operations with validation"""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize user manager with database manager"""
        self.db_manager = db_manager
    
    def validate_user_data(self, user_data: Dict[str, Any]) -> None:
        """Validate user data before creation/update"""
        required_fields = ['name', 'calendar_id']
        
        for field in required_fields:
            if field not in user_data or not user_data[field]:
                raise UserValidationError(f"Field '{field}' is required")
        
        # Validate name
        if not isinstance(user_data['name'], str) or len(user_data['name'].strip()) == 0:
            raise UserValidationError("Name must be a non-empty string")
        
        # Validate calendar_id
        if not isinstance(user_data['calendar_id'], str) or len(user_data['calendar_id'].strip()) == 0:
            raise UserValidationError("Calendar ID must be a non-empty string")
        
        # Validate phone number if provided
        if 'phone_number' in user_data and user_data['phone_number']:
            if not self.validate_phone_number(user_data['phone_number']):
                raise UserValidationError("Invalid phone number format")
        
        # Validate email if provided
        if 'email' in user_data and user_data['email']:
            if not self.validate_email(user_data['email']):
                raise UserValidationError("Invalid email format")
    
    def validate_phone_number(self, phone: str) -> bool:
        """Validate phone number format"""
        if not phone or not isinstance(phone, str):
            return False
        
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone)
        
        # Check if it has 10 or 11 digits (US format)
        return len(digits_only) in [10, 11]
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        if not email or not isinstance(email, str):
            return False
        
        # Basic email regex pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def create_user(self, user_data: Dict[str, Any]) -> int:
        """Create a new user with validation"""
        self.validate_user_data(user_data)
        
        # Check if user already exists
        existing_user = self.db_manager.get_user_by_name(user_data['name'])
        if existing_user:
            raise UserValidationError(f"User with name '{user_data['name']}' already exists")
        
        # Check phone number uniqueness if provided
        if 'phone_number' in user_data and user_data['phone_number']:
            existing_phone = self.db_manager.get_user_by_phone(user_data['phone_number'])
            if existing_phone:
                raise UserValidationError(f"User with phone number '{user_data['phone_number']}' already exists")
        
        # Check email uniqueness if provided
        if 'email' in user_data and user_data['email']:
            # Note: We'd need to add get_user_by_email method to DatabaseManager
            pass
        
        return self.db_manager.create_user(**user_data)
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        return self.db_manager.get_user_by_id(user_id)
    
    def get_user_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get user by name"""
        return self.db_manager.get_user_by_name(name)
    
    def get_user_by_phone(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """Get user by phone number"""
        return self.db_manager.get_user_by_phone(phone_number)
    
    def update_user(self, user_id: int, update_data: Dict[str, Any]) -> bool:
        """Update user with validation"""
        # Validate update data
        if 'name' in update_data:
            if not isinstance(update_data['name'], str) or len(update_data['name'].strip()) == 0:
                raise UserValidationError("Name must be a non-empty string")
            
            # Check if name is already taken by another user
            existing_user = self.db_manager.get_user_by_name(update_data['name'])
            if existing_user and existing_user['id'] != user_id:
                raise UserValidationError(f"User with name '{update_data['name']}' already exists")
        
        if 'phone_number' in update_data and update_data['phone_number']:
            if not self.validate_phone_number(update_data['phone_number']):
                raise UserValidationError("Invalid phone number format")
            
            # Check if phone number is already taken by another user
            existing_phone = self.db_manager.get_user_by_phone(update_data['phone_number'])
            if existing_phone and existing_phone['id'] != user_id:
                raise UserValidationError(f"User with phone number '{update_data['phone_number']}' already exists")
        
        if 'email' in update_data and update_data['email']:
            if not self.validate_email(update_data['email']):
                raise UserValidationError("Invalid email format")
        
        return self.db_manager.update_user(user_id, **update_data)
    
    def delete_user(self, user_id: int) -> bool:
        """Delete a user"""
        return self.db_manager.delete_user(user_id)
    
    def list_all_users(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """List all users"""
        return self.db_manager.list_users(active_only=active_only)
    
    def search_users(self, query: str) -> List[Dict[str, Any]]:
        """Search users by name, email, or phone number"""
        if not query or not isinstance(query, str):
            return []
        
        query = query.strip().lower()
        all_users = self.db_manager.list_users(active_only=False)
        
        results = []
        for user in all_users:
            # Search in name
            if user['name'] and query in user['name'].lower():
                results.append(user)
                continue
            
            # Search in email
            if user['email'] and query in user['email'].lower():
                results.append(user)
                continue
            
            # Search in phone number
            if user['phone_number'] and query in user['phone_number']:
                results.append(user)
                continue
        
        return results
    
    def update_user_oauth_tokens(self, user_id: int, oauth_data: Dict[str, str]) -> bool:
        """Update user OAuth tokens"""
        valid_fields = ['oauth_token', 'refresh_token']
        update_data = {k: v for k, v in oauth_data.items() if k in valid_fields}
        
        if not update_data:
            return False
        
        return self.db_manager.update_user(user_id, **update_data)
    
    def get_user_calendar_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get user calendar information for meeting suggestions"""
        user = self.db_manager.get_user_by_name(name)
        if not user:
            return None
        
        return {
            'id': user['id'],
            'name': user['name'],
            'calendar_id': user['calendar_id'],
            'oauth_token': user['oauth_token'],
            'refresh_token': user['refresh_token'],
            'timezone': user['timezone']
        }
    
    def activate_user(self, user_id: int) -> bool:
        """Activate a user"""
        return self.db_manager.update_user(user_id, is_active=True)
    
    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate a user"""
        return self.db_manager.update_user(user_id, is_active=False)
    
    def get_user_statistics(self) -> Dict[str, int]:
        """Get user statistics"""
        all_users = self.db_manager.list_users(active_only=False)
        active_users = [u for u in all_users if u['is_active']]
        
        return {
            'total_users': len(all_users),
            'active_users': len(active_users),
            'inactive_users': len(all_users) - len(active_users)
        }
    
    def add_suggested_friend(self, user_name: str, suggested_friend_name: str) -> Dict[str, Any]:
        """Add a suggested friend for a user"""
        try:
            # Get user IDs
            user = self.db_manager.get_user_by_name(user_name)
            if not user:
                return {"success": False, "message": f"User '{user_name}' not found"}
            
            suggested_user = self.db_manager.get_user_by_name(suggested_friend_name)
            if not suggested_user:
                return {"success": False, "message": f"User '{suggested_friend_name}' not found"}
            
            if user['id'] == suggested_user['id']:
                return {"success": False, "message": "Cannot suggest yourself as a friend"}
            
            # Check if suggestion already exists
            existing = self.db_manager.get_suggested_friend(user['id'], suggested_user['id'])
            if existing:
                return {"success": False, "message": f"Friend suggestion already exists for {suggested_friend_name}"}
            
            # Add suggestion (bidirectional)
            self.db_manager.add_suggested_friend(user['id'], suggested_user['id'])
            self.db_manager.add_suggested_friend(suggested_user['id'], user['id'])
            
            return {"success": True, "message": f"Added {suggested_friend_name} as suggested friend"}
            
        except Exception as e:
            return {"success": False, "message": f"Error adding suggested friend: {str(e)}"}
    
    def get_suggested_friends(self, user_name: str) -> List[Dict[str, Any]]:
        """Get suggested friends for a user"""
        try:
            user = self.db_manager.get_user_by_name(user_name)
            if not user:
                return []
            
            suggestions = self.db_manager.get_suggested_friends(user['id'])
            return suggestions
            
        except Exception as e:
            return []
    
    def accept_suggested_friend(self, user_name: str, friend_name: str) -> Dict[str, Any]:
        """Accept a suggested friend"""
        try:
            user = self.db_manager.get_user_by_name(user_name)
            if not user:
                return {"success": False, "message": f"User '{user_name}' not found"}
            
            friend = self.db_manager.get_user_by_name(friend_name)
            if not friend:
                return {"success": False, "message": f"User '{friend_name}' not found"}
            
            # Update both directions to accepted
            self.db_manager.update_suggested_friend_status(user['id'], friend['id'], 'accepted')
            self.db_manager.update_suggested_friend_status(friend['id'], user['id'], 'accepted')
            
            return {"success": True, "message": f"Accepted {friend_name} as friend"}
            
        except Exception as e:
            return {"success": False, "message": f"Error accepting friend: {str(e)}"}
    
    def remove_suggested_friend(self, user_name: str, friend_name: str) -> Dict[str, Any]:
        """Remove a suggested friend"""
        try:
            user = self.db_manager.get_user_by_name(user_name)
            if not user:
                return {"success": False, "message": f"User '{user_name}' not found"}
            
            friend = self.db_manager.get_user_by_name(friend_name)
            if not friend:
                return {"success": False, "message": f"User '{friend_name}' not found"}
            
            # Remove both directions
            self.db_manager.remove_suggested_friend(user['id'], friend['id'])
            self.db_manager.remove_suggested_friend(friend['id'], user['id'])
            
            return {"success": True, "message": f"Removed {friend_name} from suggestions"}
            
        except Exception as e:
            return {"success": False, "message": f"Error removing friend: {str(e)}"}
    
    def get_friends(self, user_name: str) -> List[Dict[str, Any]]:
        """Get accepted friends for a user"""
        try:
            user = self.db_manager.get_user_by_name(user_name)
            if not user:
                return []
            
            friends = self.db_manager.get_accepted_friends(user['id'])
            return friends
            
        except Exception as e:
            return []