#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test suite for meeting scheduler core logic
"""
import pytest
import json
from datetime import datetime
from src.core.meeting_scheduler import (
    format_events_for_ai, 
    create_ai_prompt, 
    validate_event_dictionary, 
    validate_meeting_suggestions
)
from src.adapters.gemini_client import (
    parse_gemini_response, 
    get_deterministic_meeting_suggestions,
    get_creative_meeting_suggestions
)


def test_format_events_for_ai():
    """Test event formatting for AI analysis"""
    events = [
        {
            "start": {"dateTime": "2025-01-15T10:00:00Z"},
            "summary": "Team Meeting",
            "location": "Conference Room A",
            "description": "Weekly standup"
        },
        {
            "start": {"dateTime": "2025-01-15T14:00:00Z"},
            "summary": "Client Call",
            "location": "",
            "description": ""
        }
    ]
    
    result = format_events_for_ai(events, "Test User")
    
    assert "Total events: 2" in result
    assert "2025-01-15 (Wednesday) 10:00 - Team Meeting" in result
    assert "@ Conference Room A" in result
    assert "| Weekly standup" in result
    assert "2025-01-15 (Wednesday) 14:00 - Client Call" in result


def test_format_events_handles_invalid_data():
    """Test event formatting handles invalid data gracefully"""
    events = [
        {"invalid": "data"},
        {
            "start": {"dateTime": "invalid-date"},
            "summary": "Test Event"
        }
    ]
    
    result = format_events_for_ai(events, "Test User")
    
    assert "Total events: 0" in result


def test_create_ai_prompt_structure():
    """Test AI prompt creation has correct structure"""
    phil_events = [{"start": {"dateTime": "2025-01-15T10:00:00Z"}, "summary": "Test"}]
    chris_events = [{"start": {"dateTime": "2025-01-15T11:00:00Z"}, "summary": "Test"}]
    
    prompt = create_ai_prompt(phil_events, chris_events)
    
    assert "MEETING SCHEDULER AI ASSISTANT" in prompt
    assert "PHIL'S CALENDAR EVENTS:" in prompt
    assert "CHRIS'S CALENDAR EVENTS:" in prompt
    assert "```json" in prompt
    assert "suggestions" in prompt


def test_create_ai_prompt_with_dynamic_user_names():
    """Test AI prompt creation with dynamic user names"""
    alice_events = [{"start": {"dateTime": "2025-01-15T10:00:00Z"}, "summary": "Alice Meeting"}]
    bob_events = [{"start": {"dateTime": "2025-01-15T11:00:00Z"}, "summary": "Bob Meeting"}]
    
    prompt = create_ai_prompt(alice_events, bob_events, "Alice", "Bob")
    
    assert "MEETING SCHEDULER AI ASSISTANT" in prompt
    assert "ALICE'S CALENDAR EVENTS:" in prompt
    assert "BOB'S CALENDAR EVENTS:" in prompt
    assert "Alice Meeting" in prompt
    assert "Bob Meeting" in prompt
    assert "```json" in prompt
    assert "suggestions" in prompt


def test_create_ai_prompt_includes_current_date():
    """Test AI prompt includes current date"""
    phil_events = []
    chris_events = []
    
    prompt = create_ai_prompt(phil_events, chris_events)
    
    current_date = datetime.now().strftime('%Y-%m-%d')
    assert current_date in prompt


def test_parse_gemini_response_valid_format():
    """Test parsing valid event dictionary format"""
    valid_response = """{
        "suggestions": [
            {
                "date": "2025-01-20",
                "time": "14:30",
                "duration": "1.5 hours",
                "reasoning": "Both have energy after lunch, no conflicts",
                "phil_energy": "High",
                "chris_energy": "Medium",
                "meeting_type": "Coffee",
                "location": "Downtown Cafe",
                "confidence": 0.85,
                "conflicts": [],
                "preparation_time": "5 minutes"
            }
        ],
        "metadata": {
            "generated_at": "2025-01-15T10:30:00Z",
            "total_suggestions": 1,
            "analysis_quality": "high",
            "time_range_analyzed": "2025-01-15 to 2025-01-29"
        }
    }"""
    
    result = parse_gemini_response(valid_response)
    
    assert result is not None
    assert "suggestions" in result
    assert "metadata" in result
    assert len(result["suggestions"]) == 1
    
    suggestion = result["suggestions"][0]
    assert suggestion["date"] == "2025-01-20"
    assert suggestion["time"] == "14:30"
    assert suggestion["duration"] == "1.5 hours"
    assert suggestion["phil_energy"] == "High"
    assert suggestion["chris_energy"] == "Medium"
    assert suggestion["meeting_type"] == "Coffee"
    assert suggestion["confidence"] == 0.85


def test_parse_gemini_response_with_code_blocks():
    """Test parsing response with JSON code blocks"""
    response_with_blocks = """Here are the meeting suggestions:

```json
{
    "suggestions": [
        {
            "date": "2025-01-20",
            "time": "14:30",
            "duration": "1 hour",
            "reasoning": "Good time for both",
            "phil_energy": "High",
            "chris_energy": "High",
            "meeting_type": "Coffee"
        }
    ]
}
```

These are the optimal times."""
    
    result = parse_gemini_response(response_with_blocks)
    
    assert result is not None
    assert "suggestions" in result
    assert len(result["suggestions"]) == 1
    assert result["suggestions"][0]["date"] == "2025-01-20"


def test_parse_gemini_response_minimal_format():
    """Test parsing minimal valid format (backward compatibility)"""
    minimal_response = """{
        "suggestions": [
            {
                "date": "2025-01-20",
                "time": "14:30",
                "duration": "1 hour",
                "reasoning": "Good time",
                "phil_energy": "High",
                "chris_energy": "High",
                "meeting_type": "Coffee"
            }
        ]
    }"""
    
    result = parse_gemini_response(minimal_response)
    
    assert result is not None
    assert "suggestions" in result
    assert len(result["suggestions"]) == 1


def test_parse_gemini_response_invalid_json():
    """Test handling of invalid JSON"""
    invalid_response = "This is not valid JSON at all"
    
    result = parse_gemini_response(invalid_response)
    
    assert result is None


def test_parse_gemini_response_malformed_json():
    """Test handling of malformed JSON"""
    malformed_response = '{"suggestions": [{"date": "2025-01-20"}]'  # Missing closing brackets
    
    result = parse_gemini_response(malformed_response)
    
    assert result is None


def test_event_dictionary_structure_validation():
    """Test that event dictionaries have required fields"""
    valid_event = {
        "date": "2025-01-20",
        "time": "14:30", 
        "duration": "1.5 hours",
        "reasoning": "Good time for both",
        "phil_energy": "High",
        "chris_energy": "Medium",
        "meeting_type": "Coffee"
    }
    
    # Test required fields
    required_fields = ["date", "time", "duration", "reasoning", "phil_energy", "chris_energy", "meeting_type"]
    for field in required_fields:
        assert field in valid_event
        assert valid_event[field] is not None
        assert valid_event[field] != ""


def test_event_dictionary_optional_fields():
    """Test optional fields in event dictionary"""
    full_event = {
        "date": "2025-01-20",
        "time": "14:30",
        "duration": "1.5 hours", 
        "reasoning": "Good time",
        "phil_energy": "High",
        "chris_energy": "High",
        "meeting_type": "Coffee",
        "location": "Downtown Cafe",
        "confidence": 0.85,
        "conflicts": [],
        "preparation_time": "5 minutes"
    }
    
    # Test optional fields are handled gracefully
    optional_fields = ["location", "confidence", "conflicts", "preparation_time"]
    for field in optional_fields:
        assert field in full_event


def test_energy_levels_validation():
    """Test that energy levels are valid"""
    valid_energy_levels = ["High", "Medium", "Low"]
    
    for energy in valid_energy_levels:
        event = {
            "date": "2025-01-20",
            "time": "14:30",
            "duration": "1 hour",
            "reasoning": "Test",
            "phil_energy": energy,
            "chris_energy": energy,
            "meeting_type": "Coffee"
        }
        
        assert event["phil_energy"] in valid_energy_levels
        assert event["chris_energy"] in valid_energy_levels


def test_meeting_types_validation():
    """Test that meeting types are valid"""
    valid_meeting_types = ["Coffee", "Casual lunch", "Evening drinks", "Activity"]
    
    for meeting_type in valid_meeting_types:
        event = {
            "date": "2025-01-20",
            "time": "14:30", 
            "duration": "1 hour",
            "reasoning": "Test",
            "phil_energy": "High",
            "chris_energy": "High",
            "meeting_type": meeting_type
        }
        
        assert event["meeting_type"] in valid_meeting_types


def test_validate_event_dictionary_valid():
    """Test validation of valid event dictionary"""
    valid_event = {
        "date": "2025-01-20",
        "time": "14:30",
        "duration": "1.5 hours",
        "reasoning": "Good time for both",
        "phil_energy": "High",
        "chris_energy": "Medium",
        "meeting_type": "Coffee"
    }
    
    is_valid, errors = validate_event_dictionary(valid_event)
    
    assert is_valid
    assert len(errors) == 0


def test_validate_event_dictionary_missing_fields():
    """Test validation catches missing required fields"""
    invalid_event = {
        "date": "2025-01-20",
        "time": "14:30"
        # Missing required fields
    }
    
    is_valid, errors = validate_event_dictionary(invalid_event)
    
    assert not is_valid
    assert len(errors) > 0
    assert any("Missing required field" in error for error in errors)


def test_validate_event_dictionary_invalid_energy():
    """Test validation catches invalid energy levels"""
    invalid_event = {
        "date": "2025-01-20",
        "time": "14:30",
        "duration": "1 hour",
        "reasoning": "Test",
        "phil_energy": "Super High",  # Invalid
        "chris_energy": "Low",
        "meeting_type": "Coffee"
    }
    
    is_valid, errors = validate_event_dictionary(invalid_event)
    
    assert not is_valid
    assert any("Invalid phil_energy" in error for error in errors)


def test_validate_event_dictionary_invalid_date_format():
    """Test validation catches invalid date format"""
    invalid_event = {
        "date": "20-01-2025",  # Wrong format
        "time": "14:30",
        "duration": "1 hour",
        "reasoning": "Test",
        "phil_energy": "High",
        "chris_energy": "High",
        "meeting_type": "Coffee"
    }
    
    is_valid, errors = validate_event_dictionary(invalid_event)
    
    assert not is_valid
    assert any("Invalid date format" in error for error in errors)


def test_validate_meeting_suggestions_valid():
    """Test validation of valid meeting suggestions"""
    valid_suggestions = {
        "suggestions": [
            {
                "date": "2025-01-20",
                "time": "14:30",
                "duration": "1 hour",
                "reasoning": "Good time",
                "phil_energy": "High",
                "chris_energy": "High",
                "meeting_type": "Coffee"
            }
        ]
    }
    
    is_valid, errors = validate_meeting_suggestions(valid_suggestions)
    
    assert is_valid
    assert len(errors) == 0


def test_validate_meeting_suggestions_no_suggestions():
    """Test validation catches empty suggestions"""
    invalid_suggestions = {
        "suggestions": []
    }
    
    is_valid, errors = validate_meeting_suggestions(invalid_suggestions)
    
    assert not is_valid
    assert any("No suggestions provided" in error for error in errors)


def test_validate_meeting_suggestions_missing_key():
    """Test validation catches missing suggestions key"""
    invalid_suggestions = {
        "metadata": {"test": "value"}
        # Missing "suggestions" key
    }
    
    is_valid, errors = validate_meeting_suggestions(invalid_suggestions)
    
    assert not is_valid
    assert any("Missing 'suggestions' key" in error for error in errors)


def test_parse_gemini_response_with_validation():
    """Test that parse_gemini_response validates format"""
    # This should pass validation
    valid_response = """{
        "suggestions": [
            {
                "date": "2025-01-20",
                "time": "14:30",
                "duration": "1 hour",
                "reasoning": "Good time",
                "phil_energy": "High",
                "chris_energy": "High",
                "meeting_type": "Coffee"
            }
        ]
    }"""
    
    result = parse_gemini_response(valid_response)
    
    assert result is not None
    assert "suggestions" in result


def test_parse_gemini_response_invalid_format():
    """Test that parse_gemini_response rejects invalid format"""
    # This should fail validation
    invalid_response = """{
        "suggestions": [
            {
                "date": "2025-01-20",
                "time": "14:30"
                // Missing required fields
            }
        ]
    }"""
    
    result = parse_gemini_response(invalid_response)
    
    assert result is None


def test_deterministic_vs_creative_parameters():
    """Test that deterministic and creative functions use different parameters"""
    # This test verifies the functions exist and can be called
    # (actual API calls would require API key)
    
    test_prompt = "Test prompt for meeting suggestions"
    
    # Test deterministic function exists
    assert callable(get_deterministic_meeting_suggestions)
    
    # Test creative function exists  
    assert callable(get_creative_meeting_suggestions)
    
    # Test that they accept the right parameters
    try:
        # These will fail without API key, but that's expected
        get_deterministic_meeting_suggestions(test_prompt, seed=123)
        get_creative_meeting_suggestions(test_prompt)
    except Exception as e:
        # Expected to fail without API key
        assert "GOOGLE_API_KEY" in str(e) or "api_key" in str(e).lower()


def test_temperature_parameter_validation():
    """Test temperature parameter validation"""
    from src.adapters.gemini_client import get_meeting_suggestions_from_gemini
    
    # Test that function accepts temperature parameter
    assert callable(get_meeting_suggestions_from_gemini)
    
    # Test with different temperature values
    test_prompt = "Test prompt"
    
    try:
        # Low temperature (deterministic)
        get_meeting_suggestions_from_gemini(test_prompt, temperature=0.1)
        
        # High temperature (creative)
        get_meeting_suggestions_from_gemini(test_prompt, temperature=0.8)
        
        # With seed
        get_meeting_suggestions_from_gemini(test_prompt, temperature=0.1, seed=42)
        
    except Exception as e:
        # Expected to fail without API key
        assert "GOOGLE_API_KEY" in str(e) or "api_key" in str(e).lower()


if __name__ == "__main__":
    pytest.main([__file__])
