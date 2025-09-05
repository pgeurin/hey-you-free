#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Calendar API client adapter
Handles external API communication with configurable date windows
"""
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class DateWindow:
    """Represents a date range for calendar queries"""
    start_date: datetime
    end_date: datetime
    
    def to_iso_strings(self) -> Tuple[str, str]:
        """Convert to ISO format strings for API"""
        return (
            self.start_date.isoformat() + 'Z',
            self.end_date.isoformat() + 'Z'
        )


def create_date_window(days_back: int = 7, days_forward: int = 7) -> DateWindow:
    """Create a date window relative to today"""
    now = datetime.utcnow()
    start_date = now - timedelta(days=days_back)
    end_date = now + timedelta(days=days_forward)
    return DateWindow(start_date, end_date)


def create_custom_date_window(start_date: str, end_date: str) -> DateWindow:
    """Create a custom date window from string dates (YYYY-MM-DD)"""
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)
    return DateWindow(start, end)


def load_google_credentials() -> Optional[Any]:
    """Load Google OAuth credentials"""
    creds_path = Path(".cursor/credentials.json")
    if not creds_path.exists():
        print("ERROR: credentials.json not found in .cursor/ folder")
        return None
    
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        
        SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
        
        creds = None
        token_path = Path(".cursor/token.json")
        
        if token_path.exists():
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(creds_path), SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        return creds
        
    except ImportError:
        print("ERROR: Google auth packages not installed")
        print("Run: mamba install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        return None
    except Exception as e:
        print(f"ERROR loading credentials: {e}")
        return None


def fetch_calendar_events(
    date_window: DateWindow,
    calendar_id: str = 'primary',
    max_results: int = 100
) -> Optional[List[Dict[str, Any]]]:
    """Fetch calendar events for specified date window"""
    
    # Load credentials
    creds = load_google_credentials()
    if not creds:
        return None
    
    try:
        from googleapiclient.discovery import build
        
        # Build service
        service = build('calendar', 'v3', credentials=creds)
        
        # Convert date window to API format
        time_min, time_max = date_window.to_iso_strings()
        
        print(f"📅 Fetching events from {date_window.start_date.date()} to {date_window.end_date.date()}")
        
        # Get events
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        print(f"✅ Found {len(events)} events")
        
        return events
        
    except ImportError:
        print("ERROR: google-api-python-client not installed")
        return None
    except Exception as e:
        print(f"ERROR fetching events: {e}")
        return None


def save_events_to_file(events: List[Dict[str, Any]], filename: str) -> None:
    """Save events to JSON file"""
    with open(filename, 'w') as f:
        json.dump(events, f, indent=2, separators=(',', ': '))
    print(f"💾 Events saved to {filename}")


def print_events_summary(events: List[Dict[str, Any]], max_events: int = 10) -> None:
    """Print detailed summary of calendar events"""
    if not events:
        print("📅 No events found in this time period")
        return
    
    print(f"\n📊 Calendar Events Summary ({len(events)} total)")
    print("=" * 60)
    
    # Group events by date
    events_by_date = {}
    for event in events:
        try:
            start_time = datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
            date_key = start_time.strftime('%Y-%m-%d (%A)')
            
            if date_key not in events_by_date:
                events_by_date[date_key] = []
            
            events_by_date[date_key].append({
                'time': start_time.strftime('%H:%M'),
                'summary': event.get('summary', 'No title'),
                'location': event.get('location', ''),
                'description': event.get('description', '')[:100] + '...' if len(event.get('description', '')) > 100 else event.get('description', '')
            })
        except (KeyError, ValueError):
            continue
    
    # Print events by date
    for date, day_events in sorted(events_by_date.items()):
        print(f"\n🗓️  {date}")
        print("-" * 40)
        
        for event in day_events[:max_events]:
            print(f"  {event['time']} - {event['summary']}")
            if event['location']:
                print(f"    📍 {event['location']}")
            if event['description']:
                print(f"    📝 {event['description']}")
        
        if len(day_events) > max_events:
            print(f"    ... and {len(day_events) - max_events} more events")
    
    # Print statistics
    print(f"\n📈 Statistics:")
    print(f"  • Total events: {len(events)}")
    print(f"  • Days with events: {len(events_by_date)}")
    print(f"  • Average events per day: {len(events) / len(events_by_date):.1f}" if events_by_date else "  • No events")


def print_detailed_events(events: List[Dict[str, Any]], max_events: int = 5) -> None:
    """Print very detailed information about events"""
    if not events:
        print("📅 No events found in this time period")
        return
    
    print(f"\n🔍 Detailed Event Information (showing {min(max_events, len(events))} of {len(events)} events)")
    print("=" * 80)
    
    for i, event in enumerate(events[:max_events]):
        print(f"\n📅 Event #{i+1}")
        print("-" * 50)
        
        # Basic info
        summary = event.get('summary', 'No title')
        print(f"Title: {summary}")
        
        # Time info
        try:
            start_time = datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
            print(f"Date: {start_time.strftime('%Y-%m-%d (%A)')}")
            print(f"Time: {start_time.strftime('%H:%M')}")
        except (KeyError, ValueError):
            print("Time: All day event")
        
        # Location
        location = event.get('location', '')
        if location:
            print(f"Location: {location}")
        
        # Description
        description = event.get('description', '')
        if description:
            print(f"Description: {description[:200]}{'...' if len(description) > 200 else ''}")
        
        # Attendees
        attendees = event.get('attendees', [])
        if attendees:
            print(f"Attendees: {len(attendees)} people")
            for attendee in attendees[:3]:  # Show first 3
                email = attendee.get('email', 'Unknown')
                print(f"  • {email}")
            if len(attendees) > 3:
                print(f"  • ... and {len(attendees) - 3} more")
        
        # Status
        status = event.get('status', 'confirmed')
        print(f"Status: {status}")
    
    if len(events) > max_events:
        print(f"\n... and {len(events) - max_events} more events (use max_events parameter to see more)")


def get_calendar_events_with_window(
    days_back: int = 7,
    days_forward: int = 7,
    calendar_id: str = 'primary',
    save_to_file: Optional[str] = None
) -> Optional[List[Dict[str, Any]]]:
    """Main function to get calendar events with configurable window"""
    
    # Create date window
    date_window = create_date_window(days_back, days_forward)
    
    # Fetch events
    events = fetch_calendar_events(date_window, calendar_id)
    
    if events and save_to_file:
        save_events_to_file(events, save_to_file)
    
    return events


def get_calendar_events_custom_window(
    start_date: str,
    end_date: str,
    calendar_id: str = 'primary',
    save_to_file: Optional[str] = None
) -> Optional[List[Dict[str, Any]]]:
    """Get calendar events with custom date window"""
    
    try:
        # Create custom date window
        date_window = create_custom_date_window(start_date, end_date)
        
        # Fetch events
        events = fetch_calendar_events(date_window, calendar_id)
        
        if events and save_to_file:
            save_events_to_file(events, save_to_file)
        
        return events
        
    except ValueError as e:
        print(f"ERROR: Invalid date format - {e}")
        print("Use YYYY-MM-DD format for dates")
        return None


if __name__ == "__main__":
    # Example usage
    print("🔄 Testing calendar window selection...")
    
    # Test relative window
    events = get_calendar_events_with_window(
        days_back=7,
        days_forward=7,
        save_to_file="test_events.json"
    )
    
    if events:
        print(f"✅ Successfully fetched {len(events)} events")
    else:
        print("❌ Failed to fetch events")
