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
    phil_energy: str = Field(..., description="Phil's energy level")
    chris_energy: str = Field(..., description="Chris's energy level")
    meeting_type: str = Field(..., description="Type of meeting")
    location: Optional[str] = Field(None, description="Suggested location")
    confidence: Optional[float] = Field(None, description="Confidence score 0.0-1.0")
    conflicts: Optional[List[str]] = Field(default_factory=list, description="Potential conflicts")
    preparation_time: Optional[str] = Field(None, description="Preparation time needed")


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
