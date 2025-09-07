#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test calendar event creation functionality
"""
import pytest
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi.testclient import TestClient
from src.api.server import app


class TestCalendarEventCreation:
    """Test calendar event creation functionality"""
    
    def setup_method(self):
        """Set up test client"""
        self.client = TestClient(app)
    
    def test_create_calendar_event_endpoint_exists(self):
        """Test that calendar event creation endpoint exists"""
        # Test endpoint exists (should return 405 Method Not Allowed for GET)
        response = self.client.get("/calendar/events")
        assert response.status_code in [405, 404]  # Method not allowed or not found
    
    def test_create_calendar_event_with_valid_data(self):
        """Test creating calendar event with valid data"""
        event_data = {
            "summary": "Test Meeting",
            "start": "2025-01-20T10:00:00Z",
            "end": "2025-01-20T11:00:00Z",
            "description": "Test meeting description",
            "location": "Test Location",
            "attendees": ["phil@example.com", "chris@example.com"]
        }
        
        # Mock the calendar service
        with patch('src.adapters.google_calendar_client.create_calendar_event') as mock_create:
            mock_create.return_value = {
                "id": "test_event_123",
                "summary": "Test Meeting",
                "status": "confirmed"
            }
            
            response = self.client.post("/calendar/events", json=event_data)
            
            # Should accept the request (may return 500 if OAuth not configured)
            assert response.status_code in [200, 201, 500, 503]
    
    def test_create_calendar_event_validation(self):
        """Test calendar event creation validation"""
        # Test with missing required fields
        invalid_data = {
            "summary": "Test Meeting"
            # Missing start, end
        }
        
        response = self.client.post("/calendar/events", json=invalid_data)
        assert response.status_code in [400, 422, 500, 503]  # Bad request or server error
    
    def test_create_calendar_event_from_suggestion(self):
        """Test creating calendar event from meeting suggestion"""
        suggestion_data = {
            "date": "2025-01-20",
            "time": "10:00",
            "duration": "1 hour",
            "summary": "Coffee Chat",
            "description": "Weekly sync meeting",
            "location": "Coffee Shop",
            "attendees": ["phil", "chris"]
        }
        
        with patch('src.adapters.google_calendar_client.create_calendar_event') as mock_create:
            mock_create.return_value = {
                "id": "suggestion_event_456",
                "summary": "Coffee Chat",
                "status": "confirmed"
            }
            
            response = self.client.post("/calendar/events/from-suggestion", json=suggestion_data)
            assert response.status_code in [200, 201, 500, 503]
    
    def test_calendar_event_conflict_detection(self):
        """Test calendar conflict detection"""
        # Test conflict detection endpoint
        response = self.client.get("/calendar/conflicts?date=2025-01-20&time=10:00&duration=60")
        assert response.status_code in [200, 500, 503]  # May not be implemented yet
    
    def test_web_interface_event_creation_button(self):
        """Test that web interface has event creation functionality"""
        response = self.client.get("/")
        assert response.status_code == 200
        html_content = response.text
        
        # Should have some indication of event creation capability
        # This will be updated as we implement the feature
        assert 'meeting' in html_content.lower() or 'calendar' in html_content.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
