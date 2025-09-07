#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for event links functionality
"""
import pytest
import json
from fastapi.testclient import TestClient
from src.api.server import app
from src.infrastructure.database import DatabaseManager
import os
import tempfile


@pytest.fixture
def test_db():
    """Create a temporary test database"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    db_manager = DatabaseManager(db_path)
    db_manager.initialize_database()
    
    # Add test users
    db_manager.create_user("phil", "primary", phone_number="+1234567890")
    db_manager.create_user("chris", "primary", phone_number="+1234567891")
    
    yield db_manager
    
    # Cleanup
    os.unlink(db_path)


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


def test_meeting_suggestions_include_event_links(client):
    """Test that meeting suggestions include clickable event creation links"""
    # Get meeting suggestions
    response = client.get("/meeting-suggestions?user1=phil&user2=chris&meeting_type=coffee")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check that suggestions exist
    assert "suggestions" in data
    assert len(data["suggestions"]) > 0
    
    # Check that each suggestion has event_link and event_id
    for suggestion in data["suggestions"]:
        assert "event_link" in suggestion
        assert "event_id" in suggestion
        assert suggestion["event_link"] is not None
        assert suggestion["event_id"] is not None
        
        # Check that event_link is a valid URL
        assert suggestion["event_link"].startswith("/calendar/events/create-from-suggestion/")
        assert suggestion["event_id"] in suggestion["event_link"]


def test_event_creation_from_suggestion_link(client):
    """Test creating calendar event from suggestion link"""
    # Test with invalid suggestion ID first
    response = client.post("/calendar/events/create-from-suggestion/999999")
    assert response.status_code == 404


def test_event_links_are_unique_per_suggestion(client):
    """Test that each suggestion has a unique event link"""
    response = client.get("/meeting-suggestions?user1=phil&user2=chris&meeting_type=coffee")
    assert response.status_code == 200
    
    data = response.json()
    suggestions = data["suggestions"]
    
    # Collect all event_ids and event_links
    event_ids = [s["event_id"] for s in suggestions]
    event_links = [s["event_link"] for s in suggestions]
    
    # Check uniqueness
    assert len(event_ids) == len(set(event_ids)), "Event IDs should be unique"
    assert len(event_links) == len(set(event_links)), "Event links should be unique"


def test_event_link_format_is_consistent(client):
    """Test that event links follow consistent format"""
    response = client.get("/meeting-suggestions?user1=phil&user2=chris&meeting_type=coffee")
    assert response.status_code == 200
    
    data = response.json()
    
    for suggestion in data["suggestions"]:
        event_link = suggestion["event_link"]
        event_id = suggestion["event_id"]
        
        # Check format: /calendar/events/create-from-suggestion/{event_id}
        expected_prefix = "/calendar/events/create-from-suggestion/"
        assert event_link.startswith(expected_prefix)
        
        # Check that event_id matches the one in the link
        link_event_id = event_link.replace(expected_prefix, "")
        assert link_event_id == event_id


def test_invalid_suggestion_id_returns_400(client):
    """Test that invalid suggestion ID returns 400"""
    response = client.post("/calendar/events/create-from-suggestion/invalid_id")
    assert response.status_code == 400  # Bad Request for invalid format
    
    # Test with valid format but non-existent ID
    response = client.post("/calendar/events/create-from-suggestion/999999")
    assert response.status_code == 404  # Not Found for non-existent ID
