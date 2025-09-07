#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple meeting suggestion demo - just shows one meeting between two users
"""
import sys
import os
from datetime import datetime, timedelta

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from infrastructure.calendar_loader import load_calendar_data
from core.meeting_scheduler import create_ai_prompt
from adapters.gemini_client import get_deterministic_meeting_suggestions, parse_gemini_response


def main():
    """Show a single meeting suggestion between Alex and Sam"""
    
    print("🤝 Meeting Suggestion: Alex & Sam")
    print("=" * 40)
    
    # Load calendars
    alex_events = load_calendar_data('../data/alex_calendar_events_raw.json')
    sam_events = load_calendar_data('../data/sam_calendar_events_raw.json')
    
    print(f"Alex: {len(alex_events)} events")
    print(f"Sam: {len(sam_events)} events")
    
    # Create AI prompt
    start_date = datetime.now() + timedelta(days=1)
    end_date = start_date + timedelta(days=7)
    prompt = create_ai_prompt(alex_events, sam_events, 'Alex', 'Sam', start_date, end_date)
    
    # Get AI response
    try:
        ai_response = get_deterministic_meeting_suggestions(prompt, seed=42)
        if ai_response:
            suggestions = parse_gemini_response(ai_response, 'alex', 'sam')
            if suggestions and 'suggestions' in suggestions and suggestions['suggestions']:
                suggestion = suggestions['suggestions'][0]  # Just the first one
                
                print(f"\n📅 {suggestion.get('date', 'N/A')} at {suggestion.get('time', 'N/A')}")
                print(f"⏱️  Duration: {suggestion.get('duration', 'N/A')}")
                print(f"🎯 Type: {suggestion.get('meeting_type', 'N/A')}")
                
                if 'user_energies' in suggestion:
                    energies = suggestion['user_energies']
                    print(f"⚡ Alex energy: {energies.get('alex', 'N/A')}")
                    print(f"⚡ Sam energy: {energies.get('sam', 'N/A')}")
                
                if 'reasoning' in suggestion:
                    print(f"💭 {suggestion['reasoning']}")
            else:
                print("❌ No suggestions generated")
        else:
            print("⚠️  No AI response (API key not set)")
    except Exception as e:
        print(f"⚠️  Error: {e}")


if __name__ == "__main__":
    main()
