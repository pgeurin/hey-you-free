#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test real Google Calendar event creation for Philip
"""
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from src.adapters.google_calendar_client import (
    create_calendar_event,
    create_event_from_meeting_suggestion,
    load_google_credentials
)


def check_current_credentials():
    """Check current Google Calendar credentials"""
    print("🔍 Checking current Google Calendar credentials...")
    
    token_path = Path("token.json")
    if not token_path.exists():
        print("❌ No token.json found")
        return False
    
    with open(token_path, 'r') as f:
        token_data = json.load(f)
    
    scopes = token_data.get('scopes', [])
    print(f"📋 Current scopes: {scopes}")
    
    if 'https://www.googleapis.com/auth/calendar.events' in scopes:
        print("✅ Calendar events permission already granted")
        return True
    else:
        print("⚠️  Calendar events permission needed")
        print("   Current: calendar.readonly")
        print("   Needed: calendar.events")
        return False


def test_credentials():
    """Test if credentials work for calendar access"""
    print("\n🔧 Testing Google Calendar credentials...")
    
    try:
        creds = load_google_credentials()
        if creds:
            print("✅ Credentials loaded successfully")
            return True
        else:
            print("❌ Failed to load credentials")
            return False
    except Exception as e:
        print(f"❌ Error loading credentials: {e}")
        return False


def create_test_event():
    """Create a test event in Philip's calendar"""
    print("\n📅 Creating test event in Philip's calendar...")
    
    # Create a test event for tomorrow
    tomorrow = datetime.now() + timedelta(days=1)
    start_time = tomorrow.replace(hour=15, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(hours=1)
    
    # Format for API
    start_iso = start_time.isoformat() + 'Z'
    end_iso = end_time.isoformat() + 'Z'
    
    print(f"📝 Test event details:")
    print(f"  Summary: Test Meeting from AI Scheduler")
    print(f"  Start: {start_iso}")
    print(f"  End: {end_iso}")
    print(f"  Description: This is a test event created by the AI meeting scheduler")
    print(f"  Location: Test Location")
    print(f"  Attendees: philip.geurin@gmail.com")
    
    try:
        result = create_calendar_event(
            summary="Test Meeting from AI Scheduler",
            start_time=start_iso,
            end_time=end_iso,
            description="This is a test event created by the AI meeting scheduler",
            location="Test Location",
            attendees=["philip.geurin@gmail.com"]
        )
        
        if result:
            print("✅ Event created successfully!")
            print(f"📧 Event ID: {result.get('id', 'Unknown')}")
            print(f"🔗 Event link: {result.get('htmlLink', 'No link available')}")
            return True
        else:
            print("❌ Failed to create event")
            return False
            
    except Exception as e:
        print(f"❌ Error creating event: {e}")
        return False


def create_meeting_suggestion_event():
    """Create an event from a meeting suggestion"""
    print("\n🤖 Creating event from meeting suggestion...")
    
    # Sample meeting suggestion
    suggestion = {
        'date': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'),
        'time': '14:00',
        'duration': '1.5 hours',
        'meeting_type': 'Coffee Chat',
        'reasoning': 'Good afternoon slot for a casual meeting',
        'location': 'Starbucks Downtown'
    }
    
    print(f"📋 Meeting suggestion:")
    for key, value in suggestion.items():
        print(f"  {key}: {value}")
    
    try:
        result = create_event_from_meeting_suggestion(
            suggestion=suggestion,
            user1_email="philip.geurin@gmail.com",
            user2_email="colleague@example.com"
        )
        
        if result:
            print("✅ Meeting suggestion event created successfully!")
            print(f"📧 Event ID: {result.get('id', 'Unknown')}")
            return True
        else:
            print("❌ Failed to create meeting suggestion event")
            return False
            
    except Exception as e:
        print(f"❌ Error creating meeting suggestion event: {e}")
        return False


def main():
    """Run real calendar event creation test"""
    print("🎯 Real Google Calendar Event Creation Test")
    print("=" * 50)
    
    # Check credentials
    has_events_scope = check_current_credentials()
    
    # Test credentials
    creds_work = test_credentials()
    
    if not creds_work:
        print("\n❌ Cannot proceed - credentials not working")
        return
    
    if not has_events_scope:
        print("\n⚠️  WARNING: Current credentials only have readonly access")
        print("   To create events, you need to:")
        print("   1. Go to Google Cloud Console")
        print("   2. Update OAuth scopes to include calendar.events")
        print("   3. Re-authorize the application")
        print("\n   For now, we'll test with readonly access...")
    
    # Try to create events
    print("\n" + "=" * 50)
    print("🚀 Attempting to create real calendar events...")
    
    # Test 1: Basic event creation
    success1 = create_test_event()
    
    # Test 2: Meeting suggestion event
    success2 = create_meeting_suggestion_event()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"  Basic event creation: {'✅ Success' if success1 else '❌ Failed'}")
    print(f"  Meeting suggestion event: {'✅ Success' if success2 else '❌ Failed'}")
    
    if success1 or success2:
        print("\n🎉 SUCCESS! Events created in your Google Calendar!")
        print("   Check your Google Calendar app to see the events")
    else:
        print("\n⚠️  No events were created")
        if not has_events_scope:
            print("   This is likely due to readonly permissions")
            print("   Update OAuth scopes to include calendar.events")


if __name__ == "__main__":
    main()
