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
    # Try multiple possible locations for credentials
    possible_paths = [
        Path(".cursor/credentials.json"),
        Path("credentials.json"),
        Path("token.json")  # Use existing token.json
    ]
    
    creds_path = None
    for path in possible_paths:
        if path.exists():
            creds_path = path
            break
    
    if not creds_path:
        print("ERROR: No credentials file found in .cursor/ or root directory")
        return None
    
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        
        SCOPES = [
            'https://www.googleapis.com/auth/calendar.readonly',
            'https://www.googleapis.com/auth/calendar.events'
        ]
        
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


def create_calendar_event(
    summary: str,
    start_time: str,
    end_time: str,
    description: Optional[str] = None,
    location: Optional[str] = None,
    attendees: Optional[List[str]] = None,
    calendar_id: str = 'primary'
) -> Optional[Dict[str, Any]]:
    """Create a calendar event"""
    
    # Load credentials
    creds = load_google_credentials()
    if not creds:
        print("ERROR: No Google credentials available")
        return None
    
    try:
        from googleapiclient.discovery import build
        
        # Build service
        service = build('calendar', 'v3', credentials=creds)
        
        # Create event object
        event = {
            'summary': summary,
            'start': {
                'dateTime': start_time,
                'timeZone': 'UTC'
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'UTC'
            }
        }
        
        # Add optional fields
        if description:
            event['description'] = description
        
        if location:
            event['location'] = location
        
        if attendees:
            event['attendees'] = [{'email': email} for email in attendees]
        
        # Create the event
        print(f"📅 Creating calendar event: {summary}")
        created_event = service.events().insert(
            calendarId=calendar_id,
            body=event
        ).execute()
        
        print(f"✅ Event created successfully: {created_event.get('id')}")
        return created_event
        
    except ImportError:
        print("ERROR: google-api-python-client not installed")
        return None
    except Exception as e:
        print(f"ERROR creating event: {e}")
        return None


def check_calendar_conflicts(
    start_time: str,
    end_time: str,
    calendar_id: str = 'primary'
) -> List[Dict[str, Any]]:
    """Check for calendar conflicts in the specified time range"""
    
    # Load credentials
    creds = load_google_credentials()
    if not creds:
        print("ERROR: No Google credentials available")
        return []
    
    try:
        from googleapiclient.discovery import build
        
        # Build service
        service = build('calendar', 'v3', credentials=creds)
        
        # Get events in the time range
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=start_time,
            timeMax=end_time,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        print(f"🔍 Found {len(events)} potential conflicts")
        
        return events
        
    except ImportError:
        print("ERROR: google-api-python-client not installed")
        return []
    except Exception as e:
        print(f"ERROR checking conflicts: {e}")
        return []


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


def create_event_from_meeting_suggestion(
    suggestion: Dict[str, Any],
    user1_email: str,
    user2_email: str,
    calendar_id: str = 'primary'
) -> Optional[Dict[str, Any]]:
    """Create a calendar event from a meeting suggestion"""
    
    try:
        # Parse date and time
        date_str = suggestion['date']  # YYYY-MM-DD
        time_str = suggestion['time']  # HH:MM
        
        # Create datetime objects
        start_datetime = datetime.fromisoformat(f"{date_str}T{time_str}:00")
        
        # Parse duration
        duration_str = suggestion.get('duration', '1 hour')
        duration_hours = parse_duration_to_hours(duration_str)
        end_datetime = start_datetime + timedelta(hours=duration_hours)
        
        # Format for API
        start_time_iso = start_datetime.isoformat() + 'Z'
        end_time_iso = end_datetime.isoformat() + 'Z'
        
        # Create event
        return create_calendar_event(
            summary=suggestion.get('meeting_type', 'Meeting'),
            start_time=start_time_iso,
            end_time=end_time_iso,
            description=suggestion.get('reasoning', ''),
            location=suggestion.get('location', ''),
            attendees=[user1_email, user2_email],
            calendar_id=calendar_id
        )
        
    except (KeyError, ValueError) as e:
        print(f"ERROR creating event from suggestion: {e}")
        return None


def parse_duration_to_hours(duration_str: str) -> float:
    """Parse duration string to hours (e.g., '1.5 hours' -> 1.5)"""
    import re
    
    # Extract number from duration string
    match = re.search(r'(\d+(?:\.\d+)?)', duration_str)
    if match:
        return float(match.group(1))
    
    # Default to 1 hour if parsing fails
    return 1.0


def create_events_for_both_users(
    suggestion: Dict[str, Any],
    user1_email: str,
    user2_email: str,
    user1_calendar_id: str = 'primary',
    user2_calendar_id: str = 'primary'
) -> Dict[str, Any]:
    """Create calendar events for both users from a meeting suggestion"""
    
    results = {
        'user1_event': None,
        'user2_event': None,
        'success': False,
        'errors': []
    }
    
    try:
        # Create event for user 1
        user1_event = create_event_from_meeting_suggestion(
            suggestion, user1_email, user2_email, user1_calendar_id
        )
        results['user1_event'] = user1_event
        
        # Create event for user 2
        user2_event = create_event_from_meeting_suggestion(
            suggestion, user1_email, user2_email, user2_calendar_id
        )
        results['user2_event'] = user2_event
        
        # Check if both events were created successfully
        if user1_event and user2_event:
            results['success'] = True
            print(f"✅ Created events for both users: {suggestion.get('meeting_type', 'Meeting')}")
        else:
            results['errors'].append("Failed to create events for one or both users")
            
    except Exception as e:
        results['errors'].append(f"Error creating events: {e}")
    
    return results


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
