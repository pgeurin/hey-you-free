#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example usage of visualize_calendar function with JSON dictionary
"""
import json
from visualize_calendar import visualize_calendar

def example_usage():
    """Show how to use visualize_calendar with JSON dictionary"""
    
    # Example 1: Load from file and pass as dictionary
    with open("calendar_events_raw.json", 'r') as f:
        phil_events = json.load(f)
    
    print("=== PHIL'S CALENDAR ===")
    visualize_calendar(phil_events, "PHIL")
    
    print("\n" + "="*60 + "\n")
    
    # Example 2: Load Chris's data
    with open("chris_calendar_events_raw.json", 'r') as f:
        chris_events = json.load(f)
    
    print("=== CHRIS'S CALENDAR ===")
    visualize_calendar(chris_events, "CHRIS")
    
    # Example 3: Create custom event data
    custom_events = [
        {
            "id": "custom_1",
            "summary": "Custom Meeting",
            "start": {
                "dateTime": "2025-09-02T10:00:00Z",
                "timeZone": "UTC"
            },
            "end": {
                "dateTime": "2025-09-02T11:00:00Z",
                "timeZone": "UTC"
            },
            "status": "confirmed"
        }
    ]
    
    print("\n=== CUSTOM CALENDAR ===")
    visualize_calendar(custom_events, "CUSTOM")

if __name__ == "__main__":
    example_usage()
