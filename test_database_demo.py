#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo of database integration with user management
"""
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from infrastructure.database import DatabaseManager
from api.user_management import UserManager
from core.meeting_scheduler import create_ai_prompt, format_events_for_ai
from infrastructure.calendar_loader import load_calendar_data
from adapters.gemini_client import get_deterministic_meeting_suggestions, parse_gemini_response


def demo_database_integration():
    """Demo the database integration functionality"""
    print("🚀 DATABASE INTEGRATION DEMO")
    print("=" * 50)
    
    # Initialize database
    db_manager = DatabaseManager(":memory:")
    db_manager.initialize_database()
    
    try:
        # Create test users
        print("\n📝 Creating test users...")
        with db_manager.transaction():
            user1_id = db_manager.create_user(
                name="alice",
                calendar_id="alice@gmail.com",
                phone_number="+1234567890",
                email="alice@example.com"
            )
            user2_id = db_manager.create_user(
                name="bob",
                calendar_id="bob@gmail.com", 
                phone_number="+1987654321",
                email="bob@example.com"
            )
        
        print(f"✅ Created users: alice (ID: {user1_id}), bob (ID: {user2_id})")
        
        # Look up users by name
        print("\n🔍 Looking up users by name...")
        alice = db_manager.get_user_by_name("alice")
        bob = db_manager.get_user_by_name("bob")
        
        print(f"✅ Found alice: {alice['name']} ({alice['email']})")
        print(f"✅ Found bob: {bob['name']} ({bob['email']})")
        
        # Load calendar data (using existing files for demo)
        print("\n📅 Loading calendar data...")
        try:
            alice_events = load_calendar_data("data/calendar_events_raw.json")
            bob_events = load_calendar_data("data/chris_calendar_events_raw.json")
            print(f"✅ Loaded {len(alice_events)} events for alice")
            print(f"✅ Loaded {len(bob_events)} events for bob")
        except FileNotFoundError:
            print("⚠️  Calendar files not found, using sample data")
            alice_events = [{"summary": "Sample Event", "start": {"dateTime": "2025-01-16T10:00:00Z"}}]
            bob_events = [{"summary": "Another Event", "start": {"dateTime": "2025-01-16T14:00:00Z"}}]
        
        # Format events for AI
        print("\n🤖 Formatting events for AI...")
        alice_formatted = format_events_for_ai(alice_events, "alice")
        bob_formatted = format_events_for_ai(bob_events, "bob")
        
        print(f"✅ Formatted alice events: {len(alice_formatted)} characters")
        print(f"✅ Formatted bob events: {len(bob_formatted)} characters")
        
        # Create AI prompt with user names
        print("\n📝 Creating AI prompt with user names...")
        prompt = create_ai_prompt(alice_events, bob_events, "alice", "bob")
        print(f"✅ Created prompt: {len(prompt)} characters")
        print(f"✅ Prompt contains 'ALICE' and 'BOB': {'ALICE' in prompt and 'BOB' in prompt}")
        
        # Store conversation context
        print("\n💬 Storing conversation context...")
        context_id = db_manager.store_conversation_context(
            user1_id, user2_id, 
            "We discussed meeting for coffee last week",
            "meeting_discussion"
        )
        print(f"✅ Stored conversation context (ID: {context_id})")
        
        # Retrieve conversation context
        context = db_manager.get_conversation_context(user1_id, user2_id)
        print(f"✅ Retrieved context: '{context['context_text']}'")
        
        # Create conversation
        print("\n🗣️  Creating conversation...")
        conv_id = db_manager.create_conversation(user1_id, user2_id)
        print(f"✅ Created conversation (ID: {conv_id})")
        
        # Get AI suggestions (mocked for demo)
        print("\n🧠 Getting AI suggestions...")
        try:
            ai_response = get_deterministic_meeting_suggestions(prompt, seed=42)
            if ai_response:
                suggestions = parse_gemini_response(ai_response, "alice", "bob")
                if suggestions:
                    print(f"✅ Generated {len(suggestions.get('suggestions', []))} meeting suggestions")
                    
                    # Store meeting suggestions
                    suggestion_id = db_manager.store_meeting_suggestion(
                        conv_id, user1_id, user2_id, suggestions
                    )
                    print(f"✅ Stored meeting suggestions (ID: {suggestion_id})")
                    
                    # Display first suggestion
                    first_suggestion = suggestions.get('suggestions', [{}])[0]
                    if first_suggestion:
                        print(f"📅 First suggestion: {first_suggestion.get('date')} at {first_suggestion.get('time')}")
                else:
                    print("⚠️  Failed to parse AI response")
            else:
                print("⚠️  No AI response received")
        except Exception as e:
            print(f"⚠️  AI suggestion generation failed: {e}")
        
        # List all users
        print("\n👥 Listing all users...")
        users = db_manager.list_users()
        for user in users:
            print(f"  - {user['name']} ({user['email']}) - Active: {user['is_active']}")
        
        print("\n🎉 Database integration demo completed successfully!")
        
    finally:
        db_manager.close()


if __name__ == "__main__":
    demo_database_integration()
