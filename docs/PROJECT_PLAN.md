# AI-Powered Event Scheduling Application

## Overview
AI-powered backend service that analyzes two Google calendars and suggests optimal meeting times when both participants are free and would enjoy the activity together.

## Architecture
- Clean Architecture: Separate I/O from business logic
- Functional Programming: No OOP, snake_case naming
- TDD Approach: Write tests first, commit when passing
- Backend Focus: API service with Google Calendar integration

## Completed Features

### Calendar Import & Processing ✅
- Google Calendar API Integration
  - OAuth2 authentication flow ✅
  - Calendar data extraction ✅
  - Event parsing and normalization ✅
- Data Processing Pipeline
  - Convert calendar events to structured text ✅
  - Extract availability windows ✅
  - Parse event metadata (title, duration, type) ✅

### AI-Powered Suggestions ✅
- AI Suggestion Engine
  - Activity recommendation based on preferences ✅
  - Optimal time slot selection ✅
  - Context-aware suggestions ✅
  - Deterministic responses with seeding ✅
- Response Validation
  - JSON schema validation ✅
  - Energy level validation ✅
  - Meeting type validation ✅
  - Date/time format validation ✅

### API & Testing ✅
- FastAPI Backend
  - Health check endpoint ✅
  - Meeting suggestions endpoint ✅
  - CORS configuration ✅
  - Error handling ✅
- Comprehensive Testing
  - 80+ test functions across 8 test files ✅
  - True end-to-end testing ✅
  - API integration tests ✅
  - Environment setup tests ✅

## Technical Stack
- Language: Python 3.11+
- Framework: FastAPI
- Database: SQLite (development) / PostgreSQL (production)
- AI/ML: Gemini AI API
- Calendar: Google Calendar API v3
- Testing: pytest
- Environment: mamba (butterfly)
- Time Zone: Seattle (PST/PDT)

## Environment Configuration
- Environment File: `.env` in project root directory
- Template File: `env.template` (copy to `.env` and fill values)
- Auto-loading: `load_env.py` automatically loads `.env` if present
- Required Variables: `GOOGLE_API_KEY`, `SERVER_HOST`, `SERVER_PORT`

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

## Development Status

### Core Infrastructure ✅
Calendar Integration:
- Set up Google Calendar API credentials ✅
- Implement OAuth2 flow ✅
- Extract calendar events (last 7 days + next 7 days) ✅
- Save raw JSON results to file ✅
- Write tests for calendar parsing ✅

AI Integration:
- Create calendar text formatter ✅
- Display events in readable format ✅
- Add time zone support ✅
- Test text output accuracy ✅
- Integrate Gemini AI for suggestions ✅
- Implement deterministic responses with seeding ✅

API Backend:
- Design FastAPI server structure ✅
- Implement health check endpoint ✅
- Create meeting suggestions endpoint ✅
- Add CORS configuration ✅
- Test API integration ✅

Testing Framework:
- Write 80+ test functions ✅
- Implement true end-to-end testing ✅
- Add API integration tests ✅
- Create environment setup tests ✅
- Test validation and error handling ✅

### User Management & Database ✅
Database Integration:
- Database integration (SQLite/PostgreSQL) ✅
- User table with name, calendar_id, oauth_tokens ✅
- Database lookup for calendar names and OAuth credentials ✅
- User authentication system ✅
- API endpoints for user management ✅

User Management Features:
- Update format_events_for_ai() to accept user names ✅
- Update create_ai_prompt() to accept user names and optional time range parameters ✅
- Update get_meeting_suggestions() to use database lookup for user calendar data ✅
- Add conversation context storage and retrieval functionality ✅
- Update API endpoints to use new user management system ✅
- Test complete database integration with user management ✅

### Personality Testing ✅
- Make two new user calendars in testing env (a json file) ✅
  - give each different personalities and preferences ✅
- Make sure the event planner is typical ✅
- Created Alex (creative, flexible) and Sam (structured, professional) ✅
- Added comprehensive personality testing suite (10 new tests) ✅
- Verified AI adapts to different personality types ✅

### Web Interface ✅
Frontend Features:
- Static HTML page with form ✅
- Simple JavaScript for API calls ✅
- Basic CSS for styling ✅
- Server-side form handling ✅
- Event confirmation page ✅

OAuth Integration:
- Implement Google OAuth2 server-side flow ✅
- Create OAuth callback endpoints ✅
- Store user tokens in database ✅
- Update web interface with working "Connect Calendar" button ✅
- Add OAuth state management and security ✅
- Test complete OAuth flow end-to-end ✅

Event Enhancement:
- Add description field to event creation ✅
- Update API to handle event descriptions ✅
- Update web interface with description input ✅
- Validate and sanitize description input ✅

### Website Autofill ✅
- Default form values for testing (Phil, Chris, coffee, description) ✅
- Quick-fill buttons for different user combinations ✅
- JavaScript fillForm() function for easy form population ✅
- Makes testing much easier with pre-filled forms ✅

## Planned Features

- calendar event types don't need to be strictly enforced for the AI. remove that from testing and code. 

### Calendar Event Creation ✅
- Google Calendar API event creation ✅
- Automatic event addition to both users' calendars ✅
- Event details population (location, description, attendees) ✅
- Calendar conflict detection (just notify) ✅
- Event modification and cancellation
- Reminder and notification settings
- User clicks on suggested events to create calendar entries ✅

make each user have suggested friends
- 

make each use have autoform filling

### Text/SMS Integration
- SMS/Text messaging integration (Twilio or similar)
- AI chat interface for meeting coordination
- Script-based conversation flows
- Text-to-meeting-scheduler integration
- Conversation history storage
- Multi-user text chat capabilities
- Natural language processing for meeting requests
- Automated meeting suggestion responses via text
- Rate limiting for SMS (200 texts/day warning to admin)

### User Invitation System
- Email invitation system for new users
- "Connect your calendar" onboarding flow
- User discovery by name/email
- Pending invitation management
- Calendar connection status tracking

### Multi-User Group Planning
- Group creation and management
- Multi-user calendar analysis (3+ people)
- Group preference settings
- Group event suggestion algorithms
- Group confirmation workflow
- Group member management interface

### Smart Context & Learning
- User preference learning from past events
- Context-aware suggestion algorithms
- Personalized activity recommendations
- Time preference learning (morning/evening person)
- Activity type preferences (coffee, outdoor, dinner)
- Historical pattern analysis

### Production Readiness
- Rate limiting and security
- Production deployment
- Monitoring and logging
- Error handling and recovery

### Advanced Features
- Multi-user support
- Recurring meeting suggestions
- Email notifications
- Mobile app integration

## Current Status
- Core Functionality: Complete and tested
- API Backend: Complete and tested  
- Testing Coverage: Comprehensive (198 tests)
- Database Infrastructure: Complete
- User Management: Complete and tested
- Personality Testing: Complete and tested
- Web Interface: Complete and tested
- OAuth Integration: Complete and tested
- Event Description: Complete and tested
- Calendar Event Creation: Complete and tested
- Website Autofill: Complete and tested
- Text Integration: In progress
- Production Ready: In progress
- Advanced Features: Planned

## Next Steps
- Complete text/SMS integration
- Production deployment
- Advanced features

---

*Last Updated: 2025-01-15*
*Status: Website Autofill Complete - Next: SMS Integration*
