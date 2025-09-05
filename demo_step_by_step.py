#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step-by-step demo showing each function call and output
Demonstrates the complete meeting scheduler workflow
"""
import sys
import os
import json
from datetime import datetime
from unittest.mock import patch

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.meeting_scheduler import (
    format_events_for_ai, 
    create_ai_prompt, 
    validate_meeting_suggestions
)
from src.adapters.gemini_client import (
    get_meeting_suggestions_from_gemini,
    parse_gemini_response,
    get_deterministic_meeting_suggestions
)
from src.infrastructure.calendar_loader import (
    load_calendar_data,
    save_prompt_to_file,
    save_suggestions_to_file
)
from fastapi.testclient import TestClient
from src.api.server import app


def demo_step_by_step():
    """Demonstrate each function call step by step"""
    print("\n" + "="*80)
    print("🚀 STEP-BY-STEP MEETING SCHEDULER DEMO")
    print("="*80)
    
    # Step 1: Load calendar data
    print("\n📅 STEP 1: Load Calendar Data")
    print("-" * 40)
    print("phil_events = load_calendar_data('data/calendar_events_raw.json')")
    phil_events = load_calendar_data('data/calendar_events_raw.json')
    print(f"✅ Result: Loaded {len(phil_events)} events for Phil")
    print(f"   First event: {phil_events[0]['summary'] if phil_events else 'No events'}")
    
    print("\nchris_events = load_calendar_data('data/chris_calendar_events_raw.json')")
    chris_events = load_calendar_data('data/chris_calendar_events_raw.json')
    print(f"✅ Result: Loaded {len(chris_events)} events for Chris")
    print(f"   First event: {chris_events[0]['summary'] if chris_events else 'No events'}")
    
    # Step 2: Format events for AI
    print("\n🤖 STEP 2: Format Events for AI")
    print("-" * 40)
    print("phil_formatted = format_events_for_ai(phil_events, 'Phil')")
    phil_formatted = format_events_for_ai(phil_events, 'Phil')
    print(f"✅ Result: Formatted {len(phil_formatted)} characters")
    print(f"   Preview: {phil_formatted[:100]}...")
    
    print("\nchris_formatted = format_events_for_ai(chris_events, 'Chris')")
    chris_formatted = format_events_for_ai(chris_events, 'Chris')
    print(f"✅ Result: Formatted {len(chris_formatted)} characters")
    print(f"   Preview: {chris_formatted[:100]}...")
    
    # Step 3: Create AI prompt
    print("\n📝 STEP 3: Create AI Prompt")
    print("-" * 40)
    print("ai_prompt = create_ai_prompt(phil_events, chris_events)")
    ai_prompt = create_ai_prompt(phil_events, chris_events)
    print(f"✅ Result: Created prompt with {len(ai_prompt)} characters")
    print(f"   Contains current date: {datetime.now().strftime('%Y-%m-%d') in ai_prompt}")
    print(f"   Preview: {ai_prompt[:200]}...")
    
    # Step 4: Save prompt to file
    print("\n💾 STEP 4: Save Prompt to File")
    print("-" * 40)
    print("save_prompt_to_file(ai_prompt, 'output/meeting_scheduler_prompt.txt')")
    save_prompt_to_file(ai_prompt, 'output/meeting_scheduler_prompt.txt')
    print("✅ Result: Prompt saved to output/meeting_scheduler_prompt.txt")
    
    # Step 5: Get AI suggestions (with mock for demo)
    print("\n🧠 STEP 5: Get AI Suggestions")
    print("-" * 40)
    print("ai_response = get_deterministic_meeting_suggestions(ai_prompt, seed=42)")
    
    # Mock the AI response for demo
    mock_ai_response = """```json
{
  "suggestions": [
    {
      "date": "2025-01-20",
      "time": "14:00",
      "duration": "1.5 hours",
      "reasoning": "Both participants are free and have high energy levels",
      "user_energies": {
        "phil": "High",
        "chris": "High"
      },
      "meeting_type": "Coffee",
      "location": "Local coffee shop",
      "confidence": 0.9,
      "conflicts": [],
      "preparation_time": "5 minutes"
    },
    {
      "date": "2025-01-22",
      "time": "10:00",
      "duration": "2 hours",
      "reasoning": "Morning energy is optimal for both participants",
      "user_energies": {
        "phil": "High",
        "chris": "Medium"
      },
      "meeting_type": "Casual lunch",
      "location": "Downtown restaurant",
      "confidence": 0.8,
      "conflicts": [],
      "preparation_time": "10 minutes"
    }
  ],
  "metadata": {
    "generated_at": "2025-01-15T10:30:00Z",
    "total_suggestions": 2,
    "analysis_quality": "high"
  }
}
```"""
    
    with patch('src.adapters.gemini_client.get_meeting_suggestions_from_gemini', return_value=mock_ai_response):
        ai_response = get_deterministic_meeting_suggestions(ai_prompt, seed=42)
    
    print(f"✅ Result: AI response received ({len(ai_response)} characters)")
    print(f"   Preview: {ai_response[:100]}...")
    
    # Step 6: Parse AI response
    print("\n🔍 STEP 6: Parse AI Response")
    print("-" * 40)
    print("suggestions = parse_gemini_response(ai_response)")
    suggestions = parse_gemini_response(ai_response)
    print(f"✅ Result: Parsed {len(suggestions['suggestions'])} suggestions")
    print(f"   First suggestion: {suggestions['suggestions'][0]['date']} at {suggestions['suggestions'][0]['time']}")
    print(f"   Meeting type: {suggestions['suggestions'][0]['meeting_type']}")
    
    # Step 7: Validate suggestions
    print("\n✅ STEP 7: Validate Suggestions")
    print("-" * 40)
    print("is_valid, errors = validate_meeting_suggestions(suggestions)")
    is_valid, errors = validate_meeting_suggestions(suggestions)
    print(f"✅ Result: Validation {'PASSED' if is_valid else 'FAILED'}")
    if errors:
        print(f"   Errors: {errors}")
    else:
        print("   No validation errors found")
    
    # Step 8: Save suggestions to file
    print("\n💾 STEP 8: Save Suggestions to File")
    print("-" * 40)
    print("save_suggestions_to_file(suggestions, 'output/meeting_suggestions.json')")
    save_suggestions_to_file(suggestions, 'output/meeting_suggestions.json')
    print("✅ Result: Suggestions saved to output/meeting_suggestions.json")
    
    # Step 9: Test FastAPI server
    print("\n🌐 STEP 9: Test FastAPI Server")
    print("-" * 40)
    print("client = TestClient(app)")
    client = TestClient(app)
    print("✅ Result: FastAPI test client created")
    
    print("\nhealth_response = client.get('/health')")
    health_response = client.get('/health')
    print(f"✅ Result: Status {health_response.status_code}")
    print(f"   Response: {health_response.json()}")
    
    print("\n# Mock the core function for API test")
    print("with patch('src.api.server.get_meeting_suggestions_from_core', return_value=suggestions):")
    print("    api_response = client.get('/meeting-suggestions')")
    
    with patch('src.api.server.get_meeting_suggestions_from_core', return_value=suggestions):
        api_response = client.get('/meeting-suggestions')
    
    print(f"✅ Result: API Status {api_response.status_code}")
    if api_response.status_code == 200:
        api_data = api_response.json()
        print(f"   Returned {len(api_data['suggestions'])} suggestions via API")
        print(f"   First API suggestion: {api_data['suggestions'][0]['date']} at {api_data['suggestions'][0]['time']}")
    
    # Step 10: Show final results
    print("\n🎯 STEP 10: Final Results Summary")
    print("-" * 40)
    print("print('=== FINAL WORKFLOW RESULTS ===')")
    print("=== FINAL WORKFLOW RESULTS ===")
    print(f"📅 Calendar events loaded: Phil={len(phil_events)}, Chris={len(chris_events)}")
    print(f"🤖 AI prompt created: {len(ai_prompt)} characters")
    print(f"🧠 AI suggestions generated: {len(suggestions['suggestions'])}")
    print(f"✅ Validation status: {'PASSED' if is_valid else 'FAILED'}")
    print(f"🌐 API server status: {'WORKING' if api_response.status_code == 200 else 'ERROR'}")
    print(f"💾 Files saved: prompt.txt, suggestions.json")
    
    print("\n" + "="*80)
    print("🎉 STEP-BY-STEP DEMO COMPLETE!")
    print("="*80)
    print("✅ All functions executed successfully")
    print("✅ FastAPI server returns meeting events")
    print("✅ Complete workflow demonstrated")
    print("="*80)


if __name__ == "__main__":
    demo_step_by_step()
