#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Development OAuth service for local testing
Bypasses Google OAuth verification issues
"""
import os
import json
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple


class DevOAuthService:
    """Development OAuth service that simulates OAuth flow"""
    
    def __init__(self):
        self.redirect_uri = 'http://localhost:8000/oauth/google/callback'
        self.scopes = ['https://www.googleapis.com/auth/calendar.readonly']
        
        # Persistent state storage using database
        self.state_storage = {}
        self._load_states_from_db()
    
    def is_configured(self) -> bool:
        """Always configured in dev mode"""
        return True
    
    def _load_states_from_db(self):
        """Load OAuth states from database"""
        try:
            from infrastructure.database_postgres import get_database_manager
            db = get_database_manager()
            
            if not db.is_connected():
                db.connect()
            
            cursor = db.connection.cursor()
            cursor.execute("SELECT state_key, state_data FROM oauth_states WHERE expires_at > NOW()")
            rows = cursor.fetchall()
            cursor.close()
            
            for row in rows:
                state_key, state_data = row
                self.state_storage[state_key] = json.loads(state_data)
        except Exception as e:
            print(f"Warning: Could not load OAuth states from database: {e}")
    
    def _save_state_to_db(self, state: str, state_data: Dict[str, Any]):
        """Save OAuth state to database"""
        try:
            from infrastructure.database_postgres import get_database_manager
            db = get_database_manager()
            
            if not db.is_connected():
                db.connect()
            
            cursor = db.connection.cursor()
            cursor.execute(
                "INSERT INTO oauth_states (state_key, state_data, expires_at) VALUES (%(state_key)s, %(state_data)s, %(expires_at)s) ON CONFLICT (state_key) DO UPDATE SET state_data = %(state_data)s, expires_at = %(expires_at)s",
                {
                    'state_key': state,
                    'state_data': json.dumps(state_data),
                    'expires_at': state_data['expires_at']
                }
            )
            db.connection.commit()
            cursor.close()
        except Exception as e:
            print(f"Warning: Could not save OAuth state to database: {e}")
    
    def _delete_state_from_db(self, state: str):
        """Delete OAuth state from database"""
        try:
            from infrastructure.database_postgres import get_database_manager
            db = get_database_manager()
            
            if not db.is_connected():
                db.connect()
            
            cursor = db.connection.cursor()
            cursor.execute("DELETE FROM oauth_states WHERE state_key = %(state_key)s", {'state_key': state})
            db.connection.commit()
            cursor.close()
        except Exception as e:
            print(f"Warning: Could not delete OAuth state from database: {e}")
    
    def get_authorization_url(self, user_id: Optional[str] = None) -> Tuple[str, str]:
        """Get simulated authorization URL for development"""
        # Generate state parameter
        state = secrets.token_urlsafe(32)
        
        # Store state
        state_data = {
            'user_id': user_id,
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(minutes=10)).isoformat()
        }
        self.state_storage[state] = state_data
        self._save_state_to_db(state, state_data)
        
        # Return a local development URL that simulates OAuth
        auth_url = f"http://localhost:8000/oauth/dev/simulate?state={state}"
        return auth_url, state
    
    def exchange_code_for_tokens(self, code: str, state: str) -> Dict[str, Any]:
        """Simulate token exchange for development"""
        if state not in self.state_storage:
            # Try to reload from database
            self._load_states_from_db()
            if state not in self.state_storage:
                raise ValueError("Invalid state parameter")
        
        stored_state = self.state_storage[state]
        if datetime.utcnow() > datetime.fromisoformat(stored_state['expires_at']):
            del self.state_storage[state]
            self._delete_state_from_db(state)
            raise ValueError("State expired")
        
        # Simulate token data
        token_data = {
            'token': f'dev_token_{secrets.token_urlsafe(16)}',
            'refresh_token': f'dev_refresh_{secrets.token_urlsafe(16)}',
            'token_uri': 'https://oauth2.googleapis.com/token',
            'client_id': 'dev_client_id',
            'client_secret': 'dev_client_secret',
            'scopes': self.scopes,
            'expiry': (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }
        
        # Clean up state
        del self.state_storage[state]
        self._delete_state_from_db(state)
        
        return {
            'credentials': token_data,
            'user_id': stored_state.get('user_id'),
            'expires_at': token_data['expiry']
        }
    
    def test_calendar_access(self, token_data: Dict[str, Any]) -> bool:
        """Simulate calendar access test"""
        return True


# Global dev OAuth service instance
dev_oauth_service = DevOAuthService()


def get_dev_oauth_service() -> DevOAuthService:
    """Get dev OAuth service instance"""
    return dev_oauth_service


def is_dev_oauth_available() -> bool:
    """Check if dev OAuth is available"""
    return True


if __name__ == "__main__":
    print("🔧 Development OAuth Service")
    print("✅ Dev OAuth is always available")
    
    try:
        auth_url, state = dev_oauth_service.get_authorization_url()
        print(f"🔗 Dev Auth URL: {auth_url}")
        print(f"🔐 State: {state}")
    except Exception as e:
        print(f"❌ Error: {e}")
