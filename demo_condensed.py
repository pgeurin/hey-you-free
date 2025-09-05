#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Condensed demo showing function calls and outputs
"""
import sys
import os
from unittest.mock import patch

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.infrastructure.calendar_loader import load_calendar_data
from src.core.meeting_scheduler import create_ai_prompt, validate_meeting_suggestions
from src.adapters.gemini_client import get_deterministic_meeting_suggestions, parse_gemini_response
from fastapi.testclient import TestClient
from src.api.server import app


def demo_condensed():
    """Condensed demo showing function calls and outputs"""
    print("🚀 CONDENSED MEETING SCHEDULER DEMO")
    print("="*50)
    
    phil_events = load_calendar_data('data/calendar_events_raw.json')
    print(f"phil_events = load_calendar_data('data/calendar_events_raw.json')  # {len(phil_events)} events loaded")
    chris_events = load_calendar_data('data/chris_calendar_events_raw.json')
    print(f"chris_events = load_calendar_data('data/chris_calendar_events_raw.json')  # {len(chris_events)} events loaded")
    ai_prompt = create_ai_prompt(phil_events, chris_events)
    print(f"ai_prompt = create_ai_prompt(phil_events, chris_events)  # {len(ai_prompt)} characters")
    mock_response = """```json
{
  "suggestions": [
    {
      "date": "2025-01-20",
      "time": "14:00",
      "duration": "1.5 hours",
      "reasoning": "Both participants are free and have high energy",
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
```"""
    
    with patch('src.adapters.gemini_client.get_meeting_suggestions_from_gemini', return_value=mock_response):
        ai_response = get_deterministic_meeting_suggestions(ai_prompt, seed=42)
    print(f"ai_response = get_deterministic_meeting_suggestions(ai_prompt, seed=42)  # {len(ai_response)} characters")
    suggestions = parse_gemini_response(ai_response)
    print(f"suggestions = parse_gemini_response(ai_response)  # {len(suggestions['suggestions'])} suggestions")
    is_valid, errors = validate_meeting_suggestions(suggestions)
    print(f"is_valid, errors = validate_meeting_suggestions(suggestions)  # {is_valid}")
    client = TestClient(app)
    print(f"client = TestClient(app)  # FastAPI client created")
    health_response = client.get('/health')
    print(f"health_response = client.get('/health')  # Status: {health_response.status_code}")
    with patch('src.api.server.get_meeting_suggestions_from_core', return_value=suggestions):
        api_response = client.get('/meeting-suggestions')
    print(f"api_response = client.get('/meeting-suggestions')  # Status: {api_response.status_code}, {len(api_response.json()['suggestions'])} suggestions")
    
    print("\n✅ All functions executed successfully!")
    print("✅ FastAPI server returns meeting events!")


if __name__ == "__main__":
    demo_condensed()
