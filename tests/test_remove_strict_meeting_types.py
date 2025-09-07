"""
Test that meeting type validation is relaxed for AI flexibility
"""
import pytest
from src.core.meeting_scheduler import validate_event_dictionary


class TestRelaxedMeetingTypes:
    """Test that meeting type validation allows AI creativity"""
    
    def test_ai_can_suggest_creative_meeting_types(self):
        """Test that AI can suggest creative meeting types without strict validation"""
        # Test various creative meeting types that should be allowed
        creative_types = [
            "virtual coffee chat",
            "walking meeting in the park", 
            "lunch at that new sushi place",
            "quick 15-minute sync",
            "team building activity",
            "brainstorming session",
            "one-on-one check-in",
            "project planning meeting",
            "casual catch-up",
            "networking event"
        ]
        
        for meeting_type in creative_types:
            event = {
                "date": "2025-01-20",
                "time": "14:30",
                "duration": "1 hour",
                "reasoning": "AI suggested creative meeting type",
                "user_energies": {
                    "phil": "High",
                    "chris": "Medium"
                },
                "meeting_type": meeting_type
            }
            
            is_valid, errors = validate_event_dictionary(event)
            assert is_valid, f"Meeting type '{meeting_type}' should be valid: {errors}"
    
    def test_meeting_type_validation_is_relaxed(self):
        """Test that meeting type validation doesn't enforce strict categories"""
        # Test that any reasonable meeting type is accepted
        flexible_types = [
            "coffee",
            "lunch", 
            "dinner",
            "meeting",
            "call",
            "chat",
            "activity",
            "social",
            "work session",
            "planning",
            "review",
            "discussion"
        ]
        
        for meeting_type in flexible_types:
            event = {
                "date": "2025-01-20",
                "time": "14:30",
                "duration": "1 hour",
                "reasoning": "Flexible meeting type test",
                "user_energies": {
                    "phil": "High",
                    "chris": "High"
                },
                "meeting_type": meeting_type
            }
            
            is_valid, errors = validate_event_dictionary(event)
            assert is_valid, f"Meeting type '{meeting_type}' should be valid: {errors}"
    
    def test_empty_meeting_type_still_invalid(self):
        """Test that empty meeting type is still invalid (required field)"""
        event = {
            "date": "2025-01-20",
            "time": "14:30",
            "duration": "1 hour",
            "reasoning": "Test empty meeting type",
            "user_energies": {
                "phil": "High",
                "chris": "High"
            },
            "meeting_type": ""  # Empty should still be invalid
        }
        
        is_valid, errors = validate_event_dictionary(event)
        assert not is_valid
        assert any("Empty required field: meeting_type" in error for error in errors)


def test_run_relaxed_meeting_types_tests():
    """Run all relaxed meeting type tests"""
    test_instance = TestRelaxedMeetingTypes()
    test_instance.test_ai_can_suggest_creative_meeting_types()
    test_instance.test_meeting_type_validation_is_relaxed()
    test_instance.test_empty_meeting_type_still_invalid()
    return True
