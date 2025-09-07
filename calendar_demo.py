#!/usr/bin/env python3
"""
Calendar Demo - Shows two calendars and finds free times
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
import argparse

def load_calendar_data(file_path: str) -> List[Dict[str, Any]]:
    """Load calendar events from JSON file"""
    with open(file_path, 'r') as f:
        return json.load(f)

def parse_event_time(event: Dict[str, Any]) -> tuple:
    """Parse event start and end times, handling both dateTime and date formats"""
    start = event.get('start', {})
    end = event.get('end', {})
    
    # Handle dateTime format
    if 'dateTime' in start:
        start_time = datetime.fromisoformat(start['dateTime'].replace('Z', '+00:00'))
    elif 'date' in start:
        start_time = datetime.fromisoformat(start['date'] + 'T00:00:00+00:00')
    else:
        return None, None
    
    if 'dateTime' in end:
        end_time = datetime.fromisoformat(end['dateTime'].replace('Z', '+00:00'))
    elif 'date' in end:
        end_time = datetime.fromisoformat(end['date'] + 'T00:00:00+00:00')
    else:
        return None, None
    
    return start_time, end_time

def format_event_summary(event: Dict[str, Any]) -> str:
    """Format event for display"""
    start_time, end_time = parse_event_time(event)
    if not start_time or not end_time:
        return f"  {event.get('summary', 'Unknown')} (Invalid time)"
    
    start_str = start_time.strftime('%Y-%m-%d %H:%M')
    end_str = end_time.strftime('%H:%M')
    return f"  {start_str} - {end_str}: {event.get('summary', 'Unknown')}"

def display_calendar(events: List[Dict[str, Any]], name: str) -> None:
    """Display calendar events in chronological order"""
    print(f"\n=== {name}'s Calendar ===")
    
    # Sort events by start time
    valid_events = []
    for event in events:
        start_time, end_time = parse_event_time(event)
        if start_time and end_time:
            valid_events.append((start_time, event))
    
    valid_events.sort(key=lambda x: x[0])
    
    for start_time, event in valid_events:
        print(format_event_summary(event))

def find_free_times(phil_events: List[Dict[str, Any]], chris_events: List[Dict[str, Any]], 
                   start_date: str, end_date: str, duration_hours: int = 1) -> List[Dict[str, Any]]:
    """Find times when both people are free"""
    
    # Parse date range
    start_dt = datetime.fromisoformat(start_date + 'T00:00:00+00:00')
    end_dt = datetime.fromisoformat(end_date + 'T23:59:59+00:00')
    
    # Get all busy times for both people
    all_busy_times = []
    
    for event in phil_events + chris_events:
        start_time, end_time = parse_event_time(event)
        if start_time and end_time:
            all_busy_times.append((start_time, end_time))
    
    # Sort busy times
    all_busy_times.sort(key=lambda x: x[0])
    
    # Find free slots
    free_times = []
    current_time = start_dt
    
    while current_time < end_dt:
        # Check if current time conflicts with any busy time
        conflicts = False
        for busy_start, busy_end in all_busy_times:
            if (current_time < busy_end and 
                current_time + timedelta(hours=duration_hours) > busy_start):
                conflicts = True
                # Move to end of this busy period
                current_time = busy_end
                break
        
        if not conflicts:
            free_end = current_time + timedelta(hours=duration_hours)
            if free_end <= end_dt:
                free_times.append({
                    'start': current_time,
                    'end': free_end,
                    'duration_hours': duration_hours
                })
            current_time += timedelta(hours=1)  # Check next hour
        else:
            current_time += timedelta(minutes=30)  # Check in 30 min intervals
    
    return free_times

def main():
    parser = argparse.ArgumentParser(description='Calendar Demo - Find free times')
    parser.add_argument('--start-date', default='2025-09-01', 
                       help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', default='2025-09-07', 
                       help='End date (YYYY-MM-DD)')
    parser.add_argument('--duration', type=int, default=1, 
                       help='Meeting duration in hours')
    parser.add_argument('--show-calendars', action='store_true', 
                       help='Show both calendars')
    
    args = parser.parse_args()
    
    print("🗓️  Calendar Demo - Finding Free Times")
    print("=" * 50)
    
    # Load calendar data
    phil_events = load_calendar_data('data/calendar_events_raw.json')
    chris_events = load_calendar_data('data/chris_calendar_events_raw.json')
    
    print(f"📅 Phil's calendar: {len(phil_events)} events")
    print(f"📅 Chris's calendar: {len(chris_events)} events")
    
    if args.show_calendars:
        display_calendar(phil_events, "Phil")
        display_calendar(chris_events, "Chris")
    
    # Find free times
    print(f"\n🔍 Looking for {args.duration}-hour free slots between {args.start_date} and {args.end_date}...")
    free_times = find_free_times(phil_events, chris_events, 
                                args.start_date, args.end_date, args.duration)
    
    if free_times:
        print(f"\n✅ Found {len(free_times)} free time slots:")
        for i, slot in enumerate(free_times, 1):
            start_str = slot['start'].strftime('%Y-%m-%d %H:%M UTC')
            end_str = slot['end'].strftime('%H:%M UTC')
            print(f"  {i}. {start_str} - {end_str} ({slot['duration_hours']}h)")
    else:
        print("\n❌ No free time slots found in the specified range")
    
    print(f"\n📊 Summary:")
    print(f"  - Phil has {len(phil_events)} events")
    print(f"  - Chris has {len(chris_events)} events") 
    print(f"  - Found {len(free_times)} free {args.duration}-hour slots")

if __name__ == '__main__':
    main()
