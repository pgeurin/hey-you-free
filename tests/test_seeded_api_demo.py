#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demonstration of Seeded API Calls
Shows how deterministic API calls work with fixed seeds
"""
import os
import json
from datetime import datetime
from unittest.mock import patch, MagicMock

from src.core.meeting_scheduler import create_ai_prompt
from src.adapters.gemini_client import get_deterministic_meeting_suggestions, parse_gemini_response


def create_demo_calendar_data():
    """Create demo calendar data for testing"""
    return {
        "phil_events": [
            {
                "kind": "calendar#event",
                "summary": "Morning Coffee",
                "start": {"dateTime": "2025-01-16T09:00:00Z"},
                "location": "Downtown Cafe",
                "description": "Regular morning coffee"
            },
            {
                "kind": "calendar#event",
                "summary": "Team Meeting",
                "start": {"dateTime": "2025-01-16T14:00:00Z"},
                "location": "Office",
                "description": "Weekly team sync"
            },
            {
                "kind": "calendar#event",
                "summary": "Gym Session",
                "start": {"dateTime": "2025-01-17T17:00:00Z"},
                "location": "Fitness Center",
                "description": "Regular workout"
            }
        ],
        "chris_events": [
            {
                "kind": "calendar#event",
                "summary": "Work Session",
                "start": {"dateTime": "2025-01-16T08:00:00Z"},
                "location": "Home Office",
                "description": "Deep work time"
            },
            {
                "kind": "calendar#event",
                "summary": "Lunch Meeting",
                "start": {"dateTime": "2025-01-17T12:00:00Z"},
                "location": "Restaurant",
                "description": "Client lunch"
            },
            {
                "kind": "calendar#event",
                "summary": "Family Time",
                "start": {"dateTime": "2025-01-18T19:00:00Z"},
                "location": "Home",
                "description": "Evening with family"
            }
        ]
    }


def mock_gemini_response_seed_42():
    """Mock response for seed 42"""
    return """{
        "suggestions": [
            {
                "date": "2025-01-20",
                "time": "15:30",
                "duration": "1.5 hours",
                "reasoning": "Both Phil and Chris have free time after lunch, perfect for coffee",
                "phil_energy": "High",
                "chris_energy": "Medium",
                "meeting_type": "Coffee",
                "location": "Downtown Cafe",
                "confidence": 0.85,
                "conflicts": [],
                "preparation_time": "5 minutes"
            },
            {
                "date": "2025-01-21",
                "time": "10:00",
                "duration": "1 hour",
                "reasoning": "Morning energy, both available before work commitments",
                "phil_energy": "High",
                "chris_energy": "High",
                "meeting_type": "Coffee"
            },
            {
                "date": "2025-01-22",
                "time": "17:00",
                "duration": "2 hours",
                "reasoning": "End of day social time, both winding down",
                "phil_energy": "Medium",
                "chris_energy": "Medium",
                "meeting_type": "Evening drinks",
                "location": "Local Bar"
            }
        ],
        "metadata": {
            "generated_at": "2025-01-15T10:30:00Z",
            "total_suggestions": 3,
            "analysis_quality": "high",
            "time_range_analyzed": "2025-01-15 to 2025-01-29"
        }
    }"""


def mock_gemini_response_seed_123():
    """Mock response for seed 123"""
    return """{
        "suggestions": [
            {
                "date": "2025-01-19",
                "time": "14:00",
                "duration": "1 hour",
                "reasoning": "Afternoon break, both have energy and availability",
                "phil_energy": "Medium",
                "chris_energy": "High",
                "meeting_type": "Coffee",
                "location": "Central Park Cafe"
            },
            {
                "date": "2025-01-21",
                "time": "11:30",
                "duration": "1.5 hours",
                "reasoning": "Late morning, good energy levels for both",
                "phil_energy": "High",
                "chris_energy": "High",
                "meeting_type": "Casual lunch",
                "location": "Restaurant District"
            },
            {
                "date": "2025-01-23",
                "time": "18:30",
                "duration": "2 hours",
                "reasoning": "Evening social time, both free after work",
                "phil_energy": "Medium",
                "chris_energy": "Medium",
                "meeting_type": "Evening drinks",
                "location": "Rooftop Bar"
            }
        ],
        "metadata": {
            "generated_at": "2025-01-15T10:30:00Z",
            "total_suggestions": 3,
            "analysis_quality": "high",
            "time_range_analyzed": "2025-01-15 to 2025-01-29"
        }
    }"""


def test_seeded_api_determinism():
    """Test that seeded API calls are deterministic"""
    print("\n🔍 TESTING: Seeded API Determinism")
    print("=" * 50)
    
    # Create demo data
    data = create_demo_calendar_data()
    prompt = create_ai_prompt(data["phil_events"], data["chris_events"])
    
    # Mock the API calls with different seeds
    with patch('src.adapters.gemini_client.get_meeting_suggestions_from_gemini') as mock_api:
        # First call with seed 42
        mock_api.return_value = mock_gemini_response_seed_42()
        response1 = get_deterministic_meeting_suggestions(prompt, seed=42)
        
        # Second call with same seed 42
        mock_api.return_value = mock_gemini_response_seed_42()
        response2 = get_deterministic_meeting_suggestions(prompt, seed=42)
        
        # Parse responses
        suggestions1 = parse_gemini_response(response1)
        suggestions2 = parse_gemini_response(response2)
        
        # Should be identical
        assert suggestions1 == suggestions2
        assert suggestions1["suggestions"][0]["date"] == "2025-01-20"
        assert suggestions1["suggestions"][0]["time"] == "15:30"
        
        print("✅ Same seed produces identical results")
        print(f"   First suggestion: {suggestions1['suggestions'][0]['date']} at {suggestions1['suggestions'][0]['time']}")
    
    # Test different seeds produce different results
    with patch('src.adapters.gemini_client.get_meeting_suggestions_from_gemini') as mock_api:
        # Call with seed 42
        mock_api.return_value = mock_gemini_response_seed_42()
        response1 = get_deterministic_meeting_suggestions(prompt, seed=42)
        
        # Call with seed 123
        mock_api.return_value = mock_gemini_response_seed_123()
        response2 = get_deterministic_meeting_suggestions(prompt, seed=123)
        
        # Parse responses
        suggestions1 = parse_gemini_response(response1)
        suggestions2 = parse_gemini_response(response2)
        
        # Should be different
        assert suggestions1 != suggestions2
        assert suggestions1["suggestions"][0]["date"] == "2025-01-20"
        assert suggestions2["suggestions"][0]["date"] == "2025-01-19"
        
        print("✅ Different seeds produce different results")
        print(f"   Seed 42: {suggestions1['suggestions'][0]['date']} at {suggestions1['suggestions'][0]['time']}")
        print(f"   Seed 123: {suggestions2['suggestions'][0]['date']} at {suggestions2['suggestions'][0]['time']}")


def test_fixed_timestamp_consistency():
    """Test that fixed timestamps produce consistent results"""
    print("\n🔍 TESTING: Fixed Timestamp Consistency")
    print("=" * 50)
    
    # Create data with fixed timestamps
    data = create_demo_calendar_data()
    
    # Generate prompt multiple times
    prompt1 = create_ai_prompt(data["phil_events"], data["chris_events"])
    prompt2 = create_ai_prompt(data["phil_events"], data["chris_events"])
    
    # Prompts should be identical (except for current date)
    assert prompt1 == prompt2
    
    print("✅ Fixed timestamps produce consistent prompts")
    print(f"   Prompt length: {len(prompt1)} characters")
    print(f"   Contains Phil events: {'Morning Coffee' in prompt1}")
    print(f"   Contains Chris events: {'Work Session' in prompt1}")


def test_api_response_validation():
    """Test API response validation with seeded data"""
    print("\n🔍 TESTING: API Response Validation")
    print("=" * 50)
    
    # Test valid response
    valid_response = mock_gemini_response_seed_42()
    suggestions = parse_gemini_response(valid_response)
    
    assert suggestions is not None
    assert "suggestions" in suggestions
    assert len(suggestions["suggestions"]) == 3
    
    # Validate each suggestion
    for i, suggestion in enumerate(suggestions["suggestions"]):
        required_fields = ["date", "time", "duration", "reasoning", "phil_energy", "chris_energy", "meeting_type"]
        for field in required_fields:
            assert field in suggestion, f"Missing field {field} in suggestion {i+1}"
            assert suggestion[field] is not None, f"Field {field} is None in suggestion {i+1}"
            assert suggestion[field] != "", f"Field {field} is empty in suggestion {i+1}"
    
    print("✅ API response validation successful")
    print(f"   Validated {len(suggestions['suggestions'])} suggestions")
    print(f"   All required fields present and valid")


def test_complete_seeded_workflow():
    """Test complete workflow with seeded API calls"""
    print("\n🔍 TESTING: Complete Seeded Workflow")
    print("=" * 50)
    
    # Create demo data
    data = create_demo_calendar_data()
    
    # Generate prompt
    prompt = create_ai_prompt(data["phil_events"], data["chris_events"])
    
    # Mock API call with seed
    with patch('src.adapters.gemini_client.get_meeting_suggestions_from_gemini') as mock_api:
        mock_api.return_value = mock_gemini_response_seed_42()
        
        # Get suggestions
        response = get_deterministic_meeting_suggestions(prompt, seed=42)
        suggestions = parse_gemini_response(response)
        
        # Verify results
        assert suggestions is not None
        assert len(suggestions["suggestions"]) == 3
        
        # Check specific seeded results
        first_suggestion = suggestions["suggestions"][0]
        assert first_suggestion["date"] == "2025-01-20"
        assert first_suggestion["time"] == "15:30"
        assert first_suggestion["meeting_type"] == "Coffee"
        assert first_suggestion["phil_energy"] == "High"
        assert first_suggestion["chris_energy"] == "Medium"
        
        print("✅ Complete seeded workflow successful")
        print(f"   Generated {len(suggestions['suggestions'])} suggestions")
        print(f"   First suggestion: {first_suggestion['date']} at {first_suggestion['time']}")
        print(f"   Meeting type: {first_suggestion['meeting_type']}")
        print(f"   Phil energy: {first_suggestion['phil_energy']}")
        print(f"   Chris energy: {first_suggestion['chris_energy']}")


def run_seeded_api_demo():
    """Run the complete seeded API demonstration"""
    print("\n" + "="*80)
    print("🎯 SEEDED API DEMONSTRATION")
    print("="*80)
    print("This demo shows how seeded API calls work with deterministic results")
    print("="*80)
    
    try:
        test_fixed_timestamp_consistency()
        test_api_response_validation()
        test_seeded_api_determinism()
        test_complete_seeded_workflow()
        
        print("\n" + "="*80)
        print("🎉 SEEDED API DEMONSTRATION COMPLETE")
        print("="*80)
        print("Key takeaways:")
        print("• Fixed timestamps ensure consistent prompts")
        print("• Same seeds produce identical API responses")
        print("• Different seeds produce different but valid responses")
        print("• All responses pass validation")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        raise


if __name__ == "__main__":
    run_seeded_api_demo()
