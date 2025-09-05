#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI adapter for meeting scheduler
Handles user interface and orchestrates the workflow
"""
import sys
from typing import Optional, Dict, Any
from src.core.meeting_scheduler import create_ai_prompt
from src.adapters.gemini_client import get_meeting_suggestions_from_gemini, parse_gemini_response
from src.infrastructure.calendar_loader import (
    load_calendar_data, 
    save_prompt_to_file, 
    save_suggestions_to_file,
    file_exists
)


def generate_meeting_suggestions() -> str:
    """Generate AI prompt for meeting suggestions"""
    
    # Load calendar data
    phil_events = load_calendar_data("calendar_events_raw.json")
    chris_events = load_calendar_data("chris_calendar_events_raw.json")
    
    # Create optimized prompt
    prompt = create_ai_prompt(phil_events, chris_events)
    
    # Save prompt to file
    save_prompt_to_file(prompt, "meeting_scheduler_prompt.txt")
    
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


def get_meeting_suggestions_with_gemini() -> Optional[str]:
    """Use Gemini API to get meeting suggestions"""
    
    # Check if prompt file exists
    if not file_exists("meeting_scheduler_prompt.txt"):
        print("ERROR: meeting_scheduler_prompt.txt not found")
        print("Please run: python3 -m src.adapters.cli generate first")
        return None
    
    # Load the prompt
    with open("meeting_scheduler_prompt.txt", 'r') as f:
        prompt = f.read()
    
    # Get suggestions from Gemini
    response_text = get_meeting_suggestions_from_gemini(prompt)
    
    if not response_text:
        return None
    
    print("\n" + "="*60)
    print("🎯 MEETING SUGGESTIONS")
    print("="*60)
    print(response_text)
    
    # Try to parse JSON response
    suggestions = parse_gemini_response(response_text)
    
    if suggestions:
        print("\n📅 FORMATTED SUGGESTIONS:")
        print("-" * 40)
        
        for i, suggestion in enumerate(suggestions.get('suggestions', []), 1):
            print(f"\n{i}. {suggestion.get('date', 'N/A')} at {suggestion.get('time', 'N/A')}")
            print(f"   Duration: {suggestion.get('duration', 'N/A')}")
            print(f"   Type: {suggestion.get('meeting_type', 'N/A')}")
            print(f"   Phil's Energy: {suggestion.get('phil_energy', 'N/A')}")
            print(f"   Chris's Energy: {suggestion.get('chris_energy', 'N/A')}")
            print(f"   Reasoning: {suggestion.get('reasoning', 'N/A')}")
        
        # Save results
        save_suggestions_to_file(suggestions, "meeting_suggestions.json")
        print(f"\n💾 Results saved to: meeting_suggestions.json")
    
    return response_text


def main() -> None:
    """Main function to run the meeting scheduler"""
    
    print("🚀 GEMINI MEETING SCHEDULER")
    print("=" * 40)
    
    # Get suggestions from Gemini
    result = get_meeting_suggestions_with_gemini()
    
    if result:
        print("\n✅ Meeting suggestions generated successfully!")
    else:
        print("\n❌ Failed to generate meeting suggestions")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "generate":
        generate_meeting_suggestions()
    else:
        main()
