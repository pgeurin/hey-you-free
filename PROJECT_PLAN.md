# AI-Powered Event Scheduling Application

## Project Overview
An AI-powered backend service that analyzes two Google calendars and suggests optimal meeting times when both participants are free and would enjoy the activity together.

## Architecture
- **Clean Architecture**: Separate I/O from business logic
- **Functional Programming**: No OOP, snake_case naming
- **TDD Approach**: Write tests first, commit when passing
- **Backend Focus**: API service with Google Calendar integration

## Core Features

### Phase 1: Calendar Import & Processing
1. **Google Calendar API Integration**
   - OAuth2 authentication flow
   - Calendar data extraction
   - Event parsing and normalization

2. **Data Processing Pipeline**
   - Convert calendar events to structured text
   - Extract availability windows
   - Parse event metadata (title, duration, type)

### Phase 2: Multi-User Support
3. **User Management**
   - Create sample users from existing calendar data
   - User preference storage
   - Calendar association mapping

### Phase 3: AI-Powered Suggestions
4. **Availability Analysis**
   - Find common free time slots
   - Conflict detection and resolution
   - Time zone handling

5. **AI Suggestion Engine**
   - Activity recommendation based on preferences
   - Optimal time slot selection
   - Context-aware suggestions

## Technical Stack
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Database**: SQLite (development) / PostgreSQL (production)
- **AI/ML**: Gemini AI API
- **Calendar**: Google Calendar API v3
- **Testing**: pytest
- **Environment**: mamba (butterfly)
- **Time Zone**: Seattle (PST/PDT)

## Project Structure
```
backend/
├── src/
│   ├── core/           # Business logic (no I/O)
│   ├── adapters/       # External integrations
│   ├── infrastructure/ # Database, config
│   └── api/           # FastAPI routes
├── tests/
├── requirements.txt
└── README.md
```

## Milestones

### Milestone 1: Single Calendar Import
- [ ] Set up Google Calendar API credentials
- [ ] Implement OAuth2 flow
- [ ] Extract calendar events (last 7 days + next 7 days)
- [ ] Save raw JSON results to file
- [ ] Write tests for calendar parsing

### Milestone 2: Text Visualization
- [ ] Create calendar text formatter
- [ ] Display events in readable format
- [ ] Add time zone support
- [ ] Test text output accuracy

### Milestone 3: Multi-User Support
- [ ] Design user data model
- [ ] Create sample user generator
- [ ] Implement user calendar mapping
- [ ] Test multi-user scenarios

### Milestone 4: AI Suggestion Engine
- [ ] Design availability algorithm (focus on free time detection)
- [ ] Implement free time detection for both users
- [ ] Integrate Gemini AI for social activity suggestions
- [ ] Test suggestion accuracy

## Questions for Refinement

1. **Calendar Scope**: ✅ **DECIDED**: Last 7 days + next 7 days (14-day window)

2. **Event Types**: ✅ **DECIDED**: Social events only

3. **AI Integration**: ✅ **DECIDED**: Gemini AI

4. **User Preferences**: ✅ **DECIDED**: Use calendar history for preferences, but focus on free time detection for now

5. **Time Zones**: ✅ **DECIDED**: Assume both users in Seattle (PST/PDT)

6. **Data Storage**: ✅ **DECIDED**: Save raw JSON results for testing

## Next Steps
1. Set up development environment
2. Implement Google Calendar API integration
3. Create basic calendar parsing functionality
4. Write comprehensive tests

---

*Last Updated: [Current Date]*
*Status: Planning Phase*
