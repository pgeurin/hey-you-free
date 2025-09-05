#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Visualize one week of Phil's calendar in terminal
"""
import json
from datetime import datetime, timedelta
from pathlib import Path

def visualize_calendar(events_data, display_name="CALENDAR"):
    """Visualize calendar for one week from JSON dictionary"""
    
    # Validate input
    if not isinstance(events_data, list):
        print("ERROR: events_data must be a list of events")
        return False
    
    events = events_data
    
    # Choose a week (let's use the current week)
    from datetime import timezone
    now = datetime.now(timezone.utc)
    week_start = now - timedelta(days=now.weekday())  # Monday
    week_end = week_start + timedelta(days=6)  # Sunday
    
    print(f"📅 {display_name}'S CALENDAR - Week of {week_start.strftime('%B %d, %Y')}")
    print("=" * 60)
    
    # Filter events for this week
    week_events = []
    for event in events:
        try:
            start_time = datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
            if week_start <= start_time <= week_end:
                week_events.append(event)
        except (KeyError, ValueError):
            continue
    
    # Group events by day
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_events = {day: [] for day in days}
    
    for event in week_events:
        try:
            start_time = datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
            day_name = days[start_time.weekday()]
            daily_events[day_name].append(event)
        except (KeyError, ValueError):
            continue
    
    # Sort events within each day by time
    for day in daily_events:
        daily_events[day].sort(key=lambda x: x['start']['dateTime'])
    
    # Display calendar
    for day in days:
        print(f"\n📆 {day.upper()}")
        print("-" * 30)
        
        if not daily_events[day]:
            print("   No events")
            continue
        
        for event in daily_events[day]:
            try:
                start_time = datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
                time_str = start_time.strftime('%H:%M')
                summary = event.get('summary', 'No title')
                
                # Truncate long summaries
                if len(summary) > 40:
                    summary = summary[:37] + "..."
                
                print(f"   {time_str} | {summary}")
                
                # Show location if available
                if 'location' in event:
                    location = event['location']
                    if len(location) > 35:
                        location = location[:32] + "..."
                    print(f"        📍 {location}")
                
                # Show description if available and short
                if 'description' in event and len(event['description']) < 50:
                    desc = event['description']
                    print(f"        💬 {desc}")
                    
            except (KeyError, ValueError):
                continue
    
    print(f"\n📊 SUMMARY")
    print("-" * 20)
    total_events = sum(len(events) for events in daily_events.values())
    print(f"Total events this week: {total_events}")
    
    for day in days:
        count = len(daily_events[day])
        if count > 0:
            print(f"{day}: {count} events")
    
    return True

def load_calendar_data(calendar_name="phil"):
    """Load calendar data from JSON file and return as dictionary"""
    
    # Determine which calendar file to use
    if calendar_name.lower() == "chris":
        calendar_file = Path("chris_calendar_events_raw.json")
        display_name = "CHRIS"
    else:  # default to phil
        calendar_file = Path("calendar_events_raw.json")
        display_name = "PHIL"
    
    if not calendar_file.exists():
        print(f"ERROR: {calendar_file} not found")
        return None, None
    
    with open(calendar_file, 'r') as f:
        events_data = json.load(f)
    
    return events_data, display_name

if __name__ == "__main__":
    import sys
    
    # Check command line arguments
    if len(sys.argv) > 1:
        calendar_name = sys.argv[1]
    else:
        calendar_name = "phil"  # default
    
    print(f"Visualizing {calendar_name.upper()}'s calendar...")
    
    # Load data and visualize
    events_data, display_name = load_calendar_data(calendar_name)
    if events_data is not None:
        visualize_calendar(events_data, display_name)
