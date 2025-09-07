#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core chat processing logic for meeting coordination
Clean Architecture: Pure business logic, no I/O dependencies
"""
import re
import html
from typing import Dict, List, Optional, Any
from datetime import datetime


def validate_chat_message(message: str) -> Dict[str, Any]:
    """Validate and sanitize chat message"""
    if not message or not message.strip():
        return {
            'is_valid': False,
            'error': 'Message is empty',
            'sanitized_message': ''
        }
    
    if len(message) > 1000:
        return {
            'is_valid': False,
            'error': 'Message is too long (max 1000 characters)',
            'sanitized_message': message[:1000]
        }
    
    # Sanitize HTML and special characters
    sanitized = html.escape(message.strip())
    
    return {
        'is_valid': True,
        'error': None,
        'sanitized_message': sanitized
    }


def extract_meeting_keywords(message: str) -> Dict[str, Any]:
    """Extract meeting-related keywords and time mentions"""
    message_lower = message.lower()
    
    # Meeting keywords
    meeting_keywords = [
        'meet', 'meeting', 'coffee', 'lunch', 'dinner', 'call', 'chat',
        'discuss', 'talk', 'catch up', 'grab', 'get together'
    ]
    
    # Time keywords
    time_keywords = [
        'today', 'tomorrow', 'yesterday', 'morning', 'afternoon', 'evening',
        'night', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday',
        'saturday', 'sunday', 'week', 'month'
    ]
    
    found_keywords = [kw for kw in meeting_keywords if kw in message_lower]
    found_time_keywords = [kw for kw in time_keywords if kw in message_lower]
    all_keywords = found_keywords + found_time_keywords
    
    # Time patterns
    time_patterns = [
        r'\b\d{1,2}:\d{2}\s*(am|pm)?\b',  # 14:00, 2:30pm, etc.
        r'\b\d{1,2}(am|pm)\b',  # 2pm, 10am, etc.
        r'\b(morning|afternoon|evening|night)\b',
        r'\b(today|tomorrow|yesterday)\b',
        r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
        r'\b(this week|next week|this month|next month)\b'
    ]
    
    time_mentions = []
    for pattern in time_patterns:
        # Use finditer to get full matches instead of groups
        for match in re.finditer(pattern, message_lower):
            time_mentions.append(match.group(0))
    
    return {
        'keywords': all_keywords,
        'time_mentions': time_mentions,
        'has_time_reference': len(time_mentions) > 0
    }


def detect_meeting_intent(message: str) -> Dict[str, Any]:
    """Detect if message contains meeting-related intent"""
    keywords = extract_meeting_keywords(message)
    message_lower = message.lower()
    
    # Strong meeting indicators
    strong_indicators = [
        'meet', 'meeting', 'coffee', 'lunch', 'dinner', 'call',
        'schedule', 'calendar', 'appointment'
    ]
    
    # Time indicators
    time_indicators = [
        'when', 'what time', 'tomorrow', 'today', 'this week',
        'next week', 'monday', 'tuesday', 'wednesday', 'thursday',
        'friday', 'saturday', 'sunday'
    ]
    
    has_strong_intent = any(indicator in message_lower for indicator in strong_indicators)
    has_time_intent = any(indicator in message_lower for indicator in time_indicators)
    
    if has_strong_intent and has_time_intent:
        intent_type = 'meeting_request'
    elif has_strong_intent:
        intent_type = 'meeting_mention'
    elif has_time_intent:
        intent_type = 'time_suggestion'
    else:
        intent_type = 'casual'
    
    return {
        'has_meeting_intent': has_strong_intent or has_time_intent,
        'intent_type': intent_type,
        'confidence': 0.8 if has_strong_intent else 0.4
    }


def parse_chat_message(message: str) -> Dict[str, Any]:
    """Parse and analyze chat message"""
    validation = validate_chat_message(message)
    if not validation['is_valid']:
        return validation
    
    keywords = extract_meeting_keywords(validation['sanitized_message'])
    intent = detect_meeting_intent(validation['sanitized_message'])
    
    # Determine message type
    if intent['has_meeting_intent']:
        if intent['intent_type'] == 'meeting_request':
            message_type = 'meeting_request'
        elif intent['intent_type'] == 'time_suggestion':
            message_type = 'time_suggestion'
        else:
            message_type = 'meeting_mention'
    else:
        message_type = 'casual'
    
    return {
        'is_valid': True,
        'message_type': message_type,
        'keywords': keywords['keywords'],
        'time_mentions': keywords['time_mentions'],
        'intent': intent,
        'sanitized_message': validation['sanitized_message']
    }


def manage_conversation_context(
    user1_name: str, 
    user2_name: str, 
    message: str, 
    existing_conversation_id: Optional[int] = None
) -> Dict[str, Any]:
    """Manage conversation context and history"""
    parsed = parse_chat_message(message)
    
    if not parsed['is_valid']:
        return {
            'conversation_id': existing_conversation_id,
            'context_updated': False,
            'error': parsed['error']
        }
    
    # Create context summary
    context_parts = []
    if parsed['keywords']:
        context_parts.append(f"Keywords: {', '.join(parsed['keywords'])}")
    if parsed['time_mentions']:
        context_parts.append(f"Time mentions: {', '.join(parsed['time_mentions'])}")
    if parsed['intent']['has_meeting_intent']:
        context_parts.append(f"Intent: {parsed['intent']['intent_type']}")
    
    context_summary = "; ".join(context_parts) if context_parts else "General conversation"
    
    # For now, simulate conversation ID generation
    # In real implementation, this would interact with database
    conversation_id = existing_conversation_id or hash(f"{user1_name}_{user2_name}_{datetime.now().isoformat()}")
    
    return {
        'conversation_id': conversation_id,
        'context_updated': True,
        'context_summary': context_summary,
        'message_analysis': parsed
    }


def apply_script_template(
    template_name: str, 
    user1_name: str, 
    user2_name: str, 
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """Apply script-based response template"""
    templates = {
        'coffee_invitation': {
            'response': f"Hi {user2_name}! I'd love to grab coffee with you. Let me check our calendars and suggest some good times.",
            'action': 'generate_meeting_suggestions',
            'template_applied': True
        },
        'meeting_confirmation': {
            'response': f"Perfect! I'll send you a calendar invite for that time.",
            'action': 'create_calendar_event',
            'template_applied': True
        },
        'time_suggestion': {
            'response': f"Thanks for the suggestion! Let me check if that works with both our schedules.",
            'action': 'check_availability',
            'template_applied': True
        },
        'casual_response': {
            'response': f"Hi {user2_name}! How are you doing?",
            'action': 'continue_conversation',
            'template_applied': True
        }
    }
    
    template = templates.get(template_name, templates['casual_response'])
    return template


def generate_chat_response(
    message: str,
    user1_name: str,
    user2_name: str,
    conversation_context: Optional[str] = None
) -> Dict[str, Any]:
    """Generate AI response for chat message"""
    parsed = parse_chat_message(message)
    
    if not parsed['is_valid']:
        return {
            'response': "I didn't understand that message. Could you try again?",
            'suggestions_generated': False,
            'conversation_id': None,
            'error': parsed['error']
        }
    
    # Manage conversation context
    context = manage_conversation_context(user1_name, user2_name, message)
    
    # Determine response strategy
    if parsed['message_type'] == 'meeting_request':
        template = apply_script_template('coffee_invitation', user1_name, user2_name, {})
        suggestions_generated = True
    elif parsed['message_type'] == 'time_suggestion':
        template = apply_script_template('time_suggestion', user1_name, user2_name, {})
        suggestions_generated = True
    elif parsed['message_type'] == 'meeting_mention':
        template = apply_script_template('meeting_confirmation', user1_name, user2_name, {})
        suggestions_generated = False
    else:
        template = apply_script_template('casual_response', user1_name, user2_name, {})
        suggestions_generated = False
    
    return {
        'response': template['response'],
        'suggestions_generated': suggestions_generated,
        'conversation_id': context['conversation_id'],
        'template_used': template.get('action', 'continue_conversation')
    }


def generate_meeting_suggestions_from_chat(
    user1_name: str,
    user2_name: str,
    message: str,
    conversation_context: Optional[str] = None
) -> Dict[str, Any]:
    """Generate meeting suggestions based on chat context"""
    parsed = parse_chat_message(message)
    
    if not parsed['is_valid'] or not parsed['intent']['has_meeting_intent']:
        return {
            'suggestions': [],
            'suggestions_generated': False,
            'conversation_id': None,
            'error': 'No meeting intent detected'
        }
    
    # For now, return mock suggestions
    # In real implementation, this would call the meeting scheduler
    mock_suggestions = [
        {
            'date': '2025-01-16',
            'time': '14:00',
            'duration': '1 hour',
            'reasoning': 'Good afternoon slot, both users typically free',
            'meeting_type': 'Coffee meeting',
            'location': 'Downtown Coffee Shop'
        },
        {
            'date': '2025-01-17',
            'time': '10:00',
            'duration': '1 hour',
            'reasoning': 'Morning slot, fresh start to the day',
            'meeting_type': 'Coffee meeting',
            'location': 'Downtown Coffee Shop'
        }
    ]
    
    context = manage_conversation_context(user1_name, user2_name, message)
    
    return {
        'suggestions': mock_suggestions,
        'suggestions_generated': True,
        'conversation_id': context['conversation_id'],
        'context_used': conversation_context
    }
