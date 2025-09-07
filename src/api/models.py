#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pydantic models for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class MeetingSuggestion(BaseModel):
    """Individual meeting suggestion model"""
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    time: str = Field(..., description="Time in HH:MM format")
    duration: str = Field(..., description="Duration in human-readable format")
    reasoning: str = Field(..., description="Why this time works well")
    meeting_type: str = Field(..., description="Type of meeting")
    user_energies: Dict[str, str] = Field(..., description="Energy levels for each user (e.g., {'phil': 'High', 'chris': 'Medium'})")
    location: Optional[str] = Field(None, description="Suggested location")
    confidence: Optional[float] = Field(None, description="Confidence score 0.0-1.0")
    conflicts: Optional[List[str]] = Field(default_factory=list, description="Potential conflicts")
    preparation_time: Optional[str] = Field(None, description="Preparation time needed")
    event_id: Optional[str] = Field(None, description="Unique identifier for this suggestion")
    event_link: Optional[str] = Field(None, description="Direct link to create this event")
    share_link: Optional[str] = Field(None, description="Link to share this event with others")
    
    class Config:
        extra = "allow"  # Allow additional fields


# MeetingSuggestion model is now defined above with user_energies dictionary


class MeetingSuggestionsResponse(BaseModel):
    """Complete meeting suggestions response"""
    suggestions: List[MeetingSuggestion] = Field(..., description="List of meeting suggestions")
    metadata: Dict[str, Any] = Field(..., description="Response metadata")


class CalendarEventsRequest(BaseModel):
    """Request model for calendar events"""
    user1_name: str = Field(..., description="Name of first user")
    user2_name: str = Field(..., description="Name of second user")
    seed: Optional[int] = Field(42, description="Seed for deterministic results")


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")


# User Management Models
class UserCreate(BaseModel):
    """User creation request model"""
    name: str = Field(..., description="User name", min_length=1, max_length=100)
    phone_number: Optional[str] = Field(None, description="Phone number")
    email: Optional[str] = Field(None, description="Email address")
    calendar_id: str = Field(..., description="Google Calendar ID", min_length=1)
    oauth_token: Optional[str] = Field(None, description="OAuth access token")
    refresh_token: Optional[str] = Field(None, description="OAuth refresh token")
    timezone: Optional[str] = Field("America/Los_Angeles", description="User timezone")


class UserUpdate(BaseModel):
    """User update request model"""
    name: Optional[str] = Field(None, description="User name", min_length=1, max_length=100)
    phone_number: Optional[str] = Field(None, description="Phone number")
    email: Optional[str] = Field(None, description="Email address")
    calendar_id: Optional[str] = Field(None, description="Google Calendar ID", min_length=1)
    oauth_token: Optional[str] = Field(None, description="OAuth access token")
    refresh_token: Optional[str] = Field(None, description="OAuth refresh token")
    timezone: Optional[str] = Field(None, description="User timezone")
    is_active: Optional[bool] = Field(None, description="User active status")


class UserResponse(BaseModel):
    """User response model"""
    id: int = Field(..., description="User ID")
    name: str = Field(..., description="User name")
    phone_number: Optional[str] = Field(None, description="Phone number")
    email: Optional[str] = Field(None, description="Email address")
    calendar_id: str = Field(..., description="Google Calendar ID")
    timezone: str = Field(..., description="User timezone")
    is_active: bool = Field(..., description="User active status")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")


# Meeting Suggestions with User Names
class MeetingSuggestionsRequest(BaseModel):
    """Meeting suggestions request with user names"""
    user1_name: str = Field(..., description="Name of first user")
    user2_name: str = Field(..., description="Name of second user")
    time_range_days: Optional[int] = Field(14, description="Number of days to analyze", ge=1, le=90)
    start_date: Optional[str] = Field(None, description="Start date in YYYY-MM-DD format")
    end_date: Optional[str] = Field(None, description="End date in YYYY-MM-DD format")
    conversation_context: Optional[str] = Field(None, description="Additional context for AI")
    description: Optional[str] = Field(None, description="Custom description for the meeting")
    seed: Optional[int] = Field(42, description="Seed for deterministic results")


# Text Chat Models
class TextChatRequest(BaseModel):
    """Text chat request model"""
    user1_name: str = Field(..., description="Name of first user")
    user2_name: str = Field(..., description="Name of second user")
    message: str = Field(..., description="Message text", min_length=1)
    script_context: Optional[str] = Field(None, description="Script context for AI")


class TextChatResponse(BaseModel):
    """Text chat response model"""
    response: str = Field(..., description="AI response text")
    suggestions_generated: bool = Field(..., description="Whether meeting suggestions were generated")
    conversation_id: Optional[int] = Field(None, description="Conversation ID if created")


# Conversation Context Models
class ConversationContextResponse(BaseModel):
    """Conversation context response model"""
    context_text: str = Field(..., description="Context text")
    context_type: str = Field(..., description="Type of context")
    created_at: str = Field(..., description="Creation timestamp")
    expires_at: Optional[str] = Field(None, description="Expiration timestamp")


# Calendar Event Models
class CalendarEventRequest(BaseModel):
    """Request model for creating calendar events"""
    summary: str
    start: str  # ISO datetime string
    end: str    # ISO datetime string
    description: Optional[str] = None
    location: Optional[str] = None
    attendees: Optional[List[str]] = None
    calendar_id: str = "primary"


class CalendarEventFromSuggestionRequest(BaseModel):
    """Request model for creating calendar events from meeting suggestions"""
    date: str
    time: str
    duration: str
    summary: str
    description: Optional[str] = None
    location: Optional[str] = None
    attendees: Optional[List[str]] = None
    meeting_type: Optional[str] = None


class CalendarEventResponse(BaseModel):
    """Response model for calendar event creation"""
    success: bool
    event_id: Optional[str] = None
    event_url: Optional[str] = None
    message: str
    conflicts: Optional[List[Dict[str, Any]]] = None


class CalendarConflictRequest(BaseModel):
    """Request model for checking calendar conflicts"""
    date: str
    time: str
    duration: int  # minutes
    calendar_id: str = "primary"


class CalendarConflictResponse(BaseModel):
    """Response model for calendar conflict check"""
    has_conflicts: bool
    conflicts: List[Dict[str, Any]]
    message: str


class CalendarEventUpdateRequest(BaseModel):
    """Request model for updating calendar events"""
    summary: Optional[str] = None
    start: Optional[str] = None  # ISO datetime string
    end: Optional[str] = None    # ISO datetime string
    description: Optional[str] = None
    location: Optional[str] = None
    attendees: Optional[List[str]] = None


class CalendarEventModifyTimeRequest(BaseModel):
    """Request model for modifying event time"""
    new_start_time: str  # ISO datetime string
    new_end_time: str    # ISO datetime string


class CalendarEventCancelRequest(BaseModel):
    """Request model for cancelling events"""
    cancellation_reason: str = "Event cancelled"


class CalendarEventUpdateResponse(BaseModel):
    """Response model for calendar event updates"""
    success: bool
    event_id: Optional[str] = None
    message: str
    updated_event: Optional[Dict[str, Any]] = None
