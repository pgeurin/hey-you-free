#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for share button functionality
"""
import pytest
import json
from fastapi.testclient import TestClient
from src.api.server import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


def test_meeting_suggestions_include_share_links(client):
    """Test that meeting suggestions include share links"""
    # Get meeting suggestions
    response = client.get("/meeting-suggestions?user1=phil&user2=chris&meeting_type=coffee")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check that suggestions exist
    assert "suggestions" in data
    assert len(data["suggestions"]) > 0
    
    # Check that each suggestion has share_link
    for suggestion in data["suggestions"]:
        assert "share_link" in suggestion
        assert suggestion["share_link"] is not None
        
        # Check that share_link is a valid URL
        assert suggestion["share_link"].startswith("/share/event/")
        assert suggestion["event_id"] in suggestion["share_link"]


def test_share_links_are_unique_per_suggestion(client):
    """Test that each suggestion has a unique share link"""
    response = client.get("/meeting-suggestions?user1=phil&user2=chris&meeting_type=coffee")
    assert response.status_code == 200
    
    data = response.json()
    suggestions = data["suggestions"]
    
    # Collect all share_links
    share_links = [s["share_link"] for s in suggestions]
    
    # Check uniqueness
    assert len(share_links) == len(set(share_links)), "Share links should be unique"


def test_share_link_format_is_consistent(client):
    """Test that share links follow consistent format"""
    response = client.get("/meeting-suggestions?user1=phil&user2=chris&meeting_type=coffee")
    assert response.status_code == 200
    
    data = response.json()
    
    for suggestion in data["suggestions"]:
        share_link = suggestion["share_link"]
        event_id = suggestion["event_id"]
        
        # Check format: /share/event/{event_id}
        expected_prefix = "/share/event/"
        assert share_link.startswith(expected_prefix)
        
        # Check that event_id matches the one in the link
        link_event_id = share_link.replace(expected_prefix, "")
        assert link_event_id == event_id


def test_share_endpoint_returns_event_details(client):
    """Test that share endpoint returns event details"""
    # Test with invalid suggestion ID first (should return 400 for invalid format)
    response = client.get("/share/event/invalid_id")
    assert response.status_code == 400  # Bad Request for invalid format
    
    # Test with valid format but non-existent ID
    response = client.get("/share/event/999999")
    assert response.status_code == 404  # Not Found for non-existent ID


def test_invalid_share_link_returns_400(client):
    """Test that invalid share link returns 400"""
    response = client.get("/share/event/invalid_id")
    assert response.status_code == 400  # Bad Request for invalid format
