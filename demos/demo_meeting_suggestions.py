#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo script showing meeting suggestions between different user pairings
Demonstrates how AI adapts to different personality combinations
"""
import sys
import os
from datetime import datetime, timedelta

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from infrastructure.calendar_loader import load_calendar_data
from core.meeting_scheduler import create_ai_prompt, validate_meeting_suggestions
from adapters.gemini_client import get_deterministic_meeting_suggestions, parse_gemini_response


def show_meeting_suggestions(user1_name, user2_name, user1_events, user2_events, seed=42):
    """Show meeting suggestions for a user pairing"""
    
    print(f"\n🤝 MEETING SUGGESTIONS: {user1_name.upper()} & {user2_name.upper()}")
    print("=" * 60)
    
    # Create AI prompt
    start_date = datetime.now() + timedelta(days=1)
    end_date = start_date + timedelta(days=7)
    
    prompt = create_ai_prompt(user1_events, user2_events, user1_name, user2_name, start_date, end_date)
    
    try:
        # Get AI response
        ai_response = get_deterministic_meeting_suggestions(prompt, seed=seed)
        if ai_response:
            suggestions = parse_gemini_response(ai_response, user1_name.lower(), user2_name.lower())
            
            if suggestions and "suggestions" in suggestions:
                is_valid, errors = validate_meeting_suggestions(suggestions, user1_name.lower(), user2_name.lower())
                
                if is_valid:
                    print(f"✅ Generated {len(suggestions['suggestions'])} meeting suggestions:")
                    print("-" * 40)
                    
                    for i, suggestion in enumerate(suggestions['suggestions'], 1):
                        print(f"\n{i}. 📅 {suggestion.get('date', 'N/A')} at {suggestion.get('time', 'N/A')}")
                        print(f"   ⏱️  Duration: {suggestion.get('duration', 'N/A')}")
                        print(f"   🎯 Type: {suggestion.get('meeting_type', 'N/A')}")
                        
                        # Show energy levels
                        user_energies = suggestion.get('user_energies', {})
                        if user_energies:
                            print(f"   ⚡ Energy Levels:")
                            for user_key, energy_level in user_energies.items():
                                print(f"      {user_key.title()}: {energy_level}")
                        
                        # Show reasoning
                        reasoning = suggestion.get('reasoning', 'N/A')
                        if reasoning:
                            print(f"   💭 Reasoning: {reasoning}")
                        
                        # Show optional fields
                        if 'location' in suggestion and suggestion['location']:
                            print(f"   📍 Location: {suggestion['location']}")
                        
                        if 'confidence' in suggestion and suggestion['confidence']:
                            print(f"   🎯 Confidence: {suggestion['confidence']}")
                else:
                    print(f"❌ Validation errors: {errors}")
            else:
                print("❌ Failed to parse suggestions")
        else:
            print("⚠️  No AI response (API key may not be set)")
            print("💡 To see real suggestions, set GOOGLE_API_KEY environment variable")
            
            # Show mock suggestions based on personalities
            show_mock_suggestions(user1_name, user2_name, user1_events, user2_events)
            
    except Exception as e:
        print(f"⚠️  Error: {e}")
        show_mock_suggestions(user1_name, user2_name, user1_events, user2_events)


def show_mock_suggestions(user1_name, user2_name, user1_events, user2_events):
    """Show mock suggestions based on personality analysis"""
    
    print("\n🎭 MOCK SUGGESTIONS (based on personality analysis):")
    print("-" * 40)
    
    # Analyze personalities
    user1_type = analyze_personality(user1_events, user1_name)
    user2_type = analyze_personality(user2_events, user2_name)
    
    print(f"   {user1_name}: {user1_type}")
    print(f"   {user2_name}: {user2_type}")
    
    # Generate mock suggestions based on personality combination
    if "creative" in user1_type.lower() and "structured" in user2_type.lower():
        print("\n   💡 Suggested meeting types:")
        print("   1. Coffee shop meeting (neutral ground)")
        print("   2. Art gallery visit (creative + professional)")
        print("   3. Business lunch (structured but social)")
        
    elif "structured" in user1_type.lower() and "structured" in user2_type.lower():
        print("\n   💡 Suggested meeting types:")
        print("   1. Morning coffee meeting (8:00-9:00am)")
        print("   2. Business lunch (12:00-1:00pm)")
        print("   3. Afternoon work session (2:00-4:00pm)")
        
    elif "creative" in user1_type.lower() and "creative" in user2_type.lower():
        print("\n   💡 Suggested meeting types:")
        print("   1. Art gallery opening (evening)")
        print("   2. Coffee shop brainstorming (flexible time)")
        print("   3. Outdoor activity (weekend)")
    
    print(f"\n   🕐 Best times for {user1_name}: {get_best_times(user1_events)}")
    print(f"   🕐 Best times for {user2_name}: {get_best_times(user2_events)}")


def analyze_personality(events, name):
    """Analyze personality based on events"""
    
    creative_keywords = ['creative', 'art', 'music', 'writing', 'gallery', 'jam', 'hiking']
    work_keywords = ['meeting', 'standup', 'sprint', 'client', 'review', 'presentation', 'interview']
    social_keywords = ['brunch', 'friends', 'lunch', 'team building']
    
    creative_count = 0
    work_count = 0
    social_count = 0
    late_events = 0
    early_events = 0
    
    for event in events:
        summary = event.get('summary', '').lower()
        
        if any(keyword in summary for keyword in creative_keywords):
            creative_count += 1
        if any(keyword in summary for keyword in work_keywords):
            work_count += 1
        if any(keyword in summary for keyword in social_keywords):
            social_count += 1
        
        # Check timing
        if 'start' in event and 'dateTime' in event['start']:
            try:
                dt = datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
                if dt.hour >= 20:
                    late_events += 1
                elif dt.hour < 10:
                    early_events += 1
            except:
                pass
    
    # Determine personality type
    if creative_count > work_count and creative_count > social_count:
        return "Creative & Flexible"
    elif work_count > creative_count and work_count > social_count:
        return "Structured & Professional"
    elif social_count > creative_count and social_count > work_count:
        return "Social & Outgoing"
    else:
        return "Balanced & Adaptable"


def get_best_times(events):
    """Get best meeting times based on schedule analysis"""
    
    morning_events = 0
    afternoon_events = 0
    evening_events = 0
    
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
            except:
                pass
    
    if morning_events > afternoon_events and morning_events > evening_events:
        return "Morning (8:00-11:00am)"
    elif afternoon_events > morning_events and afternoon_events > evening_events:
        return "Afternoon (1:00-5:00pm)"
    elif evening_events > morning_events and evening_events > afternoon_events:
        return "Evening (6:00-9:00pm)"
    else:
        return "Flexible (any time)"


def demo_meeting_suggestions():
    """Demo meeting suggestions for different user pairings"""
    
    print("🤝 MEETING SUGGESTIONS DEMO")
    print("=" * 60)
    print("Showing AI-generated meeting suggestions for different user pairings")
    
    # Load all user calendars
    print("\n📅 Loading user calendars...")
    phil_events = load_calendar_data('data/calendar_events_raw.json')
    chris_events = load_calendar_data('data/chris_calendar_events_raw.json')
    alex_events = load_calendar_data('data/alex_calendar_events_raw.json')
    sam_events = load_calendar_data('data/sam_calendar_events_raw.json')
    
    print(f"   Phil: {len(phil_events)} events")
    print(f"   Chris: {len(chris_events)} events")
    print(f"   Alex: {len(alex_events)} events")
    print(f"   Sam: {len(sam_events)} events")
    
    # Test different pairings
    pairings = [
        ("Alex", "Sam", alex_events, sam_events, "Creative vs Structured"),
        ("Phil", "Alex", phil_events, alex_events, "Original vs Creative"),
        ("Chris", "Sam", chris_events, sam_events, "Original vs Structured"),
        ("Alex", "Chris", alex_events, chris_events, "Creative vs Original"),
        ("Sam", "Phil", sam_events, phil_events, "Structured vs Original")
    ]
    
    for user1_name, user2_name, user1_events, user2_events, description in pairings:
        print(f"\n🎭 PAIRING: {description}")
        show_meeting_suggestions(user1_name, user2_name, user1_events, user2_events)
    
    print("\n✅ MEETING SUGGESTIONS DEMO COMPLETE")
    print("=" * 60)
    print("Key insights:")
    print("• AI adapts suggestions based on personality types")
    print("• Creative users get flexible, social meeting options")
    print("• Structured users get professional, time-specific options")
    print("• Mixed pairings get balanced, compromise solutions")
    print("• Energy levels and preferences are considered")


if __name__ == "__main__":
    demo_meeting_suggestions()
