#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import Google Calendar events from last 2 weeks and next week into raw JSON
"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

def get_calendar_events():
    """Get calendar events from last 2 weeks and next week"""
    
    # Check if credentials exist
    creds_path = Path(".cursor/credentials.json")
    if not creds_path.exists():
        print("ERROR: credentials.json not found in .cursor/ folder")
        print("Please add your Google Calendar OAuth credentials first")
        return False
    
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        
        SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
        
        # Authenticate
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
            
            # Save the credentials for next run
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        # Build service
        service = build('calendar', 'v3', credentials=creds)
        
        # Calculate date range
        now = datetime.utcnow()
        two_weeks_ago = now - timedelta(weeks=2)
        next_week = now + timedelta(weeks=1)
        
        # Format for API
        time_min = two_weeks_ago.isoformat() + 'Z'
        time_max = next_week.isoformat() + 'Z'
        
        print(f"Fetching events from {two_weeks_ago.date()} to {next_week.date()}")
        
        # Get events
        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            maxResults=100,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        # Save to raw JSON
        output_path = Path("calendar_events_raw.json")
        with open(output_path, 'w') as f:
            json.dump(events, f, indent=2, separators=(',', ': '))
        
        print(f"SUCCESS: {len(events)} events saved to {output_path}")
        
        # Show summary
        print("\nEvent summary:")
        for event in events[:5]:  # Show first 5 events
            start = event['start'].get('dateTime', event['start'].get('date'))
            summary = event.get('summary', 'No title')
            print(f"  {start}: {summary}")
        
        if len(events) > 5:
            print(f"  ... and {len(events) - 5} more events")
        
        return True
        
    except ImportError:
        print("ERROR: Required packages not installed")
        print("Run: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    get_calendar_events()
