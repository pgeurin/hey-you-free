#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test suite for meeting scheduler core logic
"""
import pytest
from datetime import datetime
from src.core.meeting_scheduler import format_events_for_ai, create_ai_prompt


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


def test_create_ai_prompt_includes_current_date():
    """Test AI prompt includes current date"""
    phil_events = []
    chris_events = []
    
    prompt = create_ai_prompt(phil_events, chris_events)
    
    current_date = datetime.now().strftime('%Y-%m-%d')
    assert current_date in prompt


if __name__ == "__main__":
    pytest.main([__file__])
