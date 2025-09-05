#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import Google Calendar events with configurable date windows
Uses the new flexible calendar client
"""
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.adapters.google_calendar_client import (
    get_calendar_events_with_window,
    get_calendar_events_custom_window,
    print_events_summary,
    print_detailed_events
)


def import_calendar_events_default():
    """Import calendar events with default window (last 2 weeks + next week)"""
    print("🔄 Importing calendar events with default window...")
    
    events = get_calendar_events_with_window(
        days_back=14,  # 2 weeks back
        days_forward=7,  # 1 week forward
        save_to_file="calendar_events_raw.json"
    )
    
    if events:
        print(f"✅ Successfully imported {len(events)} events")
        print_events_summary(events)
        return True
    else:
        print("❌ Failed to import events")
        return False


def import_calendar_events_custom(start_date: str, end_date: str):
    """Import calendar events with custom date window"""
    print(f"🔄 Importing calendar events from {start_date} to {end_date}...")
    
    events = get_calendar_events_custom_window(
        start_date=start_date,
        end_date=end_date,
        save_to_file="calendar_events_raw.json"
    )
    
    if events:
        print(f"✅ Successfully imported {len(events)} events")
        print_events_summary(events)
        return True
    else:
        print("❌ Failed to import events")
        return False


def import_calendar_events_week():
    """Import calendar events for current week only"""
    print("🔄 Importing calendar events for current week...")
    
    events = get_calendar_events_with_window(
        days_back=0,  # Today
        days_forward=7,  # Next week
        save_to_file="calendar_events_raw.json"
    )
    
    if events:
        print(f"✅ Successfully imported {len(events)} events")
        print_events_summary(events)
        return True
    else:
        print("❌ Failed to import events")
        return False


def import_calendar_events_detailed(days_back: int = 7, days_forward: int = 7):
    """Import calendar events with detailed output"""
    print("🔄 Importing calendar events with detailed output...")
    
    events = get_calendar_events_with_window(
        days_back=days_back,
        days_forward=days_forward,
        save_to_file="calendar_events_raw.json"
    )
    
    if events:
        print(f"✅ Successfully imported {len(events)} events")
        print_events_summary(events)
        print_detailed_events(events, max_events=3)
        return True
    else:
        print("❌ Failed to import events")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Import Google Calendar events")
    parser.add_argument("--window", choices=["default", "week", "custom", "detailed"], 
                       default="default", help="Date window type")
    parser.add_argument("--start", help="Start date (YYYY-MM-DD) for custom window")
    parser.add_argument("--end", help="End date (YYYY-MM-DD) for custom window")
    parser.add_argument("--days-back", type=int, default=7, help="Days back for detailed window")
    parser.add_argument("--days-forward", type=int, default=7, help="Days forward for detailed window")
    
    args = parser.parse_args()
    
    if args.window == "default":
        success = import_calendar_events_default()
    elif args.window == "week":
        success = import_calendar_events_week()
    elif args.window == "custom":
        if not args.start or not args.end:
            print("ERROR: --start and --end required for custom window")
            sys.exit(1)
        success = import_calendar_events_custom(args.start, args.end)
    elif args.window == "detailed":
        success = import_calendar_events_detailed(args.days_back, args.days_forward)
    
    sys.exit(0 if success else 1)
