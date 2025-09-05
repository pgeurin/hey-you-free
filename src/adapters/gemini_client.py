#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini AI client adapter
Handles external API communication
"""
import json
import os
from typing import Optional, Dict, Any


def load_gemini_api_key() -> Optional[str]:
    """Load Gemini API key from environment"""
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("ERROR: GOOGLE_API_KEY not found in environment")
        print("Please set your API key: export GOOGLE_API_KEY='your_key_here'")
        return None
    return api_key


def get_meeting_suggestions_from_gemini(prompt: str) -> Optional[str]:
    """Use Gemini API to get meeting suggestions"""
    
    # Load API key
    api_key = load_gemini_api_key()
    if not api_key:
        return None
    
    try:
        import google.generativeai as genai
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        print("🤖 Sending request to Gemini AI...")
        print("⏳ Analyzing calendars and generating suggestions...")
        
        # Generate response
        response = model.generate_content(prompt)
        
        print("✅ Response received from Gemini!")
        return response.text
        
    except ImportError:
        print("ERROR: google-generativeai package not installed")
        print("Run: pip install google-generativeai")
        return None
        
    except Exception as e:
        print(f"ERROR: {e}")
        return None


def parse_gemini_response(response_text: str) -> Optional[Dict[str, Any]]:
    """Parse JSON response from Gemini"""
    try:
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
        
        # Parse JSON
        suggestions = json.loads(json_text)
        return suggestions
        
    except json.JSONDecodeError as e:
        print("⚠️  Could not parse JSON response, showing raw text:")
        print(response_text)
        return None
        
    except Exception as e:
        print(f"⚠️  Error parsing response: {e}")
        print("Raw response:")
        print(response_text)
        return None
