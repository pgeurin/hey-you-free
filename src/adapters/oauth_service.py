#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OAuth service for Google Calendar integration
Handles OAuth2 flow and token management
"""
import os
import json
import secrets
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from pathlib import Path

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import Flow
    from googleapiclient.discovery import build
    OAUTH_AVAILABLE = True
except ImportError:
    OAUTH_AVAILABLE = False
    print("⚠️ OAuth dependencies not installed. Run: mamba install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")


class OAuthService:
    """Service for handling Google OAuth2 flow"""
    
    def __init__(self):
        self.client_id = os.getenv('GOOGLE_CLIENT_ID')
        self.client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        self.redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8000/oauth/google/callback')
        self.scopes = ['https://www.googleapis.com/auth/calendar.readonly']
        
        # Persistent state storage using database
        self.state_storage = {}
        self._load_states_from_db()
        
        # Credentials file path
        self.credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
        self.token_file = os.getenv('GOOGLE_TOKEN_FILE', 'token.json')
    
    def is_configured(self) -> bool:
        """Check if OAuth is properly configured"""
        if not OAUTH_AVAILABLE:
            return False
        
        # Check if we have credentials file or client_id/secret
        if self.client_id and self.client_secret:
            return True
        
        if Path(self.credentials_file).exists():
            try:
                with open(self.credentials_file, 'r') as f:
                    creds = json.load(f)
                # Check if it has web or installed configuration
                return 'web' in creds or 'installed' in creds
            except Exception:
                return False
        
        return False
    
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
        """Get Google OAuth authorization URL"""
        if not self.is_configured():
            raise ValueError("OAuth not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET or provide credentials.json")
        
        # Generate state parameter for security
        state = secrets.token_urlsafe(32)
        
        # Store state with optional user_id
        state_data = {
            'user_id': user_id,
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(minutes=10)).isoformat()
        }
        self.state_storage[state] = state_data
        self._save_state_to_db(state, state_data)
        
        # Create flow
        if self.client_id and self.client_secret:
            # Use client_id/secret
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [self.redirect_uri]
                    }
                },
                scopes=self.scopes
            )
        else:
            # Use credentials file
            flow = Flow.from_client_secrets_file(
                self.credentials_file,
                scopes=self.scopes
            )
            # Set redirect URI for web flow
            flow.redirect_uri = self.redirect_uri
        
        # Get authorization URL
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=state
        )
        
        return auth_url, state
    
    def exchange_code_for_tokens(self, code: str, state: str) -> Dict[str, Any]:
        """Exchange authorization code for access tokens"""
        if not self.is_configured():
            raise ValueError("OAuth not configured")
        
        # Validate state
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
        
        # Create flow
        if self.client_id and self.client_secret:
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [self.redirect_uri]
                    }
                },
                scopes=self.scopes
            )
        else:
            flow = Flow.from_client_secrets_file(
                self.credentials_file,
                scopes=self.scopes
            )
            # Set redirect URI for web flow
            flow.redirect_uri = self.redirect_uri
        
        # Exchange code for tokens
        flow.fetch_token(code=code)
        
        # Get credentials
        credentials = flow.credentials
        
        # Store tokens
        token_data = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes,
            'expiry': credentials.expiry.isoformat() if credentials.expiry else None
        }
        
        # Clean up state
        del self.state_storage[state]
        self._delete_state_from_db(state)
        
        return {
            'credentials': token_data,
            'user_id': stored_state.get('user_id'),
            'expires_at': credentials.expiry.isoformat() if credentials.expiry else None
        }
    
    def refresh_tokens(self, token_data: Dict[str, Any]) -> Dict[str, Any]:
        """Refresh expired tokens"""
        if not OAUTH_AVAILABLE:
            raise ValueError("OAuth dependencies not available")
        
        # Create credentials from stored data
        credentials = Credentials(
            token=token_data.get('token'),
            refresh_token=token_data.get('refresh_token'),
            token_uri=token_data.get('token_uri'),
            client_id=token_data.get('client_id'),
            client_secret=token_data.get('client_secret'),
            scopes=token_data.get('scopes')
        )
        
        # Refresh if needed
        if credentials.expired:
            credentials.refresh(Request())
        
        # Return updated token data
        return {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes,
            'expiry': credentials.expiry.isoformat() if credentials.expiry else None
        }
    
    def get_calendar_service(self, token_data: Dict[str, Any]):
        """Get Google Calendar service with credentials"""
        if not OAUTH_AVAILABLE:
            raise ValueError("OAuth dependencies not available")
        
        # Create credentials
        credentials = Credentials(
            token=token_data.get('token'),
            refresh_token=token_data.get('refresh_token'),
            token_uri=token_data.get('token_uri'),
            client_id=token_data.get('client_id'),
            client_secret=token_data.get('client_secret'),
            scopes=token_data.get('scopes')
        )
        
        # Refresh if needed
        if credentials.expired:
            credentials.refresh(Request())
        
        # Build service
        service = build('calendar', 'v3', credentials=credentials)
        return service
    
    def test_calendar_access(self, token_data: Dict[str, Any]) -> bool:
        """Test if we can access the user's calendar"""
        try:
            service = self.get_calendar_service(token_data)
            # Try to get calendar list
            calendar_list = service.calendarList().list().execute()
            return True
        except Exception as e:
            print(f"Calendar access test failed: {e}")
            return False


# Global OAuth service instance
oauth_service = OAuthService()


def get_oauth_service() -> OAuthService:
    """Get OAuth service instance"""
    return oauth_service


def is_oauth_available() -> bool:
    """Check if OAuth is available and configured"""
    return OAUTH_AVAILABLE and oauth_service.is_configured()


if __name__ == "__main__":
    # Test OAuth configuration
    print("🔍 Testing OAuth configuration...")
    
    if not OAUTH_AVAILABLE:
        print("❌ OAuth dependencies not installed")
        print("💡 Run: mamba install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    else:
        print("✅ OAuth dependencies available")
    
    if oauth_service.is_configured():
        print("✅ OAuth is configured")
        try:
            auth_url, state = oauth_service.get_authorization_url()
            print(f"🔗 Authorization URL generated: {auth_url[:50]}...")
            print(f"🔐 State parameter: {state}")
        except Exception as e:
            print(f"❌ Error generating auth URL: {e}")
    else:
        print("❌ OAuth not configured")
        print("💡 Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables")
        print("💡 Or provide credentials.json file")
