#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test suite for Gemini client adapter
"""
import pytest
from unittest.mock import patch, MagicMock
from src.adapters.gemini_client import (
    load_gemini_api_key, 
    parse_gemini_response,
    get_meeting_suggestions_from_gemini
)


def test_load_gemini_api_key_success():
    """Test successful API key loading"""
    with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test-key'}):
        result = load_gemini_api_key()
        assert result == 'test-key'


def test_load_gemini_api_key_missing():
    """Test missing API key handling"""
    with patch.dict('os.environ', {}, clear=True):
        result = load_gemini_api_key()
        assert result is None


def test_parse_gemini_response_json_block():
    """Test parsing JSON from code block"""
    response = """Here are the suggestions:
    ```json
    {
      "suggestions": [
        {
          "date": "2025-01-20",
          "time": "10:00",
          "duration": "1 hour",
          "reasoning": "Good time for both",
          "phil_energy": "High",
          "chris_energy": "High",
          "meeting_type": "Coffee"
        }
      ]
    }
    ```"""
    
    result = parse_gemini_response(response)
    
    assert result is not None
    assert "suggestions" in result
    assert len(result["suggestions"]) == 1
    assert result["suggestions"][0]["date"] == "2025-01-20"


def test_parse_gemini_response_direct_json():
    """Test parsing direct JSON response"""
    response = '{"suggestions": [{"date": "2025-01-20", "time": "10:00", "duration": "1 hour", "reasoning": "Good time", "phil_energy": "High", "chris_energy": "High", "meeting_type": "Coffee"}]}'
    
    result = parse_gemini_response(response)
    
    assert result is not None
    assert "suggestions" in result


def test_parse_gemini_response_invalid_json():
    """Test handling invalid JSON"""
    response = "This is not JSON at all"
    
    result = parse_gemini_response(response)
    
    assert result is None


@patch('src.adapters.gemini_client.load_gemini_api_key')
def test_get_meeting_suggestions_from_gemini_no_api_key(mock_load_key):
    """Test handling missing API key"""
    mock_load_key.return_value = None
    
    result = get_meeting_suggestions_from_gemini("test prompt")
    
    assert result is None


@patch('src.adapters.gemini_client.load_gemini_api_key')
@patch('google.generativeai.GenerativeModel')
def test_get_meeting_suggestions_from_gemini_success(mock_model_class, mock_load_key):
    """Test successful Gemini API call"""
    mock_load_key.return_value = "test-key"
    mock_model = MagicMock()
    mock_model_class.return_value = mock_model
    mock_model.generate_content.return_value.text = '{"suggestions": []}'
    
    with patch('google.generativeai.configure'):
        result = get_meeting_suggestions_from_gemini("test prompt")
    
    assert result == '{"suggestions": []}'


if __name__ == "__main__":
    pytest.main([__file__])
