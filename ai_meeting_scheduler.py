#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI-powered meeting scheduler using Gemini
Analyzes both calendars and suggests optimal meeting times
"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

def load_calendar_data(filename):
    """Load calendar data from JSON file"""
    with open(filename, 'r') as f:
        return json.load(f)

def format_events_for_ai(events, name):
    """Format calendar events for AI analysis"""
    formatted_events = []
    
    for event in events:
        try:
            start_time = datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
            summary = event.get('summary', 'No title')
            location = event.get('location', '')
            description = event.get('description', '')
            
            formatted_event = {
                'date': start_time.strftime('%Y-%m-%d'),
                'time': start_time.strftime('%H:%M'),
                'day_of_week': start_time.strftime('%A'),
                'summary': summary,
                'location': location,
                'description': description
            }
            
            formatted_events.append(formatted_event)
            
        except (KeyError, ValueError):
            continue
    
    # Sort by date and time
    formatted_events.sort(key=lambda x: (x['date'], x['time']))
    
    # Format as readable text
    result = f"Total events: {len(formatted_events)}\n\n"
    for event in formatted_events:
        result += f"{event['date']} ({event['day_of_week']}) {event['time']} - {event['summary']}"
        if event['location']:
            result += f" @ {event['location']}"
        if event['description']:
            result += f" | {event['description']}"
        result += "\n"
    
    return result

def create_ai_prompt(phil_events, chris_events):
    """Create optimized AI prompt using modern prompt engineering techniques"""
    
    # Convert events to simple format for AI analysis
    phil_data = format_events_for_ai(phil_events, "Phil")
    chris_data = format_events_for_ai(chris_events, "Chris")
    
    prompt = f"""# MEETING SCHEDULER AI ASSISTANT

## ROLE & CONTEXT
You are an expert meeting scheduler with deep understanding of human psychology, productivity patterns, and social dynamics. Your task is to analyze two people's raw calendar data and suggest 3 optimal meeting times that both would find appealing and convenient.

## RAW CALENDAR DATA

### PHIL'S CALENDAR EVENTS:
{phil_data}

### CHRIS'S CALENDAR EVENTS:
{chris_data}

## ANALYSIS INSTRUCTIONS
Before suggesting meeting times, analyze the calendar data to identify:
1. **Busy vs. free periods** for each person
2. **Preferred meeting times** based on existing social/work events
3. **Energy patterns** - when each person is most active/social
4. **Work-life boundaries** - respect their schedules
5. **Social preferences** - what types of activities they enjoy

## TASK INSTRUCTIONS

### PRIMARY OBJECTIVE
Suggest 3 specific meeting times (date + time) that would work well for both Phil and Chris, considering:
1. **Availability** - Both are free
2. **Energy levels** - Optimal times for each person
3. **Social preferences** - When they typically socialize
4. **Work-life balance** - Respecting their boundaries
5. **Practicality** - Realistic and convenient

### CONSTRAINTS
- Meeting duration: 1-2 hours
- Time range: Next 2 weeks from today ({datetime.now().strftime('%Y-%m-%d')})
- Consider time zones (both appear to be in same timezone)
- Avoid times when either person has back-to-back meetings
- Prefer times when both have energy and are in social mode

### OUTPUT FORMAT
Provide exactly 3 suggestions in this JSON format:
```json
{{
  "suggestions": [
    {{
      "date": "YYYY-MM-DD",
      "time": "HH:MM",
      "duration": "X hours",
      "reasoning": "Why this time works well for both people",
      "phil_energy": "High/Medium/Low",
      "chris_energy": "High/Medium/Low",
      "meeting_type": "Coffee/Casual lunch/Evening drinks/Activity"
    }}
  ]
}}
```

### ANALYSIS FRAMEWORK
1. **Identify free time slots** where both are available
2. **Assess energy patterns** - when each person is most social/productive
3. **Consider social preferences** - what types of activities they enjoy
4. **Evaluate convenience** - travel time, preparation needed
5. **Balance preferences** - find times that suit both personalities

### QUALITY CRITERIA
- Times should feel natural and appealing to both
- Consider their different social styles (Phil: active/social, Chris: structured/selective)
- Suggest varied options (different days/times)
- Include reasoning for each suggestion
- Be specific about why each time works

## RESPONSE
Analyze the calendar data and provide your 3 meeting suggestions following the exact JSON format above."""

    return prompt


def generate_meeting_suggestions():
    """Generate AI prompt for meeting suggestions"""
    
    # Load calendar data
    phil_events = load_calendar_data("calendar_events_raw.json")
    chris_events = load_calendar_data("chris_calendar_events_raw.json")
    
    # Create optimized prompt
    prompt = create_ai_prompt(phil_events, chris_events)
    
    # Save prompt to file
    with open("meeting_scheduler_prompt.txt", 'w') as f:
        f.write(prompt)
    
    print("🤖 AI MEETING SCHEDULER PROMPT GENERATED")
    print("=" * 50)
    print("📄 Prompt saved to: meeting_scheduler_prompt.txt")
    print("\n🔍 PROMPT PREVIEW:")
    print("-" * 30)
    print(prompt[:500] + "...")
    print("\n" + "=" * 50)
    print("📋 NEXT STEPS:")
    print("1. Copy the prompt from meeting_scheduler_prompt.txt")
    print("2. Paste into Gemini AI")
    print("3. Get 3 optimal meeting suggestions!")
    
    return prompt

if __name__ == "__main__":
    generate_meeting_suggestions()
