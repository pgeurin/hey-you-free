# Messaging Integration Plan

## Overview
Add comprehensive messaging capabilities to enable text-based AI interactions for meeting coordination.

## Database Schema Additions

### Core Messaging Tables
1. **`conversations`** - Groups messages between two users
2. **`messages`** - Individual text/SMS messages
3. **`meeting_suggestions`** - AI-generated meeting proposals
4. **`script_templates`** - Structured conversation flows

### Key Features
- **SMS Integration**: Twilio for sending/receiving texts
- **Conversation Management**: Thread messages between users
- **AI Response Generation**: Context-aware meeting suggestions
- **Script Following**: Structured conversation flows
- **Message Status Tracking**: Sent, delivered, read status

## Implementation Plan

### Phase 1: Database & Models
- [ ] Create database migration scripts
- [ ] Add SQLAlchemy models for new tables
- [ ] Create database connection utilities
- [ ] Add database tests

### Phase 2: Message Storage & Retrieval
- [ ] Implement message CRUD operations
- [ ] Add conversation management functions
- [ ] Create message history retrieval
- [ ] Add message status tracking

### Phase 3: SMS Integration
- [ ] Integrate Twilio SDK
- [ ] Add webhook endpoints for incoming SMS
- [ ] Implement outbound SMS sending
- [ ] Add SMS delivery status tracking

### Phase 4: AI Chat Interface
- [ ] Create chat message processing
- [ ] Add conversation context management
- [ ] Implement script-based responses
- [ ] Add meeting suggestion generation from chat

### Phase 5: API Endpoints
- [ ] `POST /messages` - Send message
- [ ] `GET /conversations/{id}/messages` - Get conversation history
- [ ] `POST /conversations` - Start new conversation
- [ ] `POST /webhooks/sms` - Twilio webhook
- [ ] `GET /conversations/{id}/suggestions` - Get meeting suggestions

## Message Flow Example

```
User A (Phil) → SMS: "Hey Chris, want to grab coffee this week?"
     ↓
Twilio Webhook → /webhooks/sms
     ↓
Store Message → messages table
     ↓
AI Processing → Generate contextual response
     ↓
Store Response → messages table
     ↓
Send SMS → Twilio API
     ↓
User B (Chris) ← SMS: "Sure! I'm free Tuesday 2pm or Wednesday 10am"
```

## Script Templates Structure

```json
{
  "name": "casual_coffee_invitation",
  "steps": [
    {
      "trigger": "coffee invitation",
      "response": "I'd love to grab coffee! Let me check our calendars...",
      "action": "generate_meeting_suggestions"
    },
    {
      "trigger": "time_confirmation",
      "response": "Perfect! I'll send you a calendar invite.",
      "action": "create_calendar_event"
    }
  ]
}
```

## Technical Requirements

### Dependencies
- `twilio` - SMS integration
- `sqlalchemy` - Database ORM
- `alembic` - Database migrations
- `pydantic` - Data validation

### Environment Variables
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_PHONE_NUMBER`
- `DATABASE_URL`

### Security Considerations
- Webhook signature verification
- Rate limiting on SMS endpoints
- User phone number validation
- Message content sanitization

## Testing Strategy
- Unit tests for message CRUD operations
- Integration tests for SMS webhooks
- End-to-end tests for conversation flows
- Mock Twilio API for development
