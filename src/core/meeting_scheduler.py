#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core meeting scheduler business logic
Clean Architecture: No I/O dependencies
"""
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple


def format_events_for_ai(events: List[Dict[str, Any]], name: str) -> str:
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


def create_ai_prompt(phil_events: List[Dict[str, Any]], chris_events: List[Dict[str, Any]]) -> str:
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
      "meeting_type": "Coffee/Casual lunch/Evening drinks/Activity",
      "location": "Suggested location (optional)",
      "confidence": 0.85,
      "conflicts": [],
      "preparation_time": "X minutes"
    }}
  ],
  "metadata": {{
    "generated_at": "2025-01-15T10:30:00Z",
    "total_suggestions": 3,
    "analysis_quality": "high",
    "time_range_analyzed": "2025-01-15 to 2025-01-29"
  }}
}}
```

### REQUIRED FIELDS
Each suggestion MUST include:
- date: YYYY-MM-DD format
- time: HH:MM format (24-hour)
- duration: Human-readable (e.g., "1.5 hours", "2 hours")
- reasoning: Detailed explanation of why this time works
- phil_energy: High/Medium/Low
- chris_energy: High/Medium/Low
- meeting_type: Coffee/Casual lunch/Evening drinks/Activity

### OPTIONAL FIELDS (include when relevant)
- location: Suggested meeting location
- confidence: 0.0-1.0 confidence score
- conflicts: Array of potential conflicts
- preparation_time: How much prep time needed

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


def validate_event_dictionary(event: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate event dictionary has correct shape and format"""
    errors = []
    
    # Required fields
    required_fields = ["date", "time", "duration", "reasoning", "phil_energy", "chris_energy", "meeting_type"]
    for field in required_fields:
        if field not in event:
            errors.append(f"Missing required field: {field}")
        elif not event[field] or event[field] == "":
            errors.append(f"Empty required field: {field}")
    
    # Validate energy levels
    valid_energy = ["High", "Medium", "Low"]
    if "phil_energy" in event and event["phil_energy"] not in valid_energy:
        errors.append(f"Invalid phil_energy: {event['phil_energy']}. Must be one of {valid_energy}")
    if "chris_energy" in event and event["chris_energy"] not in valid_energy:
        errors.append(f"Invalid chris_energy: {event['chris_energy']}. Must be one of {valid_energy}")
    
    # Validate meeting types
    valid_meeting_types = ["Coffee", "Casual lunch", "Evening drinks", "Activity"]
    if "meeting_type" in event and event["meeting_type"] not in valid_meeting_types:
        errors.append(f"Invalid meeting_type: {event['meeting_type']}. Must be one of {valid_meeting_types}")
    
    # Validate date format (basic check)
    if "date" in event and event["date"]:
        try:
            datetime.strptime(event["date"], "%Y-%m-%d")
        except ValueError:
            errors.append(f"Invalid date format: {event['date']}. Must be YYYY-MM-DD")
    
    # Validate time format (basic check)
    if "time" in event and event["time"]:
        try:
            datetime.strptime(event["time"], "%H:%M")
        except ValueError:
            errors.append(f"Invalid time format: {event['time']}. Must be HH:MM")
    
    # Validate confidence if present
    if "confidence" in event and event["confidence"] is not None:
        if not isinstance(event["confidence"], (int, float)) or not (0.0 <= event["confidence"] <= 1.0):
            errors.append(f"Invalid confidence: {event['confidence']}. Must be 0.0-1.0")
    
    return len(errors) == 0, errors


def validate_meeting_suggestions(suggestions: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate complete meeting suggestions response"""
    errors = []
    
    if not isinstance(suggestions, dict):
        return False, ["Response must be a dictionary"]
    
    if "suggestions" not in suggestions:
        errors.append("Missing 'suggestions' key")
        return False, errors
    
    if not isinstance(suggestions["suggestions"], list):
        errors.append("'suggestions' must be a list")
        return False, errors
    
    if len(suggestions["suggestions"]) == 0:
        errors.append("No suggestions provided")
        return False, errors
    
    # Validate each suggestion
    for i, suggestion in enumerate(suggestions["suggestions"]):
        is_valid, suggestion_errors = validate_event_dictionary(suggestion)
        if not is_valid:
            for error in suggestion_errors:
                errors.append(f"Suggestion {i+1}: {error}")
    
    return len(errors) == 0, errors
