#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Show meeting suggestions between different user pairings
"""
import sys
import os
from datetime import datetime, timedelta

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from infrastructure.calendar_loader import load_calendar_data
from core.meeting_scheduler import create_ai_prompt, format_events_for_ai
from adapters.gemini_client import get_deterministic_meeting_suggestions, parse_gemini_response


def show_user_analysis():
    """Show detailed analysis of each user"""
    
    print("🤝 MEETING SUGGESTIONS: USER PERSONALITY ANALYSIS")
    print("=" * 60)
    
    # Load all calendars
    phil_events = load_calendar_data('data/calendar_events_raw.json')
    chris_events = load_calendar_data('data/chris_calendar_events_raw.json')
    alex_events = load_calendar_data('data/alex_calendar_events_raw.json')
    sam_events = load_calendar_data('data/sam_calendar_events_raw.json')
    
    users = [
        ("Phil", phil_events, "Original user - social and outgoing"),
        ("Chris", chris_events, "Original user - structured and professional"),
        ("Alex", alex_events, "New user - creative and flexible"),
        ("Sam", sam_events, "New user - structured and professional")
    ]
    
    for name, events, description in users:
        print(f"\n👤 {name.upper()} - {description}")
        print("-" * 40)
        
        # Analyze events
        creative_count = sum(1 for event in events if any(word in event.get('summary', '').lower() for word in ['creative', 'art', 'music', 'writing', 'gallery', 'jam', 'hiking']))
        work_count = sum(1 for event in events if any(word in event.get('summary', '').lower() for word in ['meeting', 'standup', 'sprint', 'client', 'review', 'presentation', 'interview']))
        social_count = sum(1 for event in events if any(word in event.get('summary', '').lower() for word in ['brunch', 'friends', 'lunch', 'team building']))
        
        # Time analysis
        morning_events = 0
        afternoon_events = 0
        evening_events = 0
        late_events = 0
        
        for event in events:
            if 'start' in event and 'dateTime' in event['start']:
                try:
                    dt = datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
                    if 6 <= dt.hour < 12:
                        morning_events += 1
                    elif 12 <= dt.hour < 18:
                        afternoon_events += 1
                    elif 18 <= dt.hour < 22:
                        evening_events += 1
                    elif dt.hour >= 22:
                        late_events += 1
                except:
                    pass
        
        print(f"   📊 Event Analysis:")
        print(f"      • Creative events: {creative_count}")
        print(f"      • Work events: {work_count}")
        print(f"      • Social events: {social_count}")
        print(f"      • Total events: {len(events)}")
        
        print(f"   🕐 Time Preferences:")
        print(f"      • Morning (6am-12pm): {morning_events}")
        print(f"      • Afternoon (12pm-6pm): {afternoon_events}")
        print(f"      • Evening (6pm-10pm): {evening_events}")
        print(f"      • Late night (10pm+): {late_events}")
        
        # Show sample events
        print(f"   📋 Sample Events:")
        for i, event in enumerate(events[:3]):
            summary = event.get('summary', 'No title')
            if 'start' in event and 'dateTime' in event['start']:
                try:
                    dt = datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
                    time_str = dt.strftime('%H:%M')
                except:
                    time_str = 'N/A'
            else:
                time_str = 'N/A'
            print(f"      {i+1}. {time_str} - {summary}")


def show_meeting_scenarios():
    """Show suggested meeting scenarios for different pairings"""
    
    print("\n\n🤝 SUGGESTED MEETING SCENARIOS")
    print("=" * 60)
    
    scenarios = [
        {
            "pairing": "Alex & Sam",
            "description": "Creative vs Structured",
            "suggestions": [
                "☕ Coffee shop meeting (neutral ground, flexible timing)",
                "🎨 Art gallery visit (creative + professional networking)",
                "🍽️ Business lunch (structured but social environment)",
                "🏢 Co-working space (professional with creative elements)"
            ],
            "best_times": "Morning (9-11am) or Afternoon (2-4pm)",
            "reasoning": "Balances Alex's flexibility with Sam's structure"
        },
        {
            "pairing": "Phil & Alex", 
            "description": "Social vs Creative",
            "suggestions": [
                "🎵 Music venue or concert (both enjoy social activities)",
                "🍺 Casual bar or pub (social + creative atmosphere)",
                "🏞️ Outdoor activity or park (flexible, social)",
                "🎪 Cultural event or festival (creative + social)"
            ],
            "best_times": "Evening (6-9pm) or Weekend",
            "reasoning": "Both are social and enjoy flexible, fun activities"
        },
        {
            "pairing": "Chris & Sam",
            "description": "Professional vs Professional", 
            "suggestions": [
                "☕ Morning coffee meeting (8-9am, professional)",
                "🍽️ Business lunch (12-1pm, structured)",
                "🏢 Office meeting room (2-4pm, work-focused)",
                "📊 Conference or workshop (professional development)"
            ],
            "best_times": "Morning (8-10am) or Afternoon (1-3pm)",
            "reasoning": "Both prefer structured, professional environments"
        },
        {
            "pairing": "Alex & Chris",
            "description": "Creative vs Professional",
            "suggestions": [
                "☕ Coffee shop (neutral, professional but casual)",
                "🎨 Art gallery opening (creative + networking)",
                "🍽️ Business lunch (professional but social)",
                "🏢 Creative co-working space (professional + creative)"
            ],
            "best_times": "Afternoon (1-4pm)",
            "reasoning": "Compromise between creative flexibility and professional structure"
        }
    ]
    
    for scenario in scenarios:
        print(f"\n🎭 {scenario['pairing']} - {scenario['description']}")
        print("-" * 40)
        print(f"   💡 Suggested Meeting Types:")
        for suggestion in scenario['suggestions']:
            print(f"      {suggestion}")
        print(f"   🕐 Best Times: {scenario['best_times']}")
        print(f"   💭 Reasoning: {scenario['reasoning']}")


def show_ai_prompt_example():
    """Show an example of how the AI prompt looks for different personalities"""
    
    print("\n\n🤖 AI PROMPT EXAMPLE")
    print("=" * 60)
    
    # Load calendars
    alex_events = load_calendar_data('data/alex_calendar_events_raw.json')
    sam_events = load_calendar_data('data/sam_calendar_events_raw.json')
    
    # Create prompt
    start_date = datetime.now() + timedelta(days=1)
    end_date = start_date + timedelta(days=7)
    
    prompt = create_ai_prompt(alex_events, sam_events, "Alex", "Sam", start_date, end_date)
    
    print("📝 AI Prompt Structure (first 500 characters):")
    print("-" * 40)
    print(prompt[:500] + "...")
    
    print(f"\n📊 Full prompt length: {len(prompt)} characters")
    
    # Show formatted events
    alex_formatted = format_events_for_ai(alex_events, "Alex")
    sam_formatted = format_events_for_ai(sam_events, "Sam")
    
    print(f"\n📅 Formatted Events:")
    print(f"   Alex: {len(alex_formatted)} characters")
    print(f"   Sam: {len(sam_formatted)} characters")
    
    print("\n🎯 Key Elements in AI Prompt:")
    print("   • User names and personalities")
    print("   • Calendar event details")
    print("   • Energy level analysis")
    print("   • Social preferences")
    print("   • Time range constraints")
    print("   • Meeting type suggestions")


if __name__ == "__main__":
    show_user_analysis()
    show_meeting_scenarios()
    show_ai_prompt_example()
    
    print("\n\n✅ MEETING SUGGESTIONS ANALYSIS COMPLETE")
    print("=" * 60)
    print("Key insights:")
    print("• AI considers personality types when suggesting meetings")
    print("• Creative users get flexible, social options")
    print("• Structured users get professional, time-specific options")
    print("• Mixed pairings get balanced compromise solutions")
    print("• Energy levels and preferences are analyzed")
    print("• Time patterns are considered for optimal scheduling")
