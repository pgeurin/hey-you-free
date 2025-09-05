#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini AI client adapter
Handles external API communication
"""
import json
import os
from typing import Optional, Dict, Any
from src.core.meeting_scheduler import validate_meeting_suggestions


def load_gemini_api_key() -> Optional[str]:
    """Load Gemini API key from environment"""
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("ERROR: GOOGLE_API_KEY not found in environment")
        print("Please set your API key: export GOOGLE_API_KEY='your_key_here'")
        return None
    return api_key


def get_meeting_suggestions_from_gemini(prompt: str, temperature: float = 0.1, seed: Optional[int] = None) -> Optional[str]:
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
        print(f"🌡️  Temperature: {temperature} (lower = more deterministic)")
        if seed:
            print(f"🎲 Seed: {seed} (for reproducibility)")
        print("⏳ Analyzing calendars and generating suggestions...")
        
        # Generate response with temperature control
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            top_p=0.8,  # Focus on most likely tokens
            top_k=40,   # Limit vocabulary for consistency
            max_output_tokens=2048
        )
        
        # Add seed to prompt for reproducibility (Gemini doesn't have direct seed support)
        if seed:
            seeded_prompt = f"SEED: {seed}\n\n{prompt}"
        else:
            seeded_prompt = prompt
        
        response = model.generate_content(
            seeded_prompt,
            generation_config=generation_config
        )
        
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
        
        # Validate the response format
        is_valid, errors = validate_meeting_suggestions(suggestions)
        if not is_valid:
            print("⚠️  AI response format validation failed:")
            for error in errors:
                print(f"   - {error}")
            print("Raw response:")
            print(response_text)
            return None
        
        print("✅ AI response format validated successfully")
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


def get_deterministic_meeting_suggestions(prompt: str, seed: int = 42) -> Optional[str]:
    """Get deterministic meeting suggestions with low temperature and fixed seed"""
    return get_meeting_suggestions_from_gemini(
        prompt=prompt,
        temperature=0.1,  # Very low temperature for consistency
        seed=seed
    )


def get_creative_meeting_suggestions(prompt: str) -> Optional[str]:
    """Get creative meeting suggestions with higher temperature"""
    return get_meeting_suggestions_from_gemini(
        prompt=prompt,
        temperature=0.7,  # Higher temperature for creativity
        seed=None
    )
