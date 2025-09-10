#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI server implementation
Clean Architecture: API layer delegates to core business logic
"""
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from typing import Optional, Dict, Any, List
import sys
import os
import json
import logging
import time
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from api.models import (
    MeetingSuggestionsResponse, ErrorResponse, UserCreate, UserUpdate, 
    UserResponse, MeetingSuggestionsRequest, TextChatRequest, TextChatResponse,
    ConversationContextResponse, CalendarEventRequest, CalendarEventFromSuggestionRequest,
    CalendarEventResponse, CalendarConflictRequest, CalendarConflictResponse,
    CalendarEventUpdateRequest, CalendarEventModifyTimeRequest, CalendarEventCancelRequest,
    CalendarEventUpdateResponse
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
from infrastructure.database_postgres import get_database_manager
from api.user_management import UserManager
from adapters.oauth_service import get_oauth_service, is_oauth_available
from adapters.oauth_dev_service import get_dev_oauth_service, is_dev_oauth_available
from adapters.sms_service import get_sms_service, is_sms_available


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
    if db_manager is None:
        db_manager = get_database_manager()
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

# Setup rate limiting and logging
config = load_environment_config()
rate_limit = config.get('RATE_LIMIT_PER_MINUTE', 60)
limiter = Limiter(key_func=get_remote_address, default_limits=[f"{rate_limit}/minute"])

# Configure logging
log_level = getattr(logging, config.get('LOG_LEVEL', 'INFO').upper())
log_format = config.get('LOG_FORMAT', 'text')

if log_format == 'json':
    # JSON logging for production
    logging.basicConfig(
        level=log_level,
        format='%(message)s',
        handlers=[logging.StreamHandler()]
    )
    logger = logging.getLogger(__name__)
    
    class JSONFormatter(logging.Formatter):
        def format(self, record):
            log_entry = {
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'level': record.levelname,
                'logger': record.name,
                'message': record.getMessage(),
                'module': record.module,
                'function': record.funcName,
                'line': record.lineno
            }
            if hasattr(record, 'request_id'):
                log_entry['request_id'] = record.request_id
            if hasattr(record, 'user_id'):
                log_entry['user_id'] = record.user_id
            if hasattr(record, 'duration'):
                log_entry['duration'] = record.duration
            return json.dumps(log_entry)
    
    # Apply JSON formatter to all handlers
    for handler in logging.root.handlers:
        handler.setFormatter(JSONFormatter())
else:
    # Text logging for development
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

# Add rate limiting to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors"""
    request_id = request.headers.get("X-Request-ID", "unknown")
    
    logger.error(f"Unhandled exception: {str(exc)}", extra={
        'request_id': request_id,
        'method': request.method,
        'url': str(request.url),
        'exception_type': type(exc).__name__,
        'exception_message': str(exc)
    }, exc_info=True)
    
    return {
        "error": "Internal server error",
        "message": "An unexpected error occurred",
        "request_id": request_id,
        "timestamp": datetime.utcnow().isoformat() + 'Z'
    }

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing and status"""
    start_time = time.time()
    request_id = f"req_{int(start_time * 1000)}"
    
    # Log request start
    logger.info(f"Request started", extra={
        'request_id': request_id,
        'method': request.method,
        'url': str(request.url),
        'client_ip': get_remote_address(request),
        'user_agent': request.headers.get('user-agent', 'unknown')
    })
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Log request completion
    logger.info(f"Request completed", extra={
        'request_id': request_id,
        'method': request.method,
        'url': str(request.url),
        'status_code': response.status_code,
        'duration': round(duration, 3),
        'client_ip': get_remote_address(request)
    })
    
    # Add request ID to response headers
    response.headers["X-Request-ID"] = request_id
    
    return response

# Add startup event
@app.on_event("startup")
async def startup_event():
    """Log server startup"""
    logger.info("Server starting up", extra={
        'version': '1.0.0',
        'environment': 'production' if config.get('DEBUG') == False else 'development',
        'rate_limit': rate_limit,
        'log_level': config.get('LOG_LEVEL'),
        'log_format': config.get('LOG_FORMAT')
    })

# Add shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Log server shutdown"""
    logger.info("Server shutting down")

# Add CORS middleware
allowed_origins = config.get('ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:8080').split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_meeting_suggestions_from_core(seed: int = 42, user1_name: str = "phil", user2_name: str = "chris", description: Optional[str] = None, **kwargs) -> Optional[Dict[str, Any]]:
    """Get meeting suggestions from core business logic"""
    try:
        # Get AI response
        response_text = get_meeting_suggestions_with_gemini(user1_name, user2_name, description)
        if not response_text:
            return None
        
        # Parse the response with user names
        suggestions = parse_gemini_response(response_text, user1_name, user2_name)
        if not suggestions:
            return None
        
        # Add event links to suggestions
        from core.event_link_generator import add_event_links_to_suggestions
        base_url = ""  # Could be enhanced to get from environment
        enhanced_suggestions = add_event_links_to_suggestions(
            suggestions['suggestions'], user1_name, user2_name, base_url
        )
        
        # Update the suggestions with enhanced data
        suggestions['suggestions'] = enhanced_suggestions
        
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
async def serve_landing_page():
    """Serve the landing page"""
    try:
        static_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "static"))
        html_path = os.path.join(static_path, "landing.html")
        print(f"Looking for landing page at: {html_path}")
        print(f"File exists: {os.path.exists(html_path)}")
        return FileResponse(html_path)
    except Exception as e:
        print(f"Error serving landing page: {e}")
        return {"error": str(e)}

@app.get("/scheduler")
async def serve_scheduler_interface():
    """Serve the scheduler interface"""
    try:
        static_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "static"))
        html_path = os.path.join(static_path, "index.html")
        print(f"Looking for scheduler HTML file at: {html_path}")
        print(f"File exists: {os.path.exists(html_path)}")
        return FileResponse(html_path)
    except Exception as e:
        print(f"Error serving scheduler interface: {e}")
        return {"error": str(e)}

@app.get("/health")
async def health_check():
    """Health check endpoint with system metrics"""
    import psutil
    import platform
    
    # Get system metrics
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Check API key status
    api_status = get_api_key_status()
    
    # Check database connectivity
    try:
        db_manager = get_db_manager()
        db_status = "healthy"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    health_data = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + 'Z',
        "version": "1.0.0",
        "system": {
            "platform": platform.system(),
            "python_version": platform.python_version(),
            "cpu_percent": cpu_percent,
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent
            },
            "disk": {
                "total": disk.total,
                "free": disk.free,
                "percent": (disk.used / disk.total) * 100
            }
        },
        "services": {
            "api_key": api_status['status'],
            "database": db_status,
            "rate_limiting": "enabled"
        }
    }
    
    # Log health check
    logger.info("Health check requested", extra={
        'cpu_percent': cpu_percent,
        'memory_percent': memory.percent,
        'api_status': api_status['status']
    })
    
    return health_data


@app.get("/meeting-suggestions", response_model=MeetingSuggestionsResponse)
@limiter.limit("10/minute")
async def get_meeting_suggestions(
    request: Request,
    seed: int = 42,
    user1: str = Query("phil", description="First user name"),
    user2: str = Query("chris", description="Second user name"),
    meeting_type: str = Query("coffee", description="Type of meeting"),
    description: Optional[str] = Query(None, description="Custom description for the meeting")
):
    """Get AI-generated meeting suggestions with query parameters"""
    try:
        # Log request details
        logger.info(f"Meeting suggestions request", extra={
            'user1': user1,
            'user2': user2,
            'meeting_type': meeting_type,
            'seed': seed,
            'has_description': bool(description)
        })
        
        # Check API key availability first
        api_status = get_api_key_status()
        if not api_status['available']:
            logger.error(f"API key not available: {api_status['message']}")
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
            meeting_type=meeting_type,
            description=description
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
        
        # Add event links to suggestions
        from core.event_link_generator import add_event_links_to_suggestions
        base_url = ""  # Could be enhanced to get from environment
        enhanced_suggestions = add_event_links_to_suggestions(
            suggestions['suggestions'], request.user1_name, request.user2_name, base_url
        )
        
        # Update the suggestions with enhanced data
        suggestions['suggestions'] = enhanced_suggestions
        
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
@limiter.limit("20/minute")
async def handle_text_chat(request: Request, chat_request: TextChatRequest):
    """Handle text chat between users"""
    try:
        # Get user information
        user1 = get_user_manager().get_user_by_name(chat_request.user1_name)
        user2 = get_user_manager().get_user_by_name(chat_request.user2_name)
        
        if not user1:
            raise HTTPException(status_code=404, detail=f"User '{chat_request.user1_name}' not found")
        if not user2:
            raise HTTPException(status_code=404, detail=f"User '{chat_request.user2_name}' not found")
        
        # Use core business logic
        result = handle_text_chat_from_core(
            chat_request.user1_name, 
            chat_request.user2_name, 
            chat_request.message, 
            chat_request.script_context
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
@limiter.limit("5/minute")
async def oauth_start(request: Request, user_id: Optional[str] = None):
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
        
        # Use dev OAuth service if production OAuth is not available
        if is_oauth_available():
            oauth_service = get_oauth_service()
        else:
            oauth_service = get_dev_oauth_service()
        
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

# Calendar Event Creation Endpoints
@app.post("/calendar/events", response_model=CalendarEventResponse)
async def create_calendar_event(request: CalendarEventRequest):
    """Create a calendar event"""
    try:
        from adapters.google_calendar_client import create_calendar_event, check_calendar_conflicts
        
        # Check for conflicts first
        conflicts = check_calendar_conflicts(request.start, request.end, request.calendar_id)
        
        # Create the event
        created_event = create_calendar_event(
            summary=request.summary,
            start_time=request.start,
            end_time=request.end,
            description=request.description,
            location=request.location,
            attendees=request.attendees,
            calendar_id=request.calendar_id
        )
        
        if created_event:
            return CalendarEventResponse(
                success=True,
                event_id=created_event.get('id'),
                event_url=created_event.get('htmlLink'),
                message="Event created successfully",
                conflicts=conflicts if conflicts else None
            )
        else:
            return CalendarEventResponse(
                success=False,
                message="Failed to create event - check OAuth configuration",
                conflicts=conflicts if conflicts else None
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/calendar/events/from-suggestion", response_model=CalendarEventResponse)
async def create_calendar_event_from_suggestion(request: CalendarEventFromSuggestionRequest):
    """Create a calendar event from a meeting suggestion"""
    try:
        from adapters.google_calendar_client import create_calendar_event, check_calendar_conflicts
        from datetime import datetime, timedelta
        
        # Parse date and time
        date_obj = datetime.strptime(request.date, "%Y-%m-%d")
        time_obj = datetime.strptime(request.time, "%H:%M")
        
        # Combine date and time
        start_datetime = date_obj.replace(
            hour=time_obj.hour,
            minute=time_obj.minute,
            second=0,
            microsecond=0
        )
        
        # Parse duration (handle formats like "1 hour", "90 minutes", "1.5 hours")
        duration_str = request.duration.lower()
        if "hour" in duration_str:
            hours = float(duration_str.split()[0])
            duration_minutes = int(hours * 60)
        elif "minute" in duration_str:
            duration_minutes = int(duration_str.split()[0])
        else:
            duration_minutes = 60  # Default to 1 hour
        
        end_datetime = start_datetime + timedelta(minutes=duration_minutes)
        
        # Format for Google Calendar API
        start_iso = start_datetime.isoformat() + "Z"
        end_iso = end_datetime.isoformat() + "Z"
        
        # Check for conflicts
        conflicts = check_calendar_conflicts(start_iso, end_iso)
        
        # Create the event
        created_event = create_calendar_event(
            summary=request.summary,
            start_time=start_iso,
            end_time=end_iso,
            description=request.description,
            location=request.location,
            attendees=request.attendees
        )
        
        if created_event:
            return CalendarEventResponse(
                success=True,
                event_id=created_event.get('id'),
                event_url=created_event.get('htmlLink'),
                message="Event created successfully from suggestion",
                conflicts=conflicts if conflicts else None
            )
        else:
            return CalendarEventResponse(
                success=False,
                message="Failed to create event from suggestion - check OAuth configuration",
                conflicts=conflicts if conflicts else None
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/calendar/conflicts", response_model=CalendarConflictResponse)
async def check_calendar_conflicts_endpoint(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    time: str = Query(..., description="Time in HH:MM format"),
    duration: int = Query(..., description="Duration in minutes"),
    calendar_id: str = Query("primary", description="Calendar ID")
):
    """Check for calendar conflicts"""
    try:
        from adapters.google_calendar_client import check_calendar_conflicts
        from datetime import datetime, timedelta
        
        # Parse date and time
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        time_obj = datetime.strptime(time, "%H:%M")
        
        # Combine date and time
        start_datetime = date_obj.replace(
            hour=time_obj.hour,
            minute=time_obj.minute,
            second=0,
            microsecond=0
        )
        
        end_datetime = start_datetime + timedelta(minutes=duration)
        
        # Format for Google Calendar API
        start_iso = start_datetime.isoformat() + "Z"
        end_iso = end_datetime.isoformat() + "Z"
        
        # Check for conflicts
        conflicts = check_calendar_conflicts(start_iso, end_iso, calendar_id)
        
        return CalendarConflictResponse(
            has_conflicts=len(conflicts) > 0,
            conflicts=conflicts,
            message=f"Found {len(conflicts)} potential conflicts" if conflicts else "No conflicts found"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/calendar/events/create-from-suggestion/{suggestion_id}", response_model=CalendarEventResponse)
async def create_event_from_suggestion_link(suggestion_id: str):
    """Create calendar event from suggestion link"""
    try:
        # Handle hash-based suggestion IDs (like suggestion_97af7d80)
        if suggestion_id.startswith('suggestion_'):
            # For hash-based IDs, we can't look up in database directly
            # Return a message explaining the limitation
            return CalendarEventResponse(
                success=False,
                message="Hash-based suggestion IDs require the original suggestion data. Please use the 'Create Calendar Event' button from the meeting suggestions page.",
                conflicts=None
            )
        
        # Handle integer-based suggestion IDs (database lookups)
        try:
            suggestion = get_db_manager().get_meeting_suggestion(int(suggestion_id))
            if not suggestion:
                raise HTTPException(status_code=404, detail="Suggestion not found")
            
            # Extract suggestion data
            suggestion_data = suggestion['suggestion_data']
            suggestions = suggestion_data.get('suggestions', [])
            
            if not suggestions:
                raise HTTPException(status_code=400, detail="No suggestions found in stored data")
            
            # Use the first suggestion (or could be enhanced to select specific one)
            first_suggestion = suggestions[0]
            
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid suggestion ID format")
        
        # Create calendar event from suggestion
        from adapters.google_calendar_client import create_calendar_event, check_calendar_conflicts
        from datetime import datetime, timedelta
        
        # Parse date and time
        date_obj = datetime.strptime(first_suggestion['date'], "%Y-%m-%d")
        time_obj = datetime.strptime(first_suggestion['time'], "%H:%M")
        
        # Combine date and time
        start_datetime = date_obj.replace(
            hour=time_obj.hour,
            minute=time_obj.minute,
            second=0,
            microsecond=0
        )
        
        # Parse duration
        duration_str = first_suggestion['duration'].lower()
        if "hour" in duration_str:
            hours = float(duration_str.split()[0])
            duration_minutes = int(hours * 60)
        elif "minute" in duration_str:
            duration_minutes = int(duration_str.split()[0])
        else:
            duration_minutes = 60  # Default to 1 hour
        
        end_datetime = start_datetime + timedelta(minutes=duration_minutes)
        
        # Format for Google Calendar API
        start_iso = start_datetime.isoformat() + "Z"
        end_iso = end_datetime.isoformat() + "Z"
        
        # Check for conflicts
        conflicts = check_calendar_conflicts(start_iso, end_iso)
        
        # Create the event
        created_event = create_calendar_event(
            summary=f"{first_suggestion['meeting_type'].title()} Meeting",
            start_time=start_iso,
            end_time=end_iso,
            description=first_suggestion.get('reasoning', ''),
            location=first_suggestion.get('location', ''),
            attendees=None  # Could be enhanced to include user emails
        )
        
        if created_event:
            return CalendarEventResponse(
                success=True,
                event_id=created_event.get('id'),
                event_url=created_event.get('htmlLink'),
                message="Event created successfully from suggestion link",
                conflicts=conflicts if conflicts else None
            )
        else:
            return CalendarEventResponse(
                success=False,
                message="Failed to create event from suggestion link - check OAuth configuration",
                conflicts=conflicts if conflicts else None
            )
            
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid suggestion ID format")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Calendar Event Modification Endpoints
@app.put("/calendar/events/{event_id}", response_model=CalendarEventUpdateResponse)
async def update_calendar_event(
    event_id: str,
    request: CalendarEventUpdateRequest,
    calendar_id: str = "primary"
):
    """Update an existing calendar event"""
    try:
        from adapters.google_calendar_client import update_event
        
        # Prepare event data for update
        event_data = {}
        if request.summary is not None:
            event_data['summary'] = request.summary
        if request.start is not None:
            event_data['start'] = {'dateTime': request.start, 'timeZone': 'UTC'}
        if request.end is not None:
            event_data['end'] = {'dateTime': request.end, 'timeZone': 'UTC'}
        if request.description is not None:
            event_data['description'] = request.description
        if request.location is not None:
            event_data['location'] = request.location
        if request.attendees is not None:
            event_data['attendees'] = [{'email': email} for email in request.attendees]
        
        # Update the event
        updated_event = update_event(calendar_id, event_id, event_data)
        
        if updated_event:
            return CalendarEventUpdateResponse(
                success=True,
                event_id=updated_event.get('id'),
                message="Event updated successfully",
                updated_event=updated_event
            )
        else:
            return CalendarEventUpdateResponse(
                success=False,
                message="Failed to update event - check OAuth configuration"
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/calendar/events/{event_id}/time", response_model=CalendarEventUpdateResponse)
async def modify_event_time(
    event_id: str,
    request: CalendarEventModifyTimeRequest,
    calendar_id: str = "primary"
):
    """Modify the time of an existing calendar event"""
    try:
        from adapters.google_calendar_client import modify_event_time
        
        # Modify the event time
        updated_event = modify_event_time(
            calendar_id, 
            event_id, 
            request.new_start_time, 
            request.new_end_time
        )
        
        if updated_event:
            return CalendarEventUpdateResponse(
                success=True,
                event_id=updated_event.get('id'),
                message="Event time modified successfully",
                updated_event=updated_event
            )
        else:
            return CalendarEventUpdateResponse(
                success=False,
                message="Failed to modify event time - check OAuth configuration"
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/calendar/events/{event_id}/cancel", response_model=CalendarEventUpdateResponse)
async def cancel_calendar_event(
    event_id: str,
    request: CalendarEventCancelRequest,
    calendar_id: str = "primary"
):
    """Cancel an existing calendar event"""
    try:
        from adapters.google_calendar_client import cancel_event
        
        # Cancel the event
        success = cancel_event(calendar_id, event_id, request.cancellation_reason)
        
        if success:
            return CalendarEventUpdateResponse(
                success=True,
                event_id=event_id,
                message="Event cancelled successfully"
            )
        else:
            return CalendarEventUpdateResponse(
                success=False,
                message="Failed to cancel event - check OAuth configuration"
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/calendar/events/{event_id}", response_model=CalendarEventUpdateResponse)
async def delete_calendar_event(
    event_id: str,
    calendar_id: str = "primary"
):
    """Permanently delete a calendar event"""
    try:
        from adapters.google_calendar_client import delete_event
        
        # Delete the event
        success = delete_event(calendar_id, event_id)
        
        if success:
            return CalendarEventUpdateResponse(
                success=True,
                event_id=event_id,
                message="Event deleted successfully"
            )
        else:
            return CalendarEventUpdateResponse(
                success=False,
                message="Failed to delete event - check OAuth configuration"
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# SMS Webhook Endpoints
@app.post("/webhooks/sms")
async def handle_sms_webhook(request: Request):
    """Handle incoming SMS webhook from Twilio"""
    try:
        # Get SMS service
        sms_service = get_sms_service()
        if not sms_service.is_configured():
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "SMS service not configured",
                    "message": "Twilio credentials not available",
                    "help": "Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER"
                }
            )
        
        # Get request data
        form_data = await request.form()
        webhook_data = dict(form_data)
        
        # Validate webhook signature (optional but recommended)
        signature = request.headers.get('X-Twilio-Signature', '')
        webhook_url = str(request.url)
        
        # Parse incoming message
        message_data = sms_service.parse_incoming_message(webhook_data)
        
        # Log incoming message to backend_errors.txt
        with open('backend_errors.txt', 'a') as f:
            f.write(f"SMS received: {message_data}\n")
        
        # TODO: Process message with AI and generate response
        # For now, just acknowledge receipt
        response_message = "Message received! AI processing coming soon."
        
        # Send response back to user
        response_result = sms_service.send_sms(
            to_phone=message_data['from_phone'],
            message=response_message
        )
        
        return {
            "status": "received",
            "message_id": message_data['message_id'],
            "response_sent": response_result['success'],
            "response_message": response_message
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Log error to backend_errors.txt
        with open('backend_errors.txt', 'a') as f:
            f.write(f"SMS webhook error: {str(e)}\n")
        
        raise HTTPException(
            status_code=500,
            detail={
                "error": "SMS webhook processing failed",
                "message": str(e)
            }
        )


@app.get("/sms/status")
async def sms_status():
    """Check SMS service configuration status"""
    sms_service = get_sms_service()
    return {
        "available": is_sms_available(),
        "configured": sms_service.is_configured(),
        "phone_number": sms_service.phone_number if sms_service.is_configured() else None,
        "message": "SMS service is properly configured" if sms_service.is_configured() else "SMS service not configured"
    }


@app.post("/sms/send")
async def send_sms_message(
    to_phone: str = Query(..., description="Phone number to send SMS to"),
    message: str = Query(..., description="Message content to send")
):
    """Send SMS message manually"""
    try:
        sms_service = get_sms_service()
        if not sms_service.is_configured():
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "SMS service not configured",
                    "message": "Twilio credentials not available"
                }
            )
        
        result = sms_service.send_sms(to_phone, message)
        
        if result['success']:
            return {
                "success": True,
                "message_id": result['message_id'],
                "status": result['status'],
                "message": "SMS sent successfully"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Failed to send SMS",
                    "message": result.get('error', 'Unknown error')
                }
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "SMS sending failed",
                "message": str(e)
            }
        )


@app.get("/share/event/{suggestion_id}")
async def share_event_suggestion(suggestion_id: str):
    """Share event suggestion - returns event details for sharing"""
    try:
        # Handle hash-based suggestion IDs (like suggestion_97af7d80)
        if suggestion_id.startswith('suggestion_'):
            # For hash-based IDs, we can't look up in database directly
            # Return a helpful response that explains how to get the actual event details
            return {
                "event_details": {
                    "date": "Dynamic",
                    "time": "Dynamic", 
                    "duration": "Dynamic",
                    "meeting_type": "Meeting Suggestion",
                    "location": "To be determined",
                    "reasoning": "This is a shareable event link. To see the actual event details, please visit the meeting scheduler and generate new suggestions, or ask the person who shared this link for the specific meeting details.",
                    "user_energies": {},
                    "confidence": 0.8
                },
                "share_info": {
                    "suggestion_id": suggestion_id,
                    "created_at": "Dynamic",
                    "share_url": f"/share/event/{suggestion_id}",
                    "create_event_url": f"/calendar/events/create-from-suggestion/{suggestion_id}",
                    "note": "This is a dynamic event link. The actual event details are generated when suggestions are created. Please visit the meeting scheduler to see current suggestions.",
                    "instructions": "To see actual event details: 1) Visit the meeting scheduler, 2) Generate new suggestions, 3) Use the 'Create Calendar Event' button from the suggestions page"
                }
            }
        
        # Handle integer-based suggestion IDs (database lookups)
        try:
            suggestion = get_db_manager().get_meeting_suggestion(int(suggestion_id))
            if not suggestion:
                raise HTTPException(status_code=404, detail="Event suggestion not found")
            
            # Extract suggestion data
            suggestion_data = suggestion['suggestion_data']
            suggestions = suggestion_data.get('suggestions', [])
            
            if not suggestions:
                raise HTTPException(status_code=400, detail="No suggestions found in stored data")
            
            # Use the first suggestion (or could be enhanced to select specific one)
            first_suggestion = suggestions[0]
            
            # Create shareable event details
            share_data = {
                "event_details": {
                    "date": first_suggestion['date'],
                    "time": first_suggestion['time'],
                    "duration": first_suggestion['duration'],
                    "meeting_type": first_suggestion['meeting_type'],
                    "location": first_suggestion.get('location', ''),
                    "reasoning": first_suggestion.get('reasoning', ''),
                    "user_energies": first_suggestion.get('user_energies', {}),
                    "confidence": first_suggestion.get('confidence', 0.0)
                },
                "share_info": {
                    "suggestion_id": suggestion_id,
                    "created_at": suggestion['created_at'],
                    "share_url": f"/share/event/{suggestion_id}",
                    "create_event_url": f"/calendar/events/create-from-suggestion/{suggestion_id}"
                }
            }
            
            return share_data
            
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid suggestion ID format")
        except HTTPException:
            raise  # Re-raise HTTP exceptions as-is
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    import os
    # Railway uses SERVER_PORT, fallback to PORT, then 8000
    port = int(os.environ.get("SERVER_PORT", os.environ.get("PORT", 8000)))
    uvicorn.run(app, host="0.0.0.0", port=port)
