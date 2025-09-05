#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
True End-to-End Test for Meeting Scheduler
Uses real API calls with seeded data and fixed timestamps
"""
import pytest
import json
import os
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch
from typing import List, Dict, Any, Optional

# Import all components
from src.core.meeting_scheduler import (
    format_events_for_ai, 
    create_ai_prompt, 
    validate_meeting_suggestions
)
from src.adapters.gemini_client import (
    get_meeting_suggestions_from_gemini,
    parse_gemini_response,
    get_deterministic_meeting_suggestions
)
from src.adapters.google_calendar_client import (
    create_custom_date_window,
    fetch_calendar_events,
    save_events_to_file
)
from src.infrastructure.calendar_loader import (
    load_calendar_data,
    save_prompt_to_file,
    save_suggestions_to_file
)


class TestTrueEndToEnd:
    """True end-to-end test with real API calls and seeded data"""
    
    def setup_method(self):
        """Set up test environment with fixed timestamps"""
        # Fixed test date for reproducible results
        self.test_date = datetime(2025, 1, 15, 10, 0, 0)  # Wednesday 10:00 AM
        
        # Create realistic calendar data with fixed timestamps
        self.phil_events = [
            {
                "kind": "calendar#event",
                "summary": "Morning Standup",
                "start": {"dateTime": "2025-01-16T09:00:00Z"},
                "location": "Office",
                "description": "Daily team sync"
            },
            {
                "kind": "calendar#event",
                "summary": "Client Meeting",
                "start": {"dateTime": "2025-01-16T14:00:00Z"},
                "location": "Conference Room A",
                "description": "Project review with client"
            },
            {
                "kind": "calendar#event",
                "summary": "Coffee Break",
                "start": {"dateTime": "2025-01-17T10:30:00Z"},
                "location": "Downtown Cafe",
                "description": "Casual coffee with team"
            },
            {
                "kind": "calendar#event",
                "summary": "Deep Work",
                "start": {"dateTime": "2025-01-17T15:00:00Z"},
                "location": "Home Office",
                "description": "Focused coding session"
            },
            {
                "kind": "calendar#event",
                "summary": "Evening Drinks",
                "start": {"dateTime": "2025-01-18T18:00:00Z"},
                "location": "Local Bar",
                "description": "Social time with friends"
            }
        ]
        
        self.chris_events = [
            {
                "kind": "calendar#event",
                "summary": "Work Session",
                "start": {"dateTime": "2025-01-16T08:00:00Z"},
                "location": "Home",
                "description": "Early morning productivity"
            },
            {
                "kind": "calendar#event",
                "summary": "Team Meeting",
                "start": {"dateTime": "2025-01-16T11:00:00Z"},
                "location": "Office",
                "description": "Weekly planning session"
            },
            {
                "kind": "calendar#event",
                "summary": "Lunch with Colleagues",
                "start": {"dateTime": "2025-01-17T12:00:00Z"},
                "location": "Restaurant",
                "description": "Team building lunch"
            },
            {
                "kind": "calendar#event",
                "summary": "Gym Session",
                "start": {"dateTime": "2025-01-17T17:00:00Z"},
                "location": "Fitness Center",
                "description": "Regular workout"
            },
            {
                "kind": "calendar#event",
                "summary": "Family Dinner",
                "start": {"dateTime": "2025-01-18T19:00:00Z"},
                "location": "Home",
                "description": "Weekly family time"
            }
        ]
        
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.phil_file = os.path.join(self.temp_dir, "phil_calendar.json")
        self.chris_file = os.path.join(self.temp_dir, "chris_calendar.json")
        self.output_dir = os.path.join(self.temp_dir, "output")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Save test data to files
        with open(self.phil_file, 'w') as f:
            json.dump(self.phil_events, f, indent=2)
        with open(self.chris_file, 'w') as f:
            json.dump(self.chris_events, f, indent=2)
    
    def teardown_method(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_calendar_data_loading(self):
        """Test loading calendar data from files"""
        print("\n🔍 TESTING: Calendar Data Loading")
        
        phil_loaded = load_calendar_data(self.phil_file)
        chris_loaded = load_calendar_data(self.chris_file)
        
        assert len(phil_loaded) == 5
        assert len(chris_loaded) == 5
        assert phil_loaded[0]["summary"] == "Morning Standup"
        assert chris_loaded[0]["summary"] == "Work Session"
        
        print("✅ Calendar data loaded successfully")
        print(f"   Phil events: {len(phil_loaded)}")
        print(f"   Chris events: {len(chris_loaded)}")
    
    def test_event_formatting_for_ai(self):
        """Test formatting events for AI analysis"""
        print("\n🔍 TESTING: Event Formatting for AI")
        
        phil_formatted = format_events_for_ai(self.phil_events, "Phil")
        chris_formatted = format_events_for_ai(self.chris_events, "Chris")
        
        assert "Total events: 5" in phil_formatted
        assert "Total events: 5" in chris_formatted
        assert "2025-01-16 (Thursday) 09:00 - Morning Standup" in phil_formatted
        assert "2025-01-16 (Thursday) 08:00 - Work Session" in chris_formatted
        assert "@ Office" in phil_formatted
        assert "@ Home" in chris_formatted
        
        print("✅ Event formatting successful")
        print(f"   Phil formatted length: {len(phil_formatted)} chars")
        print(f"   Chris formatted length: {len(chris_formatted)} chars")
    
    def test_ai_prompt_generation(self):
        """Test AI prompt generation with realistic data"""
        print("\n🔍 TESTING: AI Prompt Generation")
        
        prompt = create_ai_prompt(self.phil_events, self.chris_events)
        
        # Verify prompt structure
        assert "MEETING SCHEDULER AI ASSISTANT" in prompt
        assert "PHIL'S CALENDAR EVENTS:" in prompt
        assert "CHRIS'S CALENDAR EVENTS:" in prompt
        assert "Morning Standup" in prompt
        assert "Work Session" in prompt
        assert "```json" in prompt
        assert "suggestions" in prompt
        
        # Check current date is included
        current_date = datetime.now().strftime('%Y-%m-%d')
        assert current_date in prompt
        
        print("✅ AI prompt generation successful")
        print(f"   Prompt length: {len(prompt)} characters")
        print(f"   Contains current date: {current_date}")
    
    @pytest.mark.skipif(not os.getenv('GOOGLE_API_KEY'), reason="GOOGLE_API_KEY not set")
    def test_real_gemini_api_call_deterministic(self):
        """Test real Gemini API call with deterministic settings"""
        print("\n🔍 TESTING: Real Gemini API Call (Deterministic)")
        
        # Create prompt
        prompt = create_ai_prompt(self.phil_events, self.chris_events)
        
        # Call Gemini with deterministic settings
        response = get_deterministic_meeting_suggestions(prompt, seed=42)
        
        assert response is not None
        assert len(response) > 0
        
        # Parse and validate response
        suggestions = parse_gemini_response(response)
        assert suggestions is not None
        assert "suggestions" in suggestions
        assert len(suggestions["suggestions"]) > 0
        
        # Validate each suggestion
        for suggestion in suggestions["suggestions"]:
            assert "date" in suggestion
            assert "time" in suggestion
            assert "duration" in suggestion
            assert "reasoning" in suggestion
            assert "phil_energy" in suggestion
            assert "chris_energy" in suggestion
            assert "meeting_type" in suggestion
        
        print("✅ Real Gemini API call successful")
        print(f"   Generated {len(suggestions['suggestions'])} suggestions")
        print(f"   First suggestion: {suggestions['suggestions'][0]['date']} at {suggestions['suggestions'][0]['time']}")
    
    @pytest.mark.skipif(not os.getenv('GOOGLE_API_KEY'), reason="GOOGLE_API_KEY not set")
    def test_real_gemini_api_call_creative(self):
        """Test real Gemini API call with creative settings"""
        print("\n🔍 TESTING: Real Gemini API Call (Creative)")
        
        # Create prompt
        prompt = create_ai_prompt(self.phil_events, self.chris_events)
        
        # Call Gemini with creative settings
        response = get_meeting_suggestions_from_gemini(prompt, temperature=0.8)
        
        assert response is not None
        assert len(response) > 0
        
        # Parse and validate response
        suggestions = parse_gemini_response(response)
        assert suggestions is not None
        assert "suggestions" in suggestions
        assert len(suggestions["suggestions"]) > 0
        
        print("✅ Real Gemini API call (creative) successful")
        print(f"   Generated {len(suggestions['suggestions'])} suggestions")
    
    @pytest.mark.skipif(not os.getenv('GOOGLE_API_KEY'), reason="GOOGLE_API_KEY not set")
    def test_complete_workflow_with_real_apis(self):
        """Test complete workflow with real API calls"""
        print("\n🔍 TESTING: Complete Workflow with Real APIs")
        
        # Step 1: Load calendar data
        phil_events = load_calendar_data(self.phil_file)
        chris_events = load_calendar_data(self.chris_file)
        
        # Step 2: Generate AI prompt
        prompt = create_ai_prompt(phil_events, chris_events)
        
        # Step 3: Save prompt to file
        prompt_file = os.path.join(self.output_dir, "meeting_prompt.txt")
        save_prompt_to_file(prompt, prompt_file)
        
        # Step 4: Call Gemini API
        response = get_deterministic_meeting_suggestions(prompt, seed=123)
        assert response is not None
        
        # Step 5: Parse response
        suggestions = parse_gemini_response(response)
        assert suggestions is not None
        
        # Step 6: Validate suggestions
        is_valid, errors = validate_meeting_suggestions(suggestions)
        assert is_valid, f"Validation failed: {errors}"
        
        # Step 7: Save suggestions to file
        suggestions_file = os.path.join(self.output_dir, "meeting_suggestions.json")
        save_suggestions_to_file(suggestions, suggestions_file)
        
        # Verify files exist
        assert os.path.exists(prompt_file)
        assert os.path.exists(suggestions_file)
        
        print("✅ Complete workflow successful")
        print(f"   Generated {len(suggestions['suggestions'])} suggestions")
        print(f"   Files saved: {prompt_file}, {suggestions_file}")
    
    @pytest.mark.skipif(not os.getenv('GOOGLE_API_KEY'), reason="GOOGLE_API_KEY not set")
    def test_deterministic_reproducibility(self):
        """Test that deterministic calls produce same results"""
        print("\n🔍 TESTING: Deterministic Reproducibility")
        
        prompt = create_ai_prompt(self.phil_events, self.chris_events)
        
        # Make two calls with same seed
        response1 = get_deterministic_meeting_suggestions(prompt, seed=42)
        response2 = get_deterministic_meeting_suggestions(prompt, seed=42)
        
        assert response1 is not None
        assert response2 is not None
        
        # Parse both responses
        suggestions1 = parse_gemini_response(response1)
        suggestions2 = parse_gemini_response(response2)
        
        assert suggestions1 is not None
        assert suggestions2 is not None
        
        # Compare first suggestions (should be identical with same seed)
        if len(suggestions1["suggestions"]) > 0 and len(suggestions2["suggestions"]) > 0:
            first1 = suggestions1["suggestions"][0]
            first2 = suggestions2["suggestions"][0]
            
            # Key fields should match
            assert first1["date"] == first2["date"]
            assert first1["time"] == first2["time"]
            assert first1["meeting_type"] == first2["meeting_type"]
        
        print("✅ Deterministic reproducibility confirmed")
        print("   Same seed produces consistent results")
    
    @pytest.mark.skipif(not os.getenv('GOOGLE_API_KEY'), reason="GOOGLE_API_KEY not set")
    def test_different_seeds_produce_different_results(self):
        """Test that different seeds produce different results"""
        print("\n🔍 TESTING: Different Seeds Produce Different Results")
        
        prompt = create_ai_prompt(self.phil_events, self.chris_events)
        
        # Make calls with different seeds
        response1 = get_deterministic_meeting_suggestions(prompt, seed=42)
        response2 = get_deterministic_meeting_suggestions(prompt, seed=123)
        
        assert response1 is not None
        assert response2 is not None
        
        # Parse both responses
        suggestions1 = parse_gemini_response(response1)
        suggestions2 = parse_gemini_response(response2)
        
        assert suggestions1 is not None
        assert suggestions2 is not None
        
        # Results should be different (at least in some fields)
        if len(suggestions1["suggestions"]) > 0 and len(suggestions2["suggestions"]) > 0:
            first1 = suggestions1["suggestions"][0]
            first2 = suggestions2["suggestions"][0]
            
            # At least some fields should differ
            different_fields = []
            for field in ["date", "time", "reasoning", "phil_energy", "chris_energy"]:
                if first1.get(field) != first2.get(field):
                    different_fields.append(field)
            
            assert len(different_fields) > 0, "Different seeds should produce different results"
        
        print("✅ Different seeds produce different results confirmed")
        print(f"   Different fields: {different_fields if 'different_fields' in locals() else 'N/A'}")
    
    def test_error_handling_without_api_key(self):
        """Test error handling when API key is not available"""
        print("\n🔍 TESTING: Error Handling Without API Key")
        
        # Temporarily remove API key
        original_key = os.environ.get('GOOGLE_API_KEY')
        if 'GOOGLE_API_KEY' in os.environ:
            del os.environ['GOOGLE_API_KEY']
        
        try:
            prompt = create_ai_prompt(self.phil_events, self.chris_events)
            response = get_deterministic_meeting_suggestions(prompt, seed=42)
            
            # Should return None when API key is missing
            assert response is None
            
        finally:
            # Restore API key
            if original_key:
                os.environ['GOOGLE_API_KEY'] = original_key
        
        print("✅ Error handling without API key works correctly")
    
    def test_validation_with_real_ai_response(self):
        """Test validation with a realistic AI response format"""
        print("\n🔍 TESTING: Validation with Real AI Response Format")
        
        # Simulate a realistic AI response
        realistic_response = """{
            "suggestions": [
                {
                    "date": "2025-01-20",
                    "time": "15:30",
                    "duration": "1.5 hours",
                    "reasoning": "Both Phil and Chris have free time after lunch, good energy levels",
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
                    "reasoning": "End of day, both winding down, good for social time",
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
        
        # Parse and validate
        suggestions = parse_gemini_response(realistic_response)
        assert suggestions is not None
        
        is_valid, errors = validate_meeting_suggestions(suggestions)
        assert is_valid, f"Validation failed: {errors}"
        
        assert len(suggestions["suggestions"]) == 3
        assert suggestions["suggestions"][0]["date"] == "2025-01-20"
        assert suggestions["suggestions"][0]["meeting_type"] == "Coffee"
        
        print("✅ Validation with realistic AI response successful")
        print(f"   Validated {len(suggestions['suggestions'])} suggestions")


def test_run_true_end_to_end_suite():
    """Run the complete true end-to-end test suite"""
    print("\n" + "="*80)
    print("🚀 RUNNING TRUE END-TO-END TEST SUITE")
    print("="*80)
    print("📝 Note: Some tests require GOOGLE_API_KEY environment variable")
    print("="*80)
    
    # Create test instance
    test_instance = TestTrueEndToEnd()
    test_instance.setup_method()
    
    try:
        # Run all test steps
        test_instance.test_calendar_data_loading()
        test_instance.test_event_formatting_for_ai()
        test_instance.test_ai_prompt_generation()
        
        # Only run API tests if key is available
        if os.getenv('GOOGLE_API_KEY'):
            test_instance.test_real_gemini_api_call_deterministic()
            test_instance.test_real_gemini_api_call_creative()
            test_instance.test_complete_workflow_with_real_apis()
            test_instance.test_deterministic_reproducibility()
            test_instance.test_different_seeds_produce_different_results()
        else:
            print("\n⚠️  Skipping API tests - GOOGLE_API_KEY not set")
        
        test_instance.test_error_handling_without_api_key()
        test_instance.test_validation_with_real_ai_response()
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        raise
        
    finally:
        test_instance.teardown_method()
    
    print("\n" + "="*80)
    print("🎯 TRUE END-TO-END TEST SUITE COMPLETE")
    print("="*80)


if __name__ == "__main__":
    # Run the true end-to-end test suite
    test_run_true_end_to_end_suite()
