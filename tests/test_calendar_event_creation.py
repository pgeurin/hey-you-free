#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for calendar event creation functionality
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from src.adapters.google_calendar_client import (
    create_calendar_event,
    check_calendar_conflicts,
    load_google_credentials,
    create_event_from_meeting_suggestion,
    parse_duration_to_hours,
    create_events_for_both_users
)


class TestCalendarEventCreation:
    """Test calendar event creation functionality"""
    
    def test_create_calendar_event_success(self):
        """Test successful calendar event creation"""
        # Mock credentials and service
        mock_creds = Mock()
        mock_service = Mock()
        mock_event = {
            'id': 'test_event_123',
            'summary': 'Test Meeting',
            'start': {'dateTime': '2024-01-15T10:00:00Z'},
            'end': {'dateTime': '2024-01-15T11:00:00Z'}
        }
        
        mock_service.events().insert().execute.return_value = mock_event
        
        with patch('src.adapters.google_calendar_client.load_google_credentials', return_value=mock_creds), \
             patch('googleapiclient.discovery.build', return_value=mock_service):
            
            result = create_calendar_event(
                summary='Test Meeting',
                start_time='2024-01-15T10:00:00Z',
                end_time='2024-01-15T11:00:00Z',
                description='Test description',
                location='Test location',
                attendees=['user1@example.com', 'user2@example.com']
            )
            
            assert result == mock_event
            # Check that insert was called with correct parameters
            mock_service.events().insert.assert_called_with(
                calendarId='primary',
                body={
                    'summary': 'Test Meeting',
                    'start': {'dateTime': '2024-01-15T10:00:00Z', 'timeZone': 'UTC'},
                    'end': {'dateTime': '2024-01-15T11:00:00Z', 'timeZone': 'UTC'},
                    'description': 'Test description',
                    'location': 'Test location',
                    'attendees': [{'email': 'user1@example.com'}, {'email': 'user2@example.com'}]
                }
            )
    
    def test_create_calendar_event_no_credentials(self):
        """Test event creation fails when no credentials available"""
        with patch('src.adapters.google_calendar_client.load_google_credentials', return_value=None):
            result = create_calendar_event(
                summary='Test Meeting',
                start_time='2024-01-15T10:00:00Z',
                end_time='2024-01-15T11:00:00Z'
            )
            
            assert result is None


class TestMeetingSuggestionIntegration:
    """Test creating events from meeting suggestions"""
    
    def test_parse_duration_to_hours(self):
        """Test duration parsing"""
        assert parse_duration_to_hours("1 hour") == 1.0
        assert parse_duration_to_hours("1.5 hours") == 1.5
        assert parse_duration_to_hours("2 hours") == 2.0
        assert parse_duration_to_hours("30 minutes") == 30.0  # This will extract 30
        assert parse_duration_to_hours("invalid") == 1.0  # Default fallback
    
    def test_create_event_from_meeting_suggestion(self):
        """Test creating event from meeting suggestion"""
        mock_creds = Mock()
        mock_service = Mock()
        mock_event = {'id': 'suggestion_event_123'}
        
        mock_service.events().insert().execute.return_value = mock_event
        
        suggestion = {
            'date': '2024-01-15',
            'time': '14:00',
            'duration': '1.5 hours',
            'meeting_type': 'Coffee Chat',
            'reasoning': 'Good afternoon slot',
            'location': 'Downtown Coffee Shop'
        }
        
        with patch('src.adapters.google_calendar_client.load_google_credentials', return_value=mock_creds), \
             patch('googleapiclient.discovery.build', return_value=mock_service):
            
            result = create_event_from_meeting_suggestion(
                suggestion, 'user1@example.com', 'user2@example.com'
            )
            
            assert result == mock_event
            
            # Check that the event was created with correct parameters
            call_args = mock_service.events().insert.call_args
            event_data = call_args[1]['body']
            
            assert event_data['summary'] == 'Coffee Chat'
            assert event_data['description'] == 'Good afternoon slot'
            assert event_data['location'] == 'Downtown Coffee Shop'
            assert len(event_data['attendees']) == 2
            assert event_data['attendees'][0]['email'] == 'user1@example.com'
            assert event_data['attendees'][1]['email'] == 'user2@example.com'
            
            # Check time formatting
            assert event_data['start']['dateTime'] == '2024-01-15T14:00:00Z'
            assert event_data['end']['dateTime'] == '2024-01-15T15:30:00Z'  # 1.5 hours later
    
    def test_create_events_for_both_users_success(self):
        """Test creating events for both users successfully"""
        mock_creds = Mock()
        mock_service = Mock()
        mock_event = {'id': 'event_123'}
        
        mock_service.events().insert().execute.return_value = mock_event
        
        suggestion = {
            'date': '2024-01-15',
            'time': '10:00',
            'duration': '1 hour',
            'meeting_type': 'Work Meeting',
            'reasoning': 'Morning slot available'
        }
        
        with patch('src.adapters.google_calendar_client.load_google_credentials', return_value=mock_creds), \
             patch('googleapiclient.discovery.build', return_value=mock_service):
            
            result = create_events_for_both_users(
                suggestion, 'user1@example.com', 'user2@example.com'
            )
            
            assert result['success'] is True
            assert result['user1_event'] == mock_event
            assert result['user2_event'] == mock_event
            assert len(result['errors']) == 0
    
    def test_create_events_for_both_users_failure(self):
        """Test handling failure when creating events for both users"""
        with patch('src.adapters.google_calendar_client.load_google_credentials', return_value=None):
            suggestion = {
                'date': '2024-01-15',
                'time': '10:00',
                'duration': '1 hour',
                'meeting_type': 'Work Meeting'
            }
            
            result = create_events_for_both_users(
                suggestion, 'user1@example.com', 'user2@example.com'
            )
            
            assert result['success'] is False
            assert result['user1_event'] is None
            assert result['user2_event'] is None
            assert len(result['errors']) > 0


if __name__ == "__main__":
    pytest.main([__file__])