#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for updated format_events_for_ai function with user names
"""
import pytest
import sys
import os
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.meeting_scheduler import format_events_for_ai


class TestFormatEventsForAiUpdate:
    """Test updated format_events_for_ai function with user names"""
    
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
            },
            {
                "kind": "calendar#event",
                "summary": "Project Review",
                "start": {"dateTime": "2025-01-17T14:00:00Z"},
                "location": "Conference Room A",
                "description": "Weekly project review meeting"
            }
        ]
    
    def test_format_events_with_user_name(self):
        """Test that format_events_for_ai accepts and uses user name parameter"""
        result = format_events_for_ai(self.sample_events, "Alice")
        
        # Should contain the events
        assert "Morning Standup" in result
        assert "Lunch with Sarah" in result
        assert "Project Review" in result
        
        # Should contain proper formatting
        assert "Total events: 3" in result
        assert "2025-01-16 (Thursday) 09:00" in result
        assert "2025-01-16 (Thursday) 12:30" in result
        assert "2025-01-17 (Friday) 14:00" in result
    
    def test_format_events_with_different_user_names(self):
        """Test that function works with different user names"""
        result1 = format_events_for_ai(self.sample_events, "Bob")
        result2 = format_events_for_ai(self.sample_events, "Charlie")
        
        # Should produce different output due to different user names
        assert result1 != result2
        assert "Bob" in result1
        assert "Charlie" in result2
        assert "Total events: 3" in result1
        assert "Total events: 3" in result2
    
    def test_format_events_with_empty_list(self):
        """Test with empty events list"""
        result = format_events_for_ai([], "TestUser")
        
        assert "Total events: 0" in result
        assert len(result.strip()) > 0  # Should not be completely empty
    
    def test_format_events_with_invalid_events(self):
        """Test with events that have invalid date formats"""
        invalid_events = [
            {
                "summary": "Valid Event",
                "start": {"dateTime": "2025-01-16T09:00:00Z"},
                "location": "Office"
            },
            {
                "summary": "Invalid Event",
                "start": {"dateTime": "invalid-date"},
                "location": "Office"
            },
            {
                "summary": "Missing Start",
                "location": "Office"
            }
        ]
        
        result = format_events_for_ai(invalid_events, "TestUser")
        
        # Should only include the valid event
        assert "Valid Event" in result
        assert "Invalid Event" not in result
        assert "Missing Start" not in result
        assert "Total events: 1" in result
    
    def test_format_events_preserves_original_functionality(self):
        """Test that the function still works as before with name parameter"""
        # This ensures backward compatibility
        result = format_events_for_ai(self.sample_events, "phil")
        
        # Should work exactly like before
        assert "Total events: 3" in result
        assert "Morning Standup" in result
        assert "Lunch with Sarah" in result
        assert "Project Review" in result


def test_run_format_events_update_tests():
    """Run all format_events_for_ai update tests"""
    print("🧪 Testing format_events_for_ai function updates...")
    
    test_instance = TestFormatEventsForAiUpdate()
    test_instance.setup_method()
    
    # Run all test methods
    test_instance.test_format_events_with_user_name()
    print("✅ User name parameter test passed")
    
    test_instance.test_format_events_with_different_user_names()
    print("✅ Different user names test passed")
    
    test_instance.test_format_events_with_empty_list()
    print("✅ Empty list test passed")
    
    test_instance.test_format_events_with_invalid_events()
    print("✅ Invalid events test passed")
    
    test_instance.test_format_events_preserves_original_functionality()
    print("✅ Backward compatibility test passed")
    
    print("🎉 All format_events_for_ai update tests passed!")


if __name__ == "__main__":
    test_run_format_events_update_tests()
