#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Event link generation utilities
Clean Architecture: Business logic for generating event links
"""
import hashlib
from typing import List, Dict, Any


def generate_suggestion_id(date: str, time: str, user1: str, user2: str) -> str:
    """Generate unique ID for a suggestion"""
    # Create hash from date, time, and users for uniqueness
    content = f"{date}_{time}_{user1}_{user2}"
    hash_obj = hashlib.md5(content.encode())
    return f"suggestion_{hash_obj.hexdigest()[:8]}"


def generate_event_creation_link(suggestion_id: str, base_url: str = "") -> str:
    """Generate a unique link for creating an event from a suggestion"""
    return f"{base_url}/calendar/events/create-from-suggestion/{suggestion_id}"


def add_event_links_to_suggestions(suggestions: List[Dict[str, Any]], 
                                 user1_name: str, 
                                 user2_name: str, 
                                 base_url: str = "") -> List[Dict[str, Any]]:
    """Add event creation links to each suggestion"""
    enhanced_suggestions = []
    
    for suggestion in suggestions:
        # Create a copy to avoid modifying original
        enhanced_suggestion = suggestion.copy()
        
        # Generate unique ID for this suggestion
        suggestion_id = generate_suggestion_id(
            suggestion['date'], 
            suggestion['time'], 
            user1_name, 
            user2_name
        )
        
        # Add event_id and event_link
        enhanced_suggestion['event_id'] = suggestion_id
        enhanced_suggestion['event_link'] = generate_event_creation_link(suggestion_id, base_url)
        
        enhanced_suggestions.append(enhanced_suggestion)
    
    return enhanced_suggestions
