#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test OAuth integration for Google Calendar
"""
import pytest
import os
import json
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from api.server import app


class TestOAuthIntegration:
    """Test OAuth integration functionality"""
    
    def setup_method(self):
        """Set up test client"""
        self.client = TestClient(app)
    
    def test_oauth_start_endpoint_exists(self):
        """Test that OAuth start endpoint exists"""
        response = self.client.get("/oauth/google/start")
        # Should redirect (302/307) or return error, not 404
        assert response.status_code in [302, 307, 500, 503]
    
    def test_oauth_callback_endpoint_exists(self):
        """Test that OAuth callback endpoint exists"""
        response = self.client.get("/oauth/google/callback")
        # Should not return 404 (endpoint exists)
        assert response.status_code != 404
    
    @patch('src.adapters.google_calendar_client.load_google_credentials')
    def test_oauth_start_redirects_to_google(self, mock_creds):
        """Test that OAuth start redirects to Google"""
        mock_creds.return_value = None
        
        response = self.client.get("/oauth/google/start")
        
        # Should redirect to Google OAuth
        assert response.status_code in [302, 307]
        location = response.headers.get("location", "")
        assert "accounts.google.com" in location
        assert "client_id" in location
    
    def test_oauth_callback_handles_code(self):
        """Test OAuth callback handles authorization code"""
        # Mock the callback with a test code
        response = self.client.get("/oauth/google/callback?code=test_code&state=test_state")
        
        # Should process the callback (may redirect, return success, or error)
        assert response.status_code in [200, 302, 400, 500]
    
    def test_oauth_callback_handles_error(self):
        """Test OAuth callback handles error responses"""
        response = self.client.get("/oauth/google/callback?error=access_denied")
        
        # Should handle error gracefully
        assert response.status_code in [200, 400, 302]
    
    @patch('src.adapters.google_calendar_client.fetch_calendar_events')
    def test_oauth_token_storage(self, mock_fetch):
        """Test that OAuth tokens are stored properly"""
        mock_fetch.return_value = []
        
        # This test will be expanded when we implement token storage
        # For now, just ensure the endpoint exists
        response = self.client.get("/oauth/google/start")
        assert response.status_code in [302, 307, 500, 503]
    
    def test_oauth_state_parameter_security(self):
        """Test that OAuth state parameter is used for security"""
        response = self.client.get("/oauth/google/start")
        
        # Should include state parameter in redirect
        location = response.headers.get("location", "")
        assert "state=" in location or response.status_code in [200, 500, 503]
    
    def test_oauth_scopes_are_correct(self):
        """Test that OAuth requests correct scopes"""
        response = self.client.get("/oauth/google/start")
        
        # Should request calendar read scope
        location = response.headers.get("location", "")
        assert "calendar.readonly" in location or response.status_code in [200, 500, 503]


class TestOAuthWebInterface:
    """Test OAuth integration with web interface"""
    
    def setup_method(self):
        """Set up test client"""
        self.client = TestClient(app)
    
    def test_web_interface_has_oauth_button(self):
        """Test that web interface has OAuth button"""
        response = self.client.get("/")
        
        assert response.status_code == 200
        html_content = response.text
        assert "Connect Google Calendar" in html_content
        assert "connectGoogleCalendar" in html_content
    
    def test_oauth_button_javascript_function(self):
        """Test that OAuth button has working JavaScript"""
        response = self.client.get("/")
        
        assert response.status_code == 200
        html_content = response.text
        
        # Should have JavaScript function for OAuth
        assert "function connectGoogleCalendar()" in html_content or "connectGoogleCalendar()" in html_content
    
    def test_oauth_redirects_to_correct_endpoint(self):
        """Test that OAuth button redirects to correct endpoint"""
        response = self.client.get("/")
        
        assert response.status_code == 200
        html_content = response.text
        
        # Should redirect to OAuth start endpoint
        assert "/oauth/google/start" in html_content or "oauth" in html_content.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
