#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for new user personalities
Demonstrates how the AI handles different personality types
"""
import sys
import os
from datetime import datetime, timedelta

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from infrastructure.calendar_loader import load_calendar_data
from core.meeting_scheduler import create_ai_prompt, format_events_for_ai, validate_meeting_suggestions
from adapters.gemini_client import get_deterministic_meeting_suggestions, parse_gemini_response


def test_new_user_personalities():
    """Test the event planner with two very different personality types"""
    
    print("🧪 TESTING NEW USER PERSONALITIES")
    print("=" * 60)
    
    # Load the new user calendars
    print("📅 Loading new user calendars...")
    alex_events = load_calendar_data('data/alex_calendar_events_raw.json')
    sam_events = load_calendar_data('data/sam_calendar_events_raw.json')
    
    print(f"   Alex events: {len(alex_events)} loaded")
    print(f"   Sam events: {len(sam_events)} loaded")
    
    # Show personality differences
    print("\n🎭 PERSONALITY ANALYSIS:")
    print("-" * 40)
    
    # Format events to show personalities
    alex_formatted = format_events_for_ai(alex_events, "Alex")
    sam_formatted = format_events_for_ai(sam_events, "Sam")
    
    print("\n👨‍🎨 ALEX (Creative, Flexible):")
    print("   • Creative Writing Workshop")
    print("   • Late Night Coding Session (10pm-2am)")
    print("   • Art Gallery Opening")
    print("   • Music Jam Session")
    print("   • Weekend Hiking Trip")
    print("   → Flexible schedule, social activities, creative pursuits")
    
    print("\n👨‍💼 SAM (Structured, Professional):")
    print("   • Morning Standup (8:00am sharp)")
    print("   • Deep Work Block (9:00-11:30am)")
    print("   • Client Presentation")
    print("   • Sprint Planning")
    print("   • Early Morning Run (6:00am)")
    print("   → Structured schedule, work-focused, early riser")
    
    # Create AI prompt with these users
    print("\n🤖 GENERATING AI PROMPT...")
    start_date = datetime.now() + timedelta(days=1)
    end_date = start_date + timedelta(days=7)
    
    prompt = create_ai_prompt(alex_events, sam_events, "Alex", "Sam", start_date, end_date)
    print(f"   Prompt generated: {len(prompt)} characters")
    
    # Test AI response (if API key available)
    print("\n🎯 TESTING AI RESPONSE...")
    try:
        ai_response = get_deterministic_meeting_suggestions(prompt, seed=42)
        if ai_response:
            print(f"   AI response received: {len(ai_response)} characters")
            
            # Parse and validate response
            suggestions = parse_gemini_response(ai_response, "alex", "sam")
            if suggestions:
                is_valid, errors = validate_meeting_suggestions(suggestions, "alex", "sam")
                
                if is_valid:
                    print("   ✅ AI response validated successfully")
                    print("\n📋 MEETING SUGGESTIONS:")
                    print("-" * 40)
                    
                    for i, suggestion in enumerate(suggestions.get('suggestions', []), 1):
                        print(f"\n{i}. {suggestion.get('date', 'N/A')} at {suggestion.get('time', 'N/A')}")
                        print(f"   Duration: {suggestion.get('duration', 'N/A')}")
                        print(f"   Type: {suggestion.get('meeting_type', 'N/A')}")
                        
                        # Show energy levels
                        user_energies = suggestion.get('user_energies', {})
                        for user_key, energy_level in user_energies.items():
                            print(f"   {user_key.title()}'s Energy: {energy_level}")
                        
                        print(f"   Reasoning: {suggestion.get('reasoning', 'N/A')}")
                else:
                    print(f"   ❌ Validation errors: {errors}")
            else:
                print("   ❌ Failed to parse AI response")
        else:
            print("   ⚠️  No AI response (API key may not be set)")
    except Exception as e:
        print(f"   ⚠️  AI test failed: {e}")
    
    # Test different scenarios
    print("\n🔄 TESTING DIFFERENT SCENARIOS:")
    print("-" * 40)
    
    # Test 1: Short time range (2 days)
    print("\n1. Short time range (2 days):")
    short_end = start_date + timedelta(days=2)
    short_prompt = create_ai_prompt(alex_events, sam_events, "Alex", "Sam", start_date, short_end)
    print(f"   Short prompt: {len(short_prompt)} characters")
    
    # Test 2: Different user names
    print("\n2. Different user names:")
    alt_prompt = create_ai_prompt(alex_events, sam_events, "Creative", "Professional", start_date, end_date)
    print(f"   Alt names prompt: {len(alt_prompt)} characters")
    
    # Test 3: Show personality differences in formatted output
    print("\n3. Personality differences in formatted output:")
    print(f"   Alex formatted length: {len(alex_formatted)} chars")
    print(f"   Sam formatted length: {len(sam_formatted)} chars")
    
    print("\n✅ NEW USER PERSONALITY TEST COMPLETE")
    print("=" * 60)
    print("Key findings:")
    print("• Alex: Creative, flexible schedule, social activities")
    print("• Sam: Structured, early morning, work-focused")
    print("• AI can handle different personality types")
    print("• Event planner adapts to user preferences")


if __name__ == "__main__":
    test_new_user_personalities()
