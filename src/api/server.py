#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI server implementation
Clean Architecture: API layer delegates to core business logic
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, Any, List
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from api.models import (
    MeetingSuggestionsResponse, ErrorResponse, UserCreate, UserUpdate, 
    UserResponse, MeetingSuggestionsRequest, TextChatRequest, TextChatResponse,
    ConversationContextResponse
)
from adapters.cli import get_meeting_suggestions_with_gemini
from core.meeting_scheduler import validate_meeting_suggestions
from adapters.gemini_client import parse_gemini_response
from infrastructure.environment import (
    validate_environment,
    get_api_key_status,
    load_environment_config
)
from infrastructure.database import DatabaseManager
from api.user_management import UserManager


# Validate environment on startup
def check_startup_requirements():
    """Check if all startup requirements are met"""
    is_valid, errors = validate_environment()
    api_status = get_api_key_status()
    
    if not is_valid:
        print("❌ Environment validation failed:")
        for error in errors:
            print(f"   • {error}")
        print("\n💡 Run 'python setup_environment.py' to fix these issues")
        return False
    
    if not api_status['available']:
        print(f"❌ API Key issue: {api_status['message']}")
        print("💡 Get your API key from: https://makersuite.google.com/app/apikey")
        print("💡 Run 'python setup_environment.py' to configure it")
        return False
    
    print("✅ Environment validation passed")
    print(f"🔑 API Key: {api_status['status']} ({api_status['key_length']} chars)")
    return True

# Check startup requirements
if not check_startup_requirements():
    print("\n⚠️  Server will start but some features may not work properly")
    print("💡 Run 'python setup_environment.py' to fix environment issues")

# Global database and user manager instances
db_manager = None
user_manager = None

def get_db_manager():
    """Get database manager instance, initializing if needed"""
    global db_manager
    db_path = os.getenv("DATABASE_PATH", "meeting_scheduler.db")
    if db_manager is None or db_manager.db_path != db_path:
        db_manager = DatabaseManager(db_path)
        db_manager.initialize_database()
    return db_manager

def get_user_manager():
    """Get user manager instance, initializing if needed"""
    global user_manager
    if user_manager is None:
        user_manager = UserManager(get_db_manager())
    return user_manager

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


def get_meeting_suggestions_from_core(seed: int = 42, **kwargs) -> Optional[Dict[str, Any]]:
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


def handle_text_chat_from_core(user1_name: str, user2_name: str, message: str, script_context: Optional[str] = None) -> Dict[str, Any]:
    """Handle text chat from core business logic"""
    try:
        # For now, return a simple response
        # TODO: Implement actual AI chat functionality
        response_text = f"AI Response to: {message}"
        
        return {
            "response": response_text,
            "suggestions_generated": False,
            "conversation_id": None
        }
        
    except Exception as e:
        print(f"Error handling text chat: {e}")
        return {
            "response": "Sorry, I encountered an error processing your message.",
            "suggestions_generated": False,
            "conversation_id": None
        }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/meeting-suggestions", response_model=MeetingSuggestionsResponse)
async def get_meeting_suggestions(seed: int = 42):
    """Get AI-generated meeting suggestions"""
    try:
        # Check API key availability first
        api_status = get_api_key_status()
        if not api_status['available']:
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "API key not configured",
                    "message": api_status['message'],
                    "help": "Run 'python setup_environment.py' to configure your API key"
                }
            )
        
        suggestions = get_meeting_suggestions_from_core(seed=seed)
        
        if not suggestions:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Failed to generate meeting suggestions",
                    "message": "AI service returned no suggestions",
                    "help": "Check your API key and try again"
                }
            )
        
        return MeetingSuggestionsResponse(**suggestions)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": str(e),
                "help": "Check server logs for more details"
            }
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


# User Management Endpoints
@app.get("/users", response_model=List[UserResponse])
async def get_users():
    """Get all users"""
    try:
        users = get_user_manager().list_all_users(active_only=False)
        return [UserResponse(**user) for user in users]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/users/{name}", response_model=UserResponse)
async def get_user_by_name(name: str):
    """Get user by name"""
    try:
        user = get_user_manager().get_user_by_name(name)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserResponse(**user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/users", response_model=UserResponse, status_code=201)
async def create_user(user_data: UserCreate):
    """Create a new user"""
    try:
        user_id = get_user_manager().create_user(user_data.model_dump())
        user = get_user_manager().get_user_by_id(user_id)
        return UserResponse(**user)
    except Exception as e:
        if "already exists" in str(e):
            raise HTTPException(status_code=400, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/users/{name}", response_model=UserResponse)
async def update_user(name: str, user_data: UserUpdate):
    """Update user by name"""
    try:
        user = get_user_manager().get_user_by_name(name)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update user
        update_dict = {k: v for k, v in user_data.model_dump().items() if v is not None}
        if update_dict:
            get_user_manager().update_user(user['id'], update_dict)
        
        # Return updated user
        updated_user = get_user_manager().get_user_by_id(user['id'])
        return UserResponse(**updated_user)
    except HTTPException:
        raise
    except Exception as e:
        if "already exists" in str(e):
            raise HTTPException(status_code=400, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/users/{name}")
async def delete_user(name: str):
    """Delete user by name"""
    try:
        user = get_user_manager().get_user_by_name(name)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        success = get_user_manager().delete_user(user['id'])
        if success:
            return {"message": "User deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete user")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Enhanced Meeting Suggestions Endpoints
@app.post("/meeting-suggestions", response_model=MeetingSuggestionsResponse)
async def get_meeting_suggestions_with_users(request: MeetingSuggestionsRequest):
    """Get meeting suggestions with user names and flexible parameters"""
    try:
        # Check API key availability first
        api_status = get_api_key_status()
        if not api_status['available']:
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "API key not configured",
                    "message": api_status['message'],
                    "help": "Run 'python setup_environment.py' to configure your API key"
                }
            )
        
        # Get user information
        user1 = get_user_manager().get_user_by_name(request.user1_name)
        user2 = get_user_manager().get_user_by_name(request.user2_name)
        
        if not user1:
            raise HTTPException(status_code=404, detail=f"User '{request.user1_name}' not found")
        if not user2:
            raise HTTPException(status_code=404, detail=f"User '{request.user2_name}' not found")
        
        # Generate suggestions (simplified for now)
        suggestions = get_meeting_suggestions_from_core(
            seed=request.seed,
            user1_name=request.user1_name,
            user2_name=request.user2_name,
            time_range_days=getattr(request, 'time_range_days', None),
            start_date=getattr(request, 'start_date', None),
            end_date=getattr(request, 'end_date', None),
            conversation_context=getattr(request, 'conversation_context', None)
        )
        
        if not suggestions:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Failed to generate meeting suggestions",
                    "message": "AI service returned no suggestions",
                    "help": "Check your API key and try again"
                }
            )
        
        return MeetingSuggestionsResponse(**suggestions)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": str(e),
                "help": "Check server logs for more details"
            }
        )


# Text Chat Endpoints
@app.post("/text-chat", response_model=TextChatResponse)
async def handle_text_chat(request: TextChatRequest):
    """Handle text chat between users"""
    try:
        # Get user information
        user1 = get_user_manager().get_user_by_name(request.user1_name)
        user2 = get_user_manager().get_user_by_name(request.user2_name)
        
        if not user1:
            raise HTTPException(status_code=404, detail=f"User '{request.user1_name}' not found")
        if not user2:
            raise HTTPException(status_code=404, detail=f"User '{request.user2_name}' not found")
        
        # Use core business logic
        result = handle_text_chat_from_core(
            request.user1_name, 
            request.user2_name, 
            request.message, 
            request.script_context
        )
        
        return TextChatResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Conversation Context Endpoints
@app.get("/conversation-context/{user1_name}/{user2_name}", response_model=ConversationContextResponse)
async def get_conversation_context(user1_name: str, user2_name: str):
    """Get conversation context between two users"""
    try:
        # Get user information
        user1 = get_user_manager().get_user_by_name(user1_name)
        user2 = get_user_manager().get_user_by_name(user2_name)
        
        if not user1:
            raise HTTPException(status_code=404, detail=f"User '{user1_name}' not found")
        if not user2:
            raise HTTPException(status_code=404, detail=f"User '{user2_name}' not found")
        
        # Get conversation context from database
        context = get_db_manager().get_conversation_context(user1['id'], user2['id'])
        if not context:
            raise HTTPException(status_code=404, detail="No conversation context found")
        
        return ConversationContextResponse(**context)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
