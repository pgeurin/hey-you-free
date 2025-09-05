#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Capture deterministic response from Gemini AI for testing
"""
import os
import json
from pathlib import Path
from src.core.meeting_scheduler import create_ai_prompt
from src.adapters.gemini_client import get_deterministic_meeting_suggestions, parse_gemini_response

def load_env_file():
    """Load environment variables from .env file if it exists"""
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

def create_test_calendar_data():
    """Create the same test data used in tests"""
    return {
        "phil_events": [
            {
                "kind": "calendar#event",
                "summary": "Morning Standup",
                "start": {"dateTime": "2025-01-16T09:00:00Z"},
                "location": "Office",
                "description": "Daily team sync"
            },
            {
                "kind": "calendar#event",
                "summary": "Client Meeting",
                "start": {"dateTime": "2025-01-16T14:00:00Z"},
                "location": "Conference Room A",
                "description": "Project review with client"
            },
            {
                "kind": "calendar#event",
                "summary": "Coffee Break",
                "start": {"dateTime": "2025-01-17T10:30:00Z"},
                "location": "Downtown Cafe",
                "description": "Casual coffee with team"
            },
            {
                "kind": "calendar#event",
                "summary": "Deep Work",
                "start": {"dateTime": "2025-01-17T15:00:00Z"},
                "location": "Home Office",
                "description": "Focused coding session"
            },
            {
                "kind": "calendar#event",
                "summary": "Evening Drinks",
                "start": {"dateTime": "2025-01-18T18:00:00Z"},
                "location": "Local Bar",
                "description": "Social time with friends"
            }
        ],
        "chris_events": [
            {
                "kind": "calendar#event",
                "summary": "Work Session",
                "start": {"dateTime": "2025-01-16T08:00:00Z"},
                "location": "Home",
                "description": "Early morning productivity"
            },
            {
                "kind": "calendar#event",
                "summary": "Team Meeting",
                "start": {"dateTime": "2025-01-16T11:00:00Z"},
                "location": "Office",
                "description": "Weekly planning session"
            },
            {
                "kind": "calendar#event",
                "summary": "Lunch with Colleagues",
                "start": {"dateTime": "2025-01-17T12:00:00Z"},
                "location": "Restaurant",
                "description": "Team building lunch"
            },
            {
                "kind": "calendar#event",
                "summary": "Gym Session",
                "start": {"dateTime": "2025-01-17T17:00:00Z"},
                "location": "Fitness Center",
                "description": "Regular workout"
            },
            {
                "kind": "calendar#event",
                "summary": "Family Dinner",
                "start": {"dateTime": "2025-01-18T19:00:00Z"},
                "location": "Home",
                "description": "Weekly family time"
            }
        ]
    }

def capture_deterministic_response():
    """Capture the deterministic response from Gemini AI"""
    print("🔍 Capturing deterministic response from Gemini AI...")
    
    # Load .env file
    load_env_file()
    
    # Check if API key is available
    if not os.getenv('GOOGLE_API_KEY'):
        print("❌ GOOGLE_API_KEY not found. Please set it in .env file or environment.")
        return None
    
    # Create test data
    data = create_test_calendar_data()
    
    # Generate prompt
    prompt = create_ai_prompt(data["phil_events"], data["chris_events"])
    
    # Get deterministic response
    print("🤖 Calling Gemini AI with temperature=0.0 and seed=42...")
    response = get_deterministic_meeting_suggestions(prompt, seed=42)
    
    if not response:
        print("❌ Failed to get response from Gemini AI")
        return None
    
    # Parse and validate response
    suggestions = parse_gemini_response(response)
    
    if not suggestions:
        print("❌ Failed to parse response from Gemini AI")
        print("Raw response:")
        print(response)
        return None
    
    print("✅ Successfully captured deterministic response!")
    print(f"   Generated {len(suggestions['suggestions'])} suggestions")
    
    # Save the response
    with open("deterministic_response.json", "w") as f:
        json.dump(suggestions, f, indent=2)
    
    print("💾 Response saved to deterministic_response.json")
    
    # Print the response for inspection
    print("\n📋 Captured Response:")
    print("=" * 60)
    print(json.dumps(suggestions, indent=2))
    print("=" * 60)
    
    return suggestions

if __name__ == "__main__":
    capture_deterministic_response()
