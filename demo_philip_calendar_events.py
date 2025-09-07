#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo: Calendar Event Creation for Philip Geurin
Personalized demo using philip.geurin@gmail.com
"""
from src.adapters.google_calendar_client import (
    create_event_from_meeting_suggestion,
    create_events_for_both_users,
    check_calendar_conflicts,
    parse_duration_to_hours
)
from datetime import datetime, timedelta


def demo_philip_meeting_creation():
    """Demo creating a meeting for Philip with a colleague"""
    print("👤 Calendar Event Creation Demo for Philip Geurin")
    print("=" * 60)
    
    # Philip's email
    philip_email = "philip.geurin@gmail.com"
    
    # Sample colleague email
    colleague_email = "colleague@example.com"
    
    print(f"📧 Philip's email: {philip_email}")
    print(f"📧 Colleague's email: {colleague_email}")
    
    # Sample meeting suggestion
    meeting_suggestion = {
        'date': '2024-01-20',
        'time': '15:00',
        'duration': '1 hour',
        'meeting_type': 'Coffee Chat',
        'reasoning': 'Good afternoon slot, both typically free for casual meetings',
        'location': 'Starbucks Downtown',
        'confidence': 0.9
    }
    
    print(f"\n📅 Meeting Suggestion:")
    print(f"  Type: {meeting_suggestion['meeting_type']}")
    print(f"  Date: {meeting_suggestion['date']}")
    print(f"  Time: {meeting_suggestion['time']}")
    print(f"  Duration: {meeting_suggestion['duration']}")
    print(f"  Location: {meeting_suggestion['location']}")
    print(f"  Reasoning: {meeting_suggestion['reasoning']}")
    
    return meeting_suggestion, philip_email, colleague_email


def demo_philip_event_creation():
    """Demo creating calendar events for Philip"""
    meeting_suggestion, philip_email, colleague_email = demo_philip_meeting_creation()
    
    print(f"\n🔄 Creating calendar events...")
    print(f"  For: {philip_email}")
    print(f"  With: {colleague_email}")
    
    # Show what the event would look like
    print(f"\n📝 Event details that would be created:")
    print(f"  Summary: {meeting_suggestion['meeting_type']}")
    print(f"  Start: {meeting_suggestion['date']}T{meeting_suggestion['time']}:00Z")
    
    # Calculate end time
    duration_hours = parse_duration_to_hours(meeting_suggestion['duration'])
    start_time = datetime.fromisoformat(f"{meeting_suggestion['date']}T{meeting_suggestion['time']}:00")
    end_time = start_time + timedelta(hours=duration_hours)
    
    print(f"  End: {end_time.strftime('%Y-%m-%dT%H:%M:%SZ')}")
    print(f"  Description: {meeting_suggestion['reasoning']}")
    print(f"  Location: {meeting_suggestion['location']}")
    print(f"  Attendees: {philip_email}, {colleague_email}")
    
    return meeting_suggestion, philip_email, colleague_email


def demo_philip_conflict_check():
    """Demo conflict checking for Philip's calendar"""
    meeting_suggestion, philip_email, colleague_email = demo_philip_event_creation()
    
    print(f"\n🔍 Checking for conflicts in Philip's calendar...")
    
    # Check time range
    start_time = f"{meeting_suggestion['date']}T{meeting_suggestion['time']}:00Z"
    duration_hours = parse_duration_to_hours(meeting_suggestion['duration'])
    end_time = (datetime.fromisoformat(f"{meeting_suggestion['date']}T{meeting_suggestion['time']}:00") + 
                timedelta(hours=duration_hours)).strftime('%Y-%m-%dT%H:%M:%SZ')
    
    print(f"  Time range: {start_time} to {end_time}")
    print(f"  Checking Philip's calendar for existing events...")
    
    # In a real scenario, this would check actual calendar
    print(f"  ✅ No conflicts detected - time slot is available for Philip")
    
    return meeting_suggestion, philip_email, colleague_email


def demo_philip_dual_calendar_creation():
    """Demo creating events for both Philip and colleague"""
    meeting_suggestion, philip_email, colleague_email = demo_philip_conflict_check()
    
    print(f"\n👥 Creating events for both calendars...")
    print(f"  Philip's calendar: {philip_email}")
    print(f"  Colleague's calendar: {colleague_email}")
    
    # Show the process
    print(f"\n🔄 Process:")
    print(f"  1. Create event in Philip's calendar")
    print(f"  2. Create event in colleague's calendar")
    print(f"  3. Both receive calendar invitations")
    print(f"  4. Both can accept/decline the meeting")
    
    print(f"\n✅ Events created successfully!")
    print(f"  📧 Philip will receive a calendar invitation")
    print(f"  📧 Colleague will receive a calendar invitation")
    print(f"  📅 Meeting: {meeting_suggestion['meeting_type']} on {meeting_suggestion['date']} at {meeting_suggestion['time']}")


def demo_philip_real_implementation():
    """Demo how this would work with real Google Calendar API"""
    print(f"\n🔧 Real Implementation for Philip:")
    print(f"  To use with real Google Calendar:")
    print(f"  1. Set up Google OAuth credentials")
    print(f"  2. Grant calendar.events permission")
    print(f"  3. Use philip.geurin@gmail.com as primary calendar")
    print(f"  4. Create events directly in Google Calendar")
    
    print(f"\n📋 Next steps for Philip:")
    print(f"  1. Update API endpoints to handle event creation")
    print(f"  2. Add 'Create Event' buttons to web interface")
    print(f"  3. Test with real Google Calendar credentials")
    print(f"  4. Deploy to production")


def main():
    """Run Philip's personalized demo"""
    demo_philip_dual_calendar_creation()
    demo_philip_real_implementation()
    
    print(f"\n" + "=" * 60)
    print(f"✅ Philip's Calendar Event Creation Demo Complete!")
    print(f"📧 Ready to create events for: philip.geurin@gmail.com")


if __name__ == "__main__":
    main()
