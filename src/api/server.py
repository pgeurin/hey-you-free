#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI server implementation
Clean Architecture: API layer delegates to core business logic
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Optional, Dict, Any, List
import sys
import os
import json

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from api.models import (
    MeetingSuggestionsResponse, ErrorResponse, UserCreate, UserUpdate, 
    UserResponse, MeetingSuggestionsRequest, TextChatRequest, TextChatResponse,
    ConversationContextResponse
)
from adapters.cli import get_meeting_suggestions_with_gemini
from core.meeting_scheduler import validate_meeting_suggestions, create_ai_prompt, format_events_for_ai
from adapters.gemini_client import parse_gemini_response, get_deterministic_meeting_suggestions
from infrastructure.calendar_loader import load_calendar_data
from infrastructure.environment import (
    validate_environment,
    get_api_key_status,
    load_environment_config
)
from infrastructure.database import DatabaseManager
from api.user_management import UserManager
from adapters.oauth_service import get_oauth_service, is_oauth_available
from adapters.oauth_dev_service import get_dev_oauth_service, is_dev_oauth_available


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

def get_meeting_suggestions_from_core(seed: int = 42, user1_name: str = "phil", user2_name: str = "chris", **kwargs) -> Optional[Dict[str, Any]]:
    """Get meeting suggestions from core business logic"""
    try:
        # Get AI response
        response_text = get_meeting_suggestions_with_gemini(user1_name, user2_name)
        if not response_text:
            return None
        
        # Parse the response with user names
        suggestions = parse_gemini_response(response_text, user1_name, user2_name)
        if not suggestions:
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


@app.get("/")
async def serve_web_interface():
    """Serve the web interface"""
    try:
        static_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "static"))
        html_path = os.path.join(static_path, "index.html")
        print(f"Looking for HTML file at: {html_path}")
        print(f"File exists: {os.path.exists(html_path)}")
        return FileResponse(html_path)
    except Exception as e:
        print(f"Error serving web interface: {e}")
        return {"error": str(e)}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/meeting-suggestions", response_model=MeetingSuggestionsResponse)
async def get_meeting_suggestions(
    seed: int = 42,
    user1: str = Query("phil", description="First user name"),
    user2: str = Query("chris", description="Second user name"),
    meeting_type: str = Query("coffee", description="Type of meeting")
):
    """Get AI-generated meeting suggestions with query parameters"""
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
        
        suggestions = get_meeting_suggestions_from_core(
            seed=seed, 
            user1_name=user1, 
            user2_name=user2,
            meeting_type=meeting_type
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
@app.post("/meeting-suggestions-db", response_model=MeetingSuggestionsResponse)
async def get_meeting_suggestions_with_database(request: MeetingSuggestionsRequest):
    """Get meeting suggestions using database integration"""
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
        
        # Get user information from database
        user1 = get_user_manager().get_user_by_name(request.user1_name)
        user2 = get_user_manager().get_user_by_name(request.user2_name)
        
        if not user1:
            raise HTTPException(status_code=404, detail=f"User '{request.user1_name}' not found")
        if not user2:
            raise HTTPException(status_code=404, detail=f"User '{request.user2_name}' not found")
        
        # Load calendar data (in production, this would use OAuth tokens)
        try:
            user1_events = load_calendar_data(f"data/{request.user1_name}_calendar_events_raw.json")
        except FileNotFoundError:
            user1_events = load_calendar_data("data/calendar_events_raw.json")
        
        try:
            user2_events = load_calendar_data(f"data/{request.user2_name}_calendar_events_raw.json")
        except FileNotFoundError:
            user2_events = load_calendar_data("data/chris_calendar_events_raw.json")
        
        # Create AI prompt with user names
        prompt = create_ai_prompt(user1_events, user2_events, request.user1_name, request.user2_name)
        
        # Store conversation context if provided
        if hasattr(request, 'conversation_context') and request.conversation_context:
            get_db_manager().store_conversation_context(
                user1['id'], user2['id'], request.conversation_context, "meeting_discussion"
            )
        
        # Get AI response
        ai_response = get_deterministic_meeting_suggestions(prompt, seed=request.seed)
        if not ai_response:
            raise HTTPException(status_code=500, detail="Failed to get AI response")
        
        # Parse response
        suggestions = parse_gemini_response(ai_response, request.user1_name, request.user2_name)
        if not suggestions:
            raise HTTPException(status_code=500, detail="Failed to parse AI response")
        
        # Store meeting suggestions in database
        # Check if conversation already exists
        existing_conversation = get_db_manager().get_conversation(user1['id'], user2['id'])
        if existing_conversation:
            conversation_id = existing_conversation['id']
        else:
            conversation_id = get_db_manager().create_conversation(user1['id'], user2['id'])
        
        get_db_manager().store_meeting_suggestion(
            conversation_id, user1['id'], user2['id'], suggestions
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


# OAuth Endpoints
@app.get("/oauth/google/start")
async def oauth_start(user_id: Optional[str] = None):
    """Start Google OAuth flow"""
    try:
        if not is_oauth_available():
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "OAuth not configured",
                    "message": "Google OAuth is not properly configured",
                    "help": "Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables"
                }
            )
        
        oauth_service = get_oauth_service()
        auth_url, state = oauth_service.get_authorization_url(user_id)
        
        # Redirect to Google OAuth
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=auth_url)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "OAuth start failed",
                "message": str(e),
                "help": "Check OAuth configuration"
            }
        )


@app.get("/oauth/google/callback")
async def oauth_callback(
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None
):
    """Handle Google OAuth callback"""
    try:
        if error:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "OAuth authorization failed",
                    "message": f"Google returned error: {error}",
                    "help": "User may have denied access or there was an OAuth error"
                }
            )
        
        if not code or not state:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Missing OAuth parameters",
                    "message": "Authorization code or state parameter missing",
                    "help": "Complete OAuth flow from the start"
                }
            )
        
        if not is_oauth_available():
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "OAuth not configured",
                    "message": "Google OAuth is not properly configured"
                }
            )
        
        oauth_service = get_oauth_service()
        token_data = oauth_service.exchange_code_for_tokens(code, state)
        
        # Test calendar access
        if not oauth_service.test_calendar_access(token_data['credentials']):
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Calendar access failed",
                    "message": "Could not access user's Google Calendar",
                    "help": "Check OAuth scopes and permissions"
                }
            )
        
        # Store tokens in database (if user_id provided)
        user_id = token_data.get('user_id')
        if user_id:
            try:
                user_manager = get_user_manager()
                user = user_manager.get_user_by_name(user_id)
                if user:
                    # Update user with OAuth tokens
                    user_manager.update_user(user['id'], {
                        'oauth_tokens': json.dumps(token_data['credentials'])
                    })
            except Exception as e:
                print(f"Warning: Could not store tokens for user {user_id}: {e}")
        
        # Redirect to success page
        from fastapi.responses import RedirectResponse
        success_url = f"/?oauth_success=true&user_id={user_id or 'unknown'}"
        return RedirectResponse(url=success_url)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "OAuth callback failed",
                "message": str(e),
                "help": "Check OAuth configuration and try again"
            }
        )


@app.get("/oauth/status")
async def oauth_status():
    """Check OAuth configuration status"""
    return {
        "available": is_oauth_available(),
        "configured": get_oauth_service().is_configured() if is_oauth_available() else False,
        "dev_mode": not is_oauth_available(),
        "message": "OAuth is properly configured" if is_oauth_available() else "OAuth not available - using dev mode"
    }


# Development OAuth Endpoints (for testing without Google verification)
@app.get("/oauth/dev/simulate")
async def dev_oauth_simulate(state: Optional[str] = None):
    """Simulate OAuth authorization for development"""
    if not state:
        return {"error": "Missing state parameter"}
    
    # Simulate user authorization
    from fastapi.responses import HTMLResponse
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dev OAuth Simulation</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }}
            .container {{ background: #f5f5f5; padding: 30px; border-radius: 10px; text-align: center; }}
            .btn {{ background: #4285f4; color: white; padding: 15px 30px; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; }}
            .btn:hover {{ background: #3367d6; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🔧 Development OAuth Simulation</h2>
            <p>This simulates Google OAuth authorization for development testing.</p>
            <p><strong>State:</strong> {state}</p>
            <button class="btn" onclick="authorize()">✅ Authorize Access</button>
            <button class="btn" onclick="deny()" style="background: #ea4335; margin-left: 10px;">❌ Deny Access</button>
        </div>
        
        <script>
            function authorize() {{
                window.location.href = '/oauth/google/callback?code=dev_code_123&state={state}';
            }}
            
            function deny() {{
                window.location.href = '/oauth/google/callback?error=access_denied&state={state}';
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/oauth/dev/start")
async def dev_oauth_start(user_id: Optional[str] = None):
    """Start development OAuth flow"""
    try:
        dev_oauth_service = get_dev_oauth_service()
        auth_url, state = dev_oauth_service.get_authorization_url(user_id)
        
        # Redirect to dev simulation
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=auth_url)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Dev OAuth start failed",
                "message": str(e)
            }
        )


# Mount static files after all routes are defined
static_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "static"))
app.mount("/static", StaticFiles(directory=static_path), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
