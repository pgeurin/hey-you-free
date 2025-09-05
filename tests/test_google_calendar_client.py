#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test suite for Google Calendar client with window selection
"""
import pytest
from datetime import datetime, timedelta
from src.adapters.google_calendar_client import (
    DateWindow,
    create_date_window,
    create_custom_date_window,
    get_calendar_events_with_window,
    get_calendar_events_custom_window
)


def test_create_date_window():
    """Test creating date window relative to today"""
    window = create_date_window(days_back=7, days_forward=7)
    
    # Check it's a DateWindow instance
    assert isinstance(window, DateWindow)
    
    # Check dates are reasonable (within expected range)
    now = datetime.utcnow()
    assert abs((window.start_date - (now - timedelta(days=7))).total_seconds()) < 60
    assert abs((window.end_date - (now + timedelta(days=7))).total_seconds()) < 60


def test_create_custom_date_window():
    """Test creating custom date window from strings"""
    window = create_custom_date_window("2025-01-15", "2025-01-22")
    
    assert isinstance(window, DateWindow)
    assert window.start_date.date().isoformat() == "2025-01-15"
    assert window.end_date.date().isoformat() == "2025-01-22"


def test_create_custom_date_window_invalid_format():
    """Test custom date window with invalid date format"""
    with pytest.raises(ValueError):
        create_custom_date_window("invalid-date", "2025-01-22")


def test_date_window_to_iso_strings():
    """Test converting DateWindow to ISO strings"""
    window = DateWindow(
        start_date=datetime(2025, 1, 15, 10, 0, 0),
        end_date=datetime(2025, 1, 22, 18, 0, 0)
    )
    
    start_iso, end_iso = window.to_iso_strings()
    
    assert start_iso == "2025-01-15T10:00:00Z"
    assert end_iso == "2025-01-22T18:00:00Z"


def test_get_calendar_events_with_window_mocked():
    """Test calendar events function with mocked credentials"""
    # This test would require mocking the Google API calls
    # For now, just test the function exists and has correct signature
    assert callable(get_calendar_events_with_window)
    assert callable(get_calendar_events_custom_window)


def test_date_window_validation():
    """Test that date windows are created correctly"""
    # Test various window sizes
    window_1 = create_date_window(0, 1)  # Today to tomorrow
    window_2 = create_date_window(30, 30)  # Month back and forward
    
    assert window_1.end_date > window_1.start_date
    assert window_2.end_date > window_2.start_date
    
    # Test custom window
    custom_window = create_custom_date_window("2025-01-01", "2025-01-31")
    assert custom_window.start_date < custom_window.end_date


def test_edge_cases():
    """Test edge cases for date window creation"""
    # Same day window
    window = create_custom_date_window("2025-01-15", "2025-01-15")
    assert window.start_date.date() == window.end_date.date()
    
    # Single day window
    window = create_date_window(0, 0)
    assert window.start_date.date() == window.end_date.date()


if __name__ == "__main__":
    pytest.main([__file__])
