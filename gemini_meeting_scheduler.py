#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini AI-powered meeting scheduler
Automatically suggests optimal meeting times using Gemini API
"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

def load_gemini_api():
    """Load Gemini API key from environment"""
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("ERROR: GOOGLE_API_KEY not found in environment")
        print("Please set your API key: export GOOGLE_API_KEY='your_key_here'")
        return None
    return api_key

def get_meeting_suggestions_with_gemini():
    """Use Gemini API to get meeting suggestions"""
    
    # Load API key
    api_key = load_gemini_api()
    if not api_key:
        return None
    
    try:
        import google.generativeai as genai
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Load the prompt
        with open("meeting_scheduler_prompt.txt", 'r') as f:
            prompt = f.read()
        
        print("🤖 Sending request to Gemini AI...")
        print("⏳ Analyzing calendars and generating suggestions...")
        
        # Generate response
        response = model.generate_content(prompt)
        
        print("✅ Response received from Gemini!")
        print("\n" + "="*60)
        print("🎯 MEETING SUGGESTIONS")
        print("="*60)
        
        # Try to parse JSON response
        try:
            # Extract JSON from response
            response_text = response.text
            print(response_text)
            
            # Try to find JSON in the response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            elif "{" in response_text and "}" in response_text:
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                json_text = response_text[json_start:json_end]
            else:
                json_text = response_text
            
            # Parse and display formatted results
            suggestions = json.loads(json_text)
            
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
            with open("meeting_suggestions.json", 'w') as f:
                json.dump(suggestions, f, indent=2)
            
            print(f"\n💾 Results saved to: meeting_suggestions.json")
            
        except json.JSONDecodeError as e:
            print("⚠️  Could not parse JSON response, showing raw text:")
            print(response_text)
            
        except Exception as e:
            print(f"⚠️  Error parsing response: {e}")
            print("Raw response:")
            print(response.text)
        
        return response.text
        
    except ImportError:
        print("ERROR: google-generativeai package not installed")
        print("Run: pip install google-generativeai")
        return None
        
    except Exception as e:
        print(f"ERROR: {e}")
        return None

def main():
    """Main function to run the meeting scheduler"""
    
    print("🚀 GEMINI MEETING SCHEDULER")
    print("=" * 40)
    
    # Check if prompt file exists
    if not Path("meeting_scheduler_prompt.txt").exists():
        print("ERROR: meeting_scheduler_prompt.txt not found")
        print("Please run: python3 ai_meeting_scheduler.py first")
        return
    
    # Get suggestions from Gemini
    result = get_meeting_suggestions_with_gemini()
    
    if result:
        print("\n✅ Meeting suggestions generated successfully!")
    else:
        print("\n❌ Failed to generate meeting suggestions")

if __name__ == "__main__":
    main()
