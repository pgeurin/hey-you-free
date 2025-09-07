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

## Task Tracking & Milestones

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

### ✅ Milestone 5: User Management & Database (COMPLETED)
**Completed Tasks:**
- [x] Update format_events_for_ai() to accept user names
- [x] Update create_ai_prompt() to accept user names and optional time range parameters
- [x] Update get_meeting_suggestions() to use database lookup for user calendar data
- [x] Add conversation context storage and retrieval functionality
- [x] Update API endpoints to use new user management system
- [x] Test complete database integration with user management

**Infrastructure (Completed):**
- [x] Database integration (SQLite/PostgreSQL)
- [x] User table with name, calendar_id, oauth_tokens
- [x] Database lookup for calendar names and OAuth credentials
- [x] User authentication system
- [x] API endpoints for user management


### 📋 Milestone 6: testing (PLANNED)
- [ ] Make two new user calendars in testing env (a json file)
   - give each different personalities and preferences
- [ ] Make sure the event planner is typical


### 📋 Milestone 6.01: Simple Web Interface (PLANNED)
**Minimal Frontend Approach:**
- [ ] Static HTML page with form
- [ ] Google OAuth integration (server-side)
- [ ] Simple JavaScript for API calls
- [ ] Basic CSS for styling
- [ ] Server-side form handling
- [ ] Event confirmation page

**Alternative: CLI Interface:**
- [ ] Interactive CLI event planner
- [ ] Command-line OAuth flow
- [ ] Terminal-based suggestion display
- [ ] Keyboard navigation for selections

### 📋 Milestone Calendar Event Creation (PLANNED)
- [ ] Google Calendar API event creation
- [ ] Automatic event addition to both users' calendars
- [ ] Event details population (location, description, attendees)
- [ ] Calendar conflict detection
- [ ] Event modification and cancellation
- [ ] Reminder and notification settings

### 📋 Milestone 6.1: User Invitation System (PLANNED)
- [ ] Email invitation system for new users
- [ ] "Connect your calendar" onboarding flow
- [ ] User discovery by name/email
- [ ] Pending invitation management
- [ ] Calendar connection status tracking

### 📋 Milestone 6.2: Multi-User Group Planning (PLANNED)
- [ ] Group creation and management
- [ ] Multi-user calendar analysis (3+ people)
- [ ] Group preference settings
- [ ] Group event suggestion algorithms
- [ ] Group confirmation workflow
- [ ] Group member management interface

### 📋 Milestone 6.3: Text/SMS Integration (PLANNED)
- [ ] SMS/Text messaging integration (Twilio or similar)
- [ ] AI chat interface for meeting coordination
- [ ] Script-based conversation flows
- [ ] Text-to-meeting-scheduler integration
- [ ] Conversation history storage
- [ ] Multi-user text chat capabilities
- [ ] Natural language processing for meeting requests
- [ ] Automated meeting suggestion responses via text
- [ ] Rate limiting for SMS (200 texts/day warning to admin)

### 📋 Milestone 6.4: Smart Context & Learning (PLANNED)
- [ ] User preference learning from past events
- [ ] Context-aware suggestion algorithms
- [ ] Personalized activity recommendations
- [ ] Time preference learning (morning/evening person)
- [ ] Activity type preferences (coffee, outdoor, dinner)
- [ ] Historical pattern analysis



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
- **Testing Coverage**: ✅ Comprehensive (153 tests)
- **Database Infrastructure**: ✅ Complete
- **User Management**: ✅ Complete and tested
- **Web Interface**: 📋 Planned (Milestone 6)
- **Text Integration**: 📋 Planned (Milestone 6.3)
- **Production Ready**: 🔄 In progress
- **Advanced Features**: 📋 Planned

## Next Steps
1. ✅ Core meeting scheduler functionality
2. ✅ AI-powered suggestions with Gemini
3. ✅ FastAPI backend with endpoints
4. ✅ Comprehensive test suite (153 tests)
5. ✅ Complete user management integration
6. 📋 Build simple web interface with OAuth (Milestone 6)
7. 📋 Add text/SMS integration (Milestone 6.3)
8. 📋 Implement calendar event creation (Milestone 6.5)
9. 📋 Production deployment
10. 📋 Advanced features

---

*Last Updated: 2025-01-15*
*Status: Milestone 5 Complete - Ready for Web Interface or Text Integration*
