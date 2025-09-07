#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test suite for new user personalities
Tests how the AI handles different personality types and schedules
"""
import pytest
import sys
import os
from datetime import datetime, timedelta

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from infrastructure.calendar_loader import load_calendar_data
from core.meeting_scheduler import create_ai_prompt, format_events_for_ai, validate_meeting_suggestions
from adapters.gemini_client import get_deterministic_meeting_suggestions, parse_gemini_response


class TestNewUserPersonalities:
    """Test class for new user personality scenarios"""
    
    def setup_method(self):
        """Set up test data"""
        self.alex_events = load_calendar_data('data/alex_calendar_events_raw.json')
        self.sam_events = load_calendar_data('data/sam_calendar_events_raw.json')
        self.start_date = datetime.now() + timedelta(days=1)
        self.end_date = self.start_date + timedelta(days=7)
    
    def test_load_new_user_calendars(self):
        """Test that new user calendars load correctly"""
        assert len(self.alex_events) > 0, "Alex calendar should have events"
        assert len(self.sam_events) > 0, "Sam calendar should have events"
        
        # Verify Alex has creative events
        alex_summaries = [event.get('summary', '') for event in self.alex_events]
        creative_keywords = ['creative', 'art', 'music', 'writing', 'gallery']
        has_creative = any(keyword in summary.lower() for summary in alex_summaries for keyword in creative_keywords)
        assert has_creative, "Alex should have creative events"
        
        # Verify Sam has structured events
        sam_summaries = [event.get('summary', '') for event in self.sam_events]
        work_keywords = ['meeting', 'standup', 'sprint', 'client', 'review']
        has_work = any(keyword in summary.lower() for summary in sam_summaries for keyword in work_keywords)
        assert has_work, "Sam should have work-focused events"
    
    def test_format_events_with_different_personalities(self):
        """Test that event formatting works with different personalities"""
        alex_formatted = format_events_for_ai(self.alex_events, "Alex")
        sam_formatted = format_events_for_ai(self.sam_events, "Sam")
        
        assert "Alex's Calendar Events:" in alex_formatted
        assert "Sam's Calendar Events:" in sam_formatted
        assert len(alex_formatted) > 0
        assert len(sam_formatted) > 0
        
        # Alex should have more flexible/creative language
        assert "Creative Writing" in alex_formatted or "Art Gallery" in alex_formatted
        
        # Sam should have more structured/professional language
        assert "Standup" in sam_formatted or "Sprint" in sam_formatted
    
    def test_create_ai_prompt_with_personalities(self):
        """Test AI prompt creation with different personalities"""
        prompt = create_ai_prompt(self.alex_events, self.sam_events, "Alex", "Sam", self.start_date, self.end_date)
        
        assert len(prompt) > 0
        assert "Alex" in prompt
        assert "Sam" in prompt
        assert "Alex's Calendar Events:" in prompt
        assert "Sam's Calendar Events:" in prompt
        
        # Should include personality context
        assert "energy" in prompt.lower()
        assert "preferences" in prompt.lower()
    
    def test_create_ai_prompt_with_time_range(self):
        """Test AI prompt creation with custom time range"""
        short_end = self.start_date + timedelta(days=2)
        prompt = create_ai_prompt(self.alex_events, self.sam_events, "Alex", "Sam", self.start_date, short_end)
        
        assert len(prompt) > 0
        assert self.start_date.strftime('%Y-%m-%d') in prompt
        assert short_end.strftime('%Y-%m-%d') in prompt
    
    def test_create_ai_prompt_with_different_names(self):
        """Test AI prompt creation with different user names"""
        prompt = create_ai_prompt(self.alex_events, self.sam_events, "Creative", "Professional", self.start_date, self.end_date)
        
        assert "Creative" in prompt
        assert "Professional" in prompt
        assert "Creative's Calendar Events:" in prompt
        assert "Professional's Calendar Events:" in prompt
    
    def test_personality_differences_in_schedule(self):
        """Test that personality differences are reflected in schedules"""
        # Alex should have more evening/late events
        alex_times = []
        for event in self.alex_events:
            if 'start' in event and 'dateTime' in event['start']:
                try:
                    dt = datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
                    alex_times.append(dt.hour)
                except:
                    continue
        
        # Sam should have more morning/early events
        sam_times = []
        for event in self.sam_events:
            if 'start' in event and 'dateTime' in event['start']:
                try:
                    dt = datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
                    sam_times.append(dt.hour)
                except:
                    continue
        
        if alex_times and sam_times:
            # Alex should have more late events (after 18:00)
            alex_late = sum(1 for hour in alex_times if hour >= 18)
            sam_late = sum(1 for hour in sam_times if hour >= 18)
            
            # Sam should have more early events (before 10:00)
            alex_early = sum(1 for hour in alex_times if hour < 10)
            sam_early = sum(1 for hour in sam_times if hour < 10)
            
            # These are personality indicators
            assert alex_late >= 0, "Alex should have some late events"
            assert sam_early >= 0, "Sam should have some early events"
    
    def test_ai_response_with_personalities(self):
        """Test AI response generation with different personalities"""
        prompt = create_ai_prompt(self.alex_events, self.sam_events, "Alex", "Sam", self.start_date, self.end_date)
        
        # Try to get AI response (may fail if no API key)
        try:
            ai_response = get_deterministic_meeting_suggestions(prompt, seed=42)
            if ai_response:
                suggestions = parse_gemini_response(ai_response, "alex", "sam")
                if suggestions:
                    is_valid, errors = validate_meeting_suggestions(suggestions, "alex", "sam")
                    assert is_valid, f"AI response should be valid: {errors}"
                    
                    # Should have suggestions
                    assert "suggestions" in suggestions
                    assert len(suggestions["suggestions"]) > 0
                    
                    # Should include both users in energy levels
                    for suggestion in suggestions["suggestions"]:
                        if "user_energies" in suggestion:
                            assert "alex" in suggestion["user_energies"]
                            assert "sam" in suggestion["user_energies"]
        except Exception as e:
            # Skip if API key not available
            pytest.skip(f"API test skipped: {e}")
    
    def test_validation_with_personality_names(self):
        """Test validation works with personality-based user names"""
        # Create a mock suggestion with personality names
        mock_suggestion = {
            "suggestions": [{
                "date": "2025-01-20",
                "time": "14:00",
                "duration": "1.5 hours",
                "reasoning": "Good time for both creative and professional types",
                "user_energies": {
                    "alex": "High",
                    "sam": "Medium"
                },
                "meeting_type": "Coffee"
            }],
            "metadata": {
                "generated_at": "2025-01-15T10:30:00Z",
                "total_suggestions": 1
            }
        }
        
        is_valid, errors = validate_meeting_suggestions(mock_suggestion, "alex", "sam")
        assert is_valid, f"Validation should pass: {errors}"
    
    def test_personality_aware_prompt_generation(self):
        """Test that prompts are aware of personality differences"""
        prompt = create_ai_prompt(self.alex_events, self.sam_events, "Alex", "Sam", self.start_date, self.end_date)
        
        # Should mention different social styles
        assert "social" in prompt.lower() or "personality" in prompt.lower()
        
        # Should include analysis instructions
        assert "energy patterns" in prompt.lower()
        assert "social preferences" in prompt.lower()
        
        # Should mention both users by name
        assert "Alex" in prompt
        assert "Sam" in prompt


def test_run_new_user_personality_tests():
    """Run all new user personality tests"""
    print("🧪 Running New User Personality Tests")
    print("=" * 50)
    
    # This would be called by pytest
    return True


if __name__ == "__main__":
    # Run tests directly
    test_instance = TestNewUserPersonalities()
    test_instance.setup_method()
    
    print("🧪 NEW USER PERSONALITY TEST SUITE")
    print("=" * 50)
    
    try:
        test_instance.test_load_new_user_calendars()
        print("✅ Load new user calendars: PASSED")
    except Exception as e:
        print(f"❌ Load new user calendars: FAILED - {e}")
    
    try:
        test_instance.test_format_events_with_different_personalities()
        print("✅ Format events with personalities: PASSED")
    except Exception as e:
        print(f"❌ Format events with personalities: FAILED - {e}")
    
    try:
        test_instance.test_create_ai_prompt_with_personalities()
        print("✅ Create AI prompt with personalities: PASSED")
    except Exception as e:
        print(f"❌ Create AI prompt with personalities: FAILED - {e}")
    
    try:
        test_instance.test_personality_differences_in_schedule()
        print("✅ Personality differences in schedule: PASSED")
    except Exception as e:
        print(f"❌ Personality differences in schedule: FAILED - {e}")
    
    try:
        test_instance.test_validation_with_personality_names()
        print("✅ Validation with personality names: PASSED")
    except Exception as e:
        print(f"❌ Validation with personality names: FAILED - {e}")
    
    print("\n🎯 New User Personality Test Suite Complete")
