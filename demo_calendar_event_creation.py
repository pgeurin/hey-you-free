#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo: Calendar Event Creation from Meeting Suggestions
"""
from src.adapters.google_calendar_client import (
    create_event_from_meeting_suggestion,
    create_events_for_both_users,
    check_calendar_conflicts,
    parse_duration_to_hours
)


def demo_parse_duration():
    """Demo duration parsing functionality"""
    print("🕐 Testing duration parsing:")
    
    test_durations = [
        "1 hour",
        "1.5 hours", 
        "2 hours",
        "30 minutes",
        "invalid duration"
    ]
    
    for duration in test_durations:
        hours = parse_duration_to_hours(duration)
        print(f"  '{duration}' -> {hours} hours")


def demo_meeting_suggestion_structure():
    """Demo meeting suggestion data structure"""
    print("\n📋 Sample meeting suggestion structure:")
    
    sample_suggestion = {
        'date': '2024-01-15',
        'time': '14:00',
        'duration': '1.5 hours',
        'meeting_type': 'Coffee Chat',
        'reasoning': 'Good afternoon slot, both users typically free',
        'location': 'Downtown Coffee Shop',
        'confidence': 0.85
    }
    
    for key, value in sample_suggestion.items():
        print(f"  {key}: {value}")


def demo_event_creation_mock():
    """Demo event creation with mocked responses"""
    print("\n📅 Demo: Creating calendar events from meeting suggestions")
    
    # Sample meeting suggestion
    suggestion = {
        'date': '2024-01-15',
        'time': '14:00',
        'duration': '1.5 hours',
        'meeting_type': 'Coffee Chat',
        'reasoning': 'Good afternoon slot, both users typically free',
        'location': 'Downtown Coffee Shop'
    }
    
    print(f"Meeting suggestion: {suggestion['meeting_type']} on {suggestion['date']} at {suggestion['time']}")
    print(f"Duration: {suggestion['duration']}")
    print(f"Location: {suggestion['location']}")
    print(f"Reasoning: {suggestion['reasoning']}")
    
    # Show what the event would look like
    print("\n📝 Event details that would be created:")
    print(f"  Summary: {suggestion['meeting_type']}")
    print(f"  Start: {suggestion['date']}T{suggestion['time']}:00Z")
    print(f"  End: {suggestion['date']}T15:30:00Z")  # 1.5 hours later
    print(f"  Description: {suggestion['reasoning']}")
    print(f"  Location: {suggestion['location']}")
    print(f"  Attendees: user1@example.com, user2@example.com")


def demo_conflict_detection():
    """Demo conflict detection functionality"""
    print("\n🔍 Demo: Calendar conflict detection")
    
    # Sample time range to check
    start_time = '2024-01-15T14:00:00Z'
    end_time = '2024-01-15T15:30:00Z'
    
    print(f"Checking for conflicts between {start_time} and {end_time}")
    print("(This would check both users' calendars for existing events)")
    
    # In a real scenario, this would return actual conflicts
    print("✅ No conflicts detected - time slot is available")


def demo_both_users_event_creation():
    """Demo creating events for both users"""
    print("\n👥 Demo: Creating events for both users")
    
    suggestion = {
        'date': '2024-01-15',
        'time': '14:00',
        'duration': '1.5 hours',
        'meeting_type': 'Coffee Chat',
        'reasoning': 'Good afternoon slot, both users typically free',
        'location': 'Downtown Coffee Shop'
    }
    
    print("Creating events for:")
    print("  User 1: phil@example.com")
    print("  User 2: chris@example.com")
    
    # In a real scenario, this would create actual calendar events
    print("✅ Events created successfully for both users")
    print("✅ Both users will receive calendar invitations")


def main():
    """Run all demos"""
    print("🎯 Calendar Event Creation Demo")
    print("=" * 50)
    
    demo_parse_duration()
    demo_meeting_suggestion_structure()
    demo_event_creation_mock()
    demo_conflict_detection()
    demo_both_users_event_creation()
    
    print("\n" + "=" * 50)
    print("✅ Demo completed successfully!")
    print("\nNext steps:")
    print("1. Update API endpoints to handle event creation")
    print("2. Update web interface with event creation buttons")
    print("3. Add conflict detection to the UI")
    print("4. Test with real Google Calendar credentials")


if __name__ == "__main__":
    main()
