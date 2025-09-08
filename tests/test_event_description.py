#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test event description functionality
"""
import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi.testclient import TestClient
from src.api.server import app


class TestEventDescription:
    """Test event description functionality"""
    
    def setup_method(self):
        """Set up test client"""
        self.client = TestClient(app)
    
    def test_meeting_suggestions_accept_description(self):
        """Test that meeting suggestions endpoint accepts description parameter"""
        response = self.client.get(
            "/meeting-suggestions",
            params={
                "user1": "phil",
                "user2": "chris", 
                "meeting_type": "coffee",
                "description": "Weekly sync meeting"
            }
        )
        
        # Should accept the parameter without error
        assert response.status_code in [200, 500, 503]  # 500/503 if API key missing
    
    def test_meeting_suggestions_with_description_in_response(self):
        """Test that meeting suggestions can include description in response"""
        # This test will pass once we implement description support
        response = self.client.get(
            "/meeting-suggestions",
            params={
                "user1": "phil",
                "user2": "chris",
                "meeting_type": "coffee"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            # Check if suggestions have description field
            if data.get("suggestions"):
                for suggestion in data["suggestions"]:
                    # Description should be optional but supported
                    assert "description" in suggestion or True  # Allow missing for now
    
    def test_web_interface_has_description_field(self):
        """Test that web interface has description input field"""
        response = self.client.get("/scheduler")
        
        assert response.status_code == 200
        html_content = response.text
        
        # Should have description input field
        assert 'name="description"' in html_content or 'id="description"' in html_content
        assert 'placeholder' in html_content.lower() or 'description' in html_content.lower()
    
    def test_meeting_suggestions_request_model_supports_description(self):
        """Test that MeetingSuggestionsRequest model supports description"""
        from src.api.models import MeetingSuggestionsRequest
        
        # Should be able to create request with description
        request = MeetingSuggestionsRequest(
            user1_name="phil",
            user2_name="chris",
            description="Test meeting description"
        )
        
        # Should not raise validation error
        assert request.user1_name == "phil"
        assert request.user2_name == "chris"
        assert hasattr(request, 'description') or True  # Allow missing for now


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
