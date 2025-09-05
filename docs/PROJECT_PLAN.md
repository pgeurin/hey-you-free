# AI-Powered Event Scheduling Application

## Project Overview
An AI-powered backend service that analyzes two Google calendars and suggests optimal meeting times when both participants are free and would enjoy the activity together.

## Architecture
- **Clean Architecture**: Separate I/O from business logic ✅
- **Functional Programming**: No OOP, snake_case naming ✅
- **TDD Approach**: Write tests first, commit when passing ✅
- **Backend Focus**: API service with Google Calendar integration ✅

## Core Features

### ✅ COMPLETED: Calendar Import & Processing
1. **Google Calendar API Integration**
   - OAuth2 authentication flow ✅
   - Calendar data extraction ✅
   - Event parsing and normalization ✅

2. **Data Processing Pipeline**
   - Convert calendar events to structured text ✅
   - Extract availability windows ✅
   - Parse event metadata (title, duration, type) ✅

### ✅ COMPLETED: AI-Powered Suggestions
3. **AI Suggestion Engine**
   - Activity recommendation based on preferences ✅
   - Optimal time slot selection ✅
   - Context-aware suggestions ✅
   - Deterministic responses with seeding ✅

4. **Response Validation**
   - JSON schema validation ✅
   - Energy level validation ✅
   - Meeting type validation ✅
   - Date/time format validation ✅

### ✅ COMPLETED: API & Testing
5. **FastAPI Backend**
   - Health check endpoint ✅
   - Meeting suggestions endpoint ✅
   - CORS configuration ✅
   - Error handling ✅

6. **Comprehensive Testing**
   - 80+ test functions across 8 test files ✅
   - True end-to-end testing ✅
   - API integration tests ✅
   - Environment setup tests ✅



## Technical Stack
- **Language**: Python 3.11+ ✅
- **Framework**: FastAPI ✅
- **Database**: SQLite (development) / PostgreSQL (production) 🔄
- **AI/ML**: Gemini AI API ✅
- **Calendar**: Google Calendar API v3 ✅
- **Testing**: pytest ✅
- **Environment**: mamba (butterfly) ✅
- **Time Zone**: Seattle (PST/PDT) ✅

## Project Structure
```
butterfly2/
├── src/
│   ├── core/           # Business logic (no I/O) ✅
│   ├── adapters/       # External integrations ✅
│   ├── infrastructure/ # Database, config ✅
│   └── api/           # FastAPI routes ✅
├── tests/              # 80+ test functions ✅
├── requirements.txt    ✅
└── data/              # Sample calendar data ✅
```

## Technical Requirements

### Database Schema
See [docs/database/schema.sql](docs/database/schema.sql) for complete schema definition.

#### Key Tables
- **users** - User accounts with phone numbers and calendar info
- **conversations** - Message threads between users
- **messages** - Individual SMS/text messages
- **meeting_suggestions** - AI-generated meeting proposals
- **conversation_contexts** - AI context for better responses
- **script_templates** - Structured conversation flows

#### Messaging Integration
See [docs/database/MESSAGING_PLAN.md](docs/database/MESSAGING_PLAN.md) for detailed messaging implementation plan.

See [docs/database/schema.sql](docs/database/schema.sql) for complete schema definition.

#### Key Tables

### API Endpoint Updates
- `POST /meeting-suggestions` - Accept user names, optional time range, and conversation context
  - Parameters:
    - `user1_name`: string (required)
    - `user2_name`: string (required) 
    - `time_range_days`: integer (optional, default: 14)
    - `start_date`: string (optional, ISO format YYYY-MM-DD)
    - `end_date`: string (optional, ISO format YYYY-MM-DD)
    - `conversation_context`: string (optional, additional context for AI)
- `GET /users` - List all users
- `POST /users` - Create new user
- `PUT /users/{user_id}` - Update user calendar/oauth info
- `DELETE /users/{user_id}` - Remove user
- `POST /text-chat` - Text integration endpoint for AI chat
- `GET /conversation-context/{user1}/{user2}` - Get conversation history

### Function Signature Updates
```python
def format_events_for_ai(events: List[Dict[str, Any]], user_name: str) -> str:
    """Format calendar events for AI analysis with dynamic user names"""

def create_ai_prompt(user1_name: str, user1_events: List[Dict], 
                    user2_name: str, user2_events: List[Dict],
                    time_range_days: int = 14,
                    start_date: Optional[str] = None,
                    end_date: Optional[str] = None,
                    conversation_context: Optional[str] = None) -> str:
    """Create AI prompt with dynamic user names, configurable time range, and conversation context"""

def get_meeting_suggestions(user1_name: str, user2_name: str,
                           time_range_days: int = 14,
                           start_date: Optional[str] = None,
                           end_date: Optional[str] = None,
                           conversation_context: Optional[str] = None) -> Dict[str, Any]:
    """Main API function with flexible time range parameters and conversation context"""

def handle_text_chat(user1_name: str, user2_name: str, 
                    message: str, script_context: Optional[str] = None) -> str:
    """Handle text-based AI chat between users with optional script following"""
```

### Request/Response Examples
```json
// POST /meeting-suggestions
{
  "user1_name": "phil",
  "user2_name": "chris",
  "time_range_days": 21,
  "start_date": "2025-01-20",
  "end_date": "2025-02-10",
  "conversation_context": "We discussed meeting for coffee last week and both mentioned being interested in trying the new cafe downtown"
}

// Response
{
  "suggestions": [...],
  "metadata": {
    "time_range_analyzed": "2025-01-20 to 2025-02-10",
    "user1": "phil",
    "user2": "chris",
    "conversation_context_used": true
  }
}

// POST /text-chat
{
  "user1_name": "phil",
  "user2_name": "chris",
  "message": "Hey, want to grab coffee sometime this week?",
  "script_context": "casual_coffee_invitation"
}
```

## Milestones

### ✅ Milestone 1: Single Calendar Import (COMPLETED)
- [x] Set up Google Calendar API credentials
- [x] Implement OAuth2 flow
- [x] Extract calendar events (last 7 days + next 7 days)
- [x] Save raw JSON results to file
- [x] Write tests for calendar parsing

### ✅ Milestone 2: AI Integration (COMPLETED)
- [x] Create calendar text formatter
- [x] Display events in readable format
- [x] Add time zone support
- [x] Test text output accuracy
- [x] Integrate Gemini AI for suggestions
- [x] Implement deterministic responses with seeding

### ✅ Milestone 3: API Backend (COMPLETED)
- [x] Design FastAPI server structure
- [x] Implement health check endpoint
- [x] Create meeting suggestions endpoint
- [x] Add CORS configuration
- [x] Test API integration

### ✅ Milestone 4: Comprehensive Testing (COMPLETED)
- [x] Write 80+ test functions
- [x] Implement true end-to-end testing
- [x] Add API integration tests
- [x] Create environment setup tests
- [x] Test validation and error handling

### �� Milestone 5: User Management & Database (IN PROGRESS)
- [ ] Database integration (SQLite/PostgreSQL)
- [ ] User table with name, calendar_id, oauth_tokens
- [ ] Update format_events_for_ai() to accept user names
- [ ] Database lookup for calendar names and OAuth credentials
- [ ] User authentication system
- [ ] API endpoints for user management
- [ ] Optional time range parameters for meeting suggestions
- [ ] Conversation context storage and retrieval

### 📋 Milestone 6: Text Integration (PLANNED)
- [ ] SMS/Text messaging integration (Twilio or similar)
- [ ] AI chat interface for meeting coordination
- [ ] Script-based conversation flows
- [ ] Text-to-meeting-scheduler integration
- [ ] Conversation history storage
- [ ] Multi-user text chat capabilities
- [ ] Natural language processing for meeting requests
- [ ] Automated meeting suggestion responses via text

### 📋 Milestone 7: Production Readiness (PLANNED)
- [ ] Rate limiting and security
- [ ] Production deployment
- [ ] Monitoring and logging
- [ ] Error handling and recovery

### 📋 Milestone 8: Advanced Features (PLANNED)
- [ ] Multi-user support
- [ ] Recurring meeting suggestions
- [ ] Calendar event creation
- [ ] Email notifications
- [ ] Mobile app integration




## Current Status
- **Core Functionality**: ✅ Complete and tested
- **API Backend**: ✅ Complete and tested  
- **Testing Coverage**: ✅ Comprehensive (80+ tests)
- **Production Ready**: 🔄 In progress
- **Advanced Features**: 📋 Planned

## Next Steps
1. ✅ Core meeting scheduler functionality
2. ✅ AI-powered suggestions with Gemini
3. ✅ FastAPI backend with endpoints
4. ✅ Comprehensive test suite
5. 🔄 Database integration
6. 📋 Text integration and chat capabilities
7. 📋 Production deployment
8. 📋 Advanced features

---

*Last Updated: 2025-01-15*
*Status: Core Complete, Production Ready in Progress*
