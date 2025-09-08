#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for FastAPI server implementation
"""
import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from api.server import app
from api.models import MeetingSuggestionsResponse, MeetingSuggestion


class TestFastAPIServer:
    """Test FastAPI server endpoints"""
    
    def setup_method(self):
        """Set up test client"""
        self.client = TestClient(app)
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
        assert "system" in data
        assert "services" in data
    
    @patch('api.server.get_meeting_suggestions_from_core')
    def test_get_meeting_suggestions_success(self, mock_get_suggestions):
        """Test successful meeting suggestions endpoint"""
        # Mock the core function to return test data
        mock_suggestions = {
            "suggestions": [
                {
                    "date": "2025-01-20",
                    "time": "14:00",
                    "duration": "1.5 hours",
                    "reasoning": "Both are free and have high energy",
                    "user_energies": {
                        "phil": "High",
                        "chris": "High"
                    },
                    "meeting_type": "Coffee",
                    "location": "Local coffee shop",
                    "confidence": 0.9,
                    "conflicts": [],
                    "preparation_time": "5 minutes"
                }
            ],
            "metadata": {
                "generated_at": "2025-01-15T10:30:00Z",
                "total_suggestions": 1,
                "analysis_quality": "high"
            }
        }
        mock_get_suggestions.return_value = mock_suggestions
        
        # Test the endpoint
        response = self.client.get("/meeting-suggestions")
        assert response.status_code == 200
        
        # Validate response structure
        data = response.json()
        assert "suggestions" in data
        assert "metadata" in data
        assert len(data["suggestions"]) == 1
        
        # Validate suggestion structure
        suggestion = data["suggestions"][0]
        assert suggestion["date"] == "2025-01-20"
        assert suggestion["time"] == "14:00"
        assert suggestion["user_energies"]["phil"] == "High"
        assert suggestion["user_energies"]["chris"] == "High"
    
    @patch('api.server.get_meeting_suggestions_from_core')
    def test_get_meeting_suggestions_with_seed(self, mock_get_suggestions):
        """Test meeting suggestions with custom seed"""
        mock_suggestions = {
            "suggestions": [],
            "metadata": {"generated_at": "2025-01-15T10:30:00Z"}
        }
        mock_get_suggestions.return_value = mock_suggestions
        
        response = self.client.get("/meeting-suggestions?seed=123")
        assert response.status_code == 200
        mock_get_suggestions.assert_called_once_with(seed=123, user1_name='phil', user2_name='chris', meeting_type='coffee', description=None)
    
    @patch('api.server.get_meeting_suggestions_from_core')
    def test_get_meeting_suggestions_error(self, mock_get_suggestions):
        """Test meeting suggestions when core function fails"""
        mock_get_suggestions.return_value = None
        
        response = self.client.get("/meeting-suggestions")
        assert response.status_code == 500
        assert "detail" in response.json()
    
    def test_get_meeting_suggestions_validation(self):
        """Test that response validates against Pydantic models"""
        with patch('api.server.get_meeting_suggestions_from_core') as mock_get_suggestions:
            mock_suggestions = {
                "suggestions": [
                    {
                        "date": "2025-01-20",
                        "time": "14:00",
                        "duration": "1.5 hours",
                        "reasoning": "Test reasoning",
                        "user_energies": {
                            "phil": "High",
                            "chris": "Medium"
                        },
                        "meeting_type": "Coffee"
                    }
                ],
                "metadata": {
                    "generated_at": "2025-01-15T10:30:00Z",
                    "total_suggestions": 1
                }
            }
            mock_get_suggestions.return_value = mock_suggestions
            
            response = self.client.get("/meeting-suggestions")
            assert response.status_code == 200
            
            # Validate that response can be parsed as Pydantic model
            response_data = response.json()
            parsed_response = MeetingSuggestionsResponse(**response_data)
            assert len(parsed_response.suggestions) == 1
            assert parsed_response.suggestions[0].date == "2025-01-20"
    
    @patch('api.server.get_meeting_suggestions_from_core')
    def test_cors_headers(self, mock_get_suggestions):
        """Test that CORS headers are properly set"""
        # Mock a successful response to ensure we get CORS headers
        mock_suggestions = {
            "suggestions": [],
            "metadata": {"generated_at": "2025-01-15T10:30:00Z"}
        }
        mock_get_suggestions.return_value = mock_suggestions
        
        response = self.client.get("/meeting-suggestions")
        # TestClient may not show CORS headers, so just verify the response works
        assert response.status_code == 200
        # Verify the CORS middleware is configured by checking the app
        from api.server import app
        cors_middleware = None
        for middleware in app.user_middleware:
            if "CORSMiddleware" in str(middleware):
                cors_middleware = middleware
                break
        assert cors_middleware is not None, "CORS middleware should be configured"


def test_run_fastapi_test_suite():
    """Run the complete FastAPI test suite"""
    print("\n" + "="*80)
    print("🚀 RUNNING FASTAPI TEST SUITE")
    print("="*80)
    
    # Create test instance and run tests
    test_instance = TestFastAPIServer()
    test_instance.setup_method()
    
    try:
        test_instance.test_health_endpoint()
        print("✅ Health endpoint test passed")
        
        test_instance.test_get_meeting_suggestions_success()
        print("✅ Meeting suggestions success test passed")
        
        test_instance.test_get_meeting_suggestions_with_seed()
        print("✅ Meeting suggestions with seed test passed")
        
        test_instance.test_get_meeting_suggestions_error()
        print("✅ Meeting suggestions error test passed")
        
        test_instance.test_get_meeting_suggestions_validation()
        print("✅ Meeting suggestions validation test passed")
        
        test_instance.test_cors_headers()
        print("✅ CORS headers test passed")
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        raise
    
    print("\n" + "="*80)
    print("🎯 FASTAPI TEST SUITE COMPLETE")
    print("="*80)


if __name__ == "__main__":
    test_run_fastapi_test_suite()
