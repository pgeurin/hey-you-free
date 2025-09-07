#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for updated create_ai_prompt function with time range parameters
"""
import pytest
import sys
import os
from datetime import datetime, timedelta

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.meeting_scheduler import create_ai_prompt


class TestCreateAiPromptUpdate:
    """Test updated create_ai_prompt function with time range parameters"""
    
    def setup_method(self):
        """Set up test data"""
        self.sample_events = [
            {
                "kind": "calendar#event",
                "summary": "Morning Standup",
                "start": {"dateTime": "2025-01-16T09:00:00Z"},
                "location": "Office",
                "description": "Daily team sync"
            },
            {
                "kind": "calendar#event", 
                "summary": "Lunch with Sarah",
                "start": {"dateTime": "2025-01-16T12:30:00Z"},
                "location": "Downtown Cafe",
                "description": "Catch up over lunch"
            }
        ]
    
    def test_create_ai_prompt_with_default_parameters(self):
        """Test that create_ai_prompt works with default parameters"""
        prompt = create_ai_prompt(self.sample_events, self.sample_events)
        
        # Should contain the basic structure
        assert "MEETING SCHEDULER AI ASSISTANT" in prompt
        assert "PHIL'S CALENDAR EVENTS:" in prompt
        assert "CHRIS'S CALENDAR EVENTS:" in prompt
        # Should contain a time range (now uses dynamic dates)
        assert "Time range:" in prompt
        
        # Should contain the events
        assert "Morning Standup" in prompt
        assert "Lunch with Sarah" in prompt
    
    def test_create_ai_prompt_with_custom_user_names(self):
        """Test that create_ai_prompt works with custom user names"""
        prompt = create_ai_prompt(self.sample_events, self.sample_events, "Alice", "Bob")
        
        # Should contain custom names
        assert "ALICE'S CALENDAR EVENTS:" in prompt
        assert "BOB'S CALENDAR EVENTS:" in prompt
        assert "Alice" in prompt
        assert "Bob" in prompt
        
        # Should not contain default names
        assert "PHIL'S CALENDAR EVENTS:" not in prompt
        assert "CHRIS'S CALENDAR EVENTS:" not in prompt
    
    def test_create_ai_prompt_with_time_range_parameters(self):
        """Test that create_ai_prompt accepts time range parameters"""
        start_date = datetime(2025, 1, 20)
        end_date = datetime(2025, 1, 27)
        
        prompt = create_ai_prompt(
            self.sample_events, 
            self.sample_events, 
            "Alice", 
            "Bob",
            start_date=start_date,
            end_date=end_date
        )
        
        # Should contain custom time range
        assert "2025-01-20 to 2025-01-27" in prompt
        assert "Next 2 weeks from today" not in prompt
        
        # Should still contain user names
        assert "ALICE'S CALENDAR EVENTS:" in prompt
        assert "BOB'S CALENDAR EVENTS:" in prompt
    
    def test_create_ai_prompt_with_start_date_only(self):
        """Test that create_ai_prompt works with start_date only"""
        start_date = datetime(2025, 2, 1)
        
        prompt = create_ai_prompt(
            self.sample_events, 
            self.sample_events, 
            "Alice", 
            "Bob",
            start_date=start_date
        )
        
        # Should contain start date and default end date (2 weeks later)
        assert "2025-02-01" in prompt
        assert "2025-02-15" in prompt  # 2 weeks later
    
    def test_create_ai_prompt_with_end_date_only(self):
        """Test that create_ai_prompt works with end_date only"""
        end_date = datetime(2025, 12, 31)  # Use a future date
        
        prompt = create_ai_prompt(
            self.sample_events, 
            self.sample_events, 
            "Alice", 
            "Bob",
            end_date=end_date
        )
        
        # Should contain end date and default start date (today)
        today = datetime.now().strftime('%Y-%m-%d')
        assert today in prompt
        assert "2025-12-31" in prompt
    
    def test_create_ai_prompt_time_range_validation(self):
        """Test that create_ai_prompt validates time range parameters"""
        # Test with end_date before start_date
        start_date = datetime(2025, 2, 15)
        end_date = datetime(2025, 2, 1)
        
        # Should raise ValueError or handle gracefully
        with pytest.raises(ValueError):
            create_ai_prompt(
                self.sample_events, 
                self.sample_events, 
                "Alice", 
                "Bob",
                start_date=start_date,
                end_date=end_date
            )
    
    def test_create_ai_prompt_metadata_time_range(self):
        """Test that the metadata section includes the correct time range"""
        start_date = datetime(2025, 1, 20)
        end_date = datetime(2025, 1, 27)
        
        prompt = create_ai_prompt(
            self.sample_events, 
            self.sample_events, 
            "Alice", 
            "Bob",
            start_date=start_date,
            end_date=end_date
        )
        
        # Should contain the time range in metadata section
        assert '"time_range_analyzed": "2025-01-20 to 2025-01-27"' in prompt
