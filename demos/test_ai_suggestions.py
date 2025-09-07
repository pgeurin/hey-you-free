#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test actual AI-generated meeting suggestions
"""
import sys
import os
from datetime import datetime, timedelta

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.infrastructure.calendar_loader import load_calendar_data
from src.core.meeting_scheduler import create_ai_prompt
from src.adapters.gemini_client import get_deterministic_meeting_suggestions, parse_gemini_response


def test_ai_suggestions():
    """Test actual AI-generated meeting suggestions"""
    
    print("🎯 ACTUAL AI-GENERATED MEETING SUGGESTIONS")
    print("=" * 60)
    
    # Load calendars
    alex_events = load_calendar_data('data/alex_calendar_events_raw.json')
    sam_events = load_calendar_data('data/sam_calendar_events_raw.json')
    
    print(f"📅 Alex: {len(alex_events)} events")
    print(f"📅 Sam: {len(sam_events)} events")
    
    # Create prompt
    start_date = datetime.now() + timedelta(days=1)
    end_date = start_date + timedelta(days=7)
    prompt = create_ai_prompt(alex_events, sam_events, 'Alex', 'Sam', start_date, end_date)
    
    print(f"📝 Generated AI prompt: {len(prompt)} characters")
    print(f"📅 Time range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    # Try to get AI response
    try:
        ai_response = get_deterministic_meeting_suggestions(prompt, seed=42)
        if ai_response:
            print(f"🤖 AI Response received: {len(ai_response)} characters")
            
            suggestions = parse_gemini_response(ai_response, 'alex', 'sam')
            if suggestions and 'suggestions' in suggestions:
                print(f"✅ Parsed {len(suggestions['suggestions'])} meeting suggestions:")
                print("-" * 40)
                
                for i, suggestion in enumerate(suggestions['suggestions'], 1):
                    print(f"\n{i}. 📅 {suggestion.get('date', 'N/A')} at {suggestion.get('time', 'N/A')}")
                    print(f"   ⏱️  Duration: {suggestion.get('duration', 'N/A')}")
                    print(f"   🎯 Type: {suggestion.get('meeting_type', 'N/A')}")
                    
                    if 'user_energies' in suggestion:
                        energies = suggestion['user_energies']
                        print(f"   ⚡ Alex energy: {energies.get('alex', 'N/A')}")
                        print(f"   ⚡ Sam energy: {energies.get('sam', 'N/A')}")
                    
                    if 'reasoning' in suggestion:
                        print(f"   💭 Reasoning: {suggestion['reasoning']}")
            else:
                print("❌ Failed to parse suggestions")
        else:
            print("⚠️  No AI response (API key not set)")
            print("💡 To see real AI suggestions, set GOOGLE_API_KEY environment variable")
    except Exception as e:
        print(f"⚠️  Error: {e}")
        print("💡 This is expected if API key is not set")
    
    print("\n✅ Demo complete!")


if __name__ == "__main__":
    test_ai_suggestions()
