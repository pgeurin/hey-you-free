#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate fictional calendar events for Chris
Same timeframe as real calendar: last 2 weeks and next week
"""
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

def generate_chris_calendar():
    """Generate fictional calendar events for Chris"""
    
    # Event templates for different types
    work_events = [
        "Team standup meeting",
        "Project planning session", 
        "Client presentation",
        "Code review",
        "Sprint retrospective",
        "One-on-one with manager",
        "Product demo",
        "Technical architecture review",
        "Bug triage meeting",
        "Design system workshop"
    ]
    
    personal_events = [
        "Gym workout",
        "Coffee with Sarah",
        "Grocery shopping",
        "Doctor appointment",
        "Dentist checkup",
        "Haircut appointment",
        "Movie night",
        "Dinner with friends",
        "Weekend hiking trip",
        "Book club meeting",
        "Cooking class",
        "Art gallery visit",
        "Concert tickets",
        "Birthday party",
        "Date night"
    ]
    
    recurring_events = [
        "Morning jog",
        "Meditation session",
        "Weekly team sync",
        "Lunch break",
        "Evening walk",
        "Weekend brunch"
    ]
    
    # Calculate date range (same as real calendar)
    now = datetime.utcnow()
    two_weeks_ago = now - timedelta(weeks=2)
    next_week = now + timedelta(weeks=1)
    
    events = []
    event_id = 1
    
    # Generate events for each day in the range
    current_date = two_weeks_ago
    while current_date <= next_week:
        date_str = current_date.strftime('%Y-%m-%d')
        
        # Skip some days randomly (not every day has events)
        if random.random() < 0.3:  # 30% chance of no events
            current_date += timedelta(days=1)
            continue
            
        # Generate 1-4 events per day
        num_events = random.randint(1, 4)
        
        for i in range(num_events):
            # Choose event type
            event_type = random.choices(
                ['work', 'personal', 'recurring'], 
                weights=[0.4, 0.4, 0.2]
            )[0]
            
            if event_type == 'work':
                summary = random.choice(work_events)
                start_hour = random.randint(9, 17)
            elif event_type == 'personal':
                summary = random.choice(personal_events)
                start_hour = random.randint(8, 20)
            else:  # recurring
                summary = random.choice(recurring_events)
                start_hour = random.randint(6, 22)
            
            # Generate start time
            start_minute = random.choice([0, 15, 30, 45])
            start_time = current_date.replace(
                hour=start_hour, 
                minute=start_minute, 
                second=0, 
                microsecond=0
            )
            
            # Generate duration (15 min to 3 hours)
            duration_minutes = random.choice([15, 30, 45, 60, 90, 120, 180])
            end_time = start_time + timedelta(minutes=duration_minutes)
            
            # Create event object
            event = {
                "id": f"chris_event_{event_id:03d}",
                "summary": summary,
                "start": {
                    "dateTime": start_time.isoformat() + "Z",
                    "timeZone": "UTC"
                },
                "end": {
                    "dateTime": end_time.isoformat() + "Z", 
                    "timeZone": "UTC"
                },
                "status": "confirmed",
                "created": start_time.isoformat() + "Z",
                "updated": start_time.isoformat() + "Z",
                "creator": {
                    "email": "chris@example.com",
                    "displayName": "Chris"
                },
                "organizer": {
                    "email": "chris@example.com",
                    "displayName": "Chris"
                }
            }
            
            # Add some optional fields randomly
            if random.random() < 0.3:  # 30% chance
                event["description"] = f"Details for {summary.lower()}"
            
            if random.random() < 0.2:  # 20% chance
                event["location"] = random.choice([
                    "Conference Room A",
                    "Coffee Shop Downtown", 
                    "Gym",
                    "Home",
                    "Restaurant",
                    "Park"
                ])
            
            events.append(event)
            event_id += 1
        
        current_date += timedelta(days=1)
    
    # Sort events by start time
    events.sort(key=lambda x: x['start']['dateTime'])
    
    # Save to JSON file
    output_path = Path("chris_calendar_events_raw.json")
    with open(output_path, 'w') as f:
        json.dump(events, f, indent=2, separators=(',', ': '))
    
    print(f"SUCCESS: Generated {len(events)} fictional events for Chris")
    print(f"Date range: {two_weeks_ago.date()} to {next_week.date()}")
    print(f"Saved to: {output_path}")
    
    # Show sample events
    print("\nSample events:")
    for event in events[:5]:
        start_time = event['start']['dateTime'][:16].replace('T', ' ')
        summary = event['summary']
        print(f"  {start_time}: {summary}")
    
    if len(events) > 5:
        print(f"  ... and {len(events) - 5} more events")
    
    return True

if __name__ == "__main__":
    generate_chris_calendar()
