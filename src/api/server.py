#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI server implementation
Clean Architecture: API layer delegates to core business logic
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, Any
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from api.models import MeetingSuggestionsResponse, ErrorResponse
from adapters.cli import get_meeting_suggestions_with_gemini
from core.meeting_scheduler import validate_meeting_suggestions
from adapters.gemini_client import parse_gemini_response


# Create FastAPI app
app = FastAPI(
    title="Meeting Scheduler API",
    description="AI-powered meeting scheduling service",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_meeting_suggestions_from_core(seed: int = 42) -> Optional[Dict[str, Any]]:
    """Get meeting suggestions from core business logic"""
    try:
        # Get AI response
        response_text = get_meeting_suggestions_with_gemini()
        if not response_text:
            return None
        
        # Parse the response
        suggestions = parse_gemini_response(response_text)
        if not suggestions:
            return None
        
        # Validate the suggestions
        is_valid, errors = validate_meeting_suggestions(suggestions)
        if not is_valid:
            print(f"Validation errors: {errors}")
            return None
        
        return suggestions
        
    except Exception as e:
        print(f"Error getting meeting suggestions: {e}")
        return None


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/meeting-suggestions", response_model=MeetingSuggestionsResponse)
async def get_meeting_suggestions(seed: int = 42):
    """Get AI-generated meeting suggestions"""
    try:
        suggestions = get_meeting_suggestions_from_core(seed=seed)
        
        if not suggestions:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate meeting suggestions"
            )
        
        return MeetingSuggestionsResponse(**suggestions)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/meeting-suggestions/raw")
async def get_raw_meeting_suggestions(seed: int = 42):
    """Get raw meeting suggestions without validation"""
    try:
        response_text = get_meeting_suggestions_with_gemini()
        if not response_text:
            raise HTTPException(
                status_code=500,
                detail="Failed to get AI response"
            )
        
        return {"raw_response": response_text}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
