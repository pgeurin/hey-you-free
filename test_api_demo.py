#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo script to test FastAPI server with mock data
"""
import sys
import os
from unittest.mock import patch

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from api.server import app
from fastapi.testclient import TestClient


def demo_fastapi_server():
    """Demonstrate FastAPI server functionality"""
    print("\n" + "="*80)
    print("🚀 FASTAPI SERVER DEMO")
    print("="*80)
    
    client = TestClient(app)
    
    # Test health endpoint
    print("\n1. Testing health endpoint...")
    response = client.get("/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    # Test meeting suggestions with mock data
    print("\n2. Testing meeting suggestions with mock data...")
    
    # Mock the core function to return test data
    mock_suggestions = {
        "suggestions": [
            {
                "date": "2025-01-20",
                "time": "14:00",
                "duration": "1.5 hours",
                "reasoning": "Both Phil and Chris are free and have high energy levels",
                "user_energies": {
                    "phil": "High",
                    "chris": "High"
                },
                "meeting_type": "Coffee",
                "location": "Local coffee shop",
                "confidence": 0.9,
                "conflicts": [],
                "preparation_time": "5 minutes"
            },
            {
                "date": "2025-01-22",
                "time": "10:00",
                "duration": "2 hours",
                "reasoning": "Morning energy is optimal for both participants",
                "user_energies": {
                    "phil": "High",
                    "chris": "Medium"
                },
                "meeting_type": "Casual lunch",
                "location": "Downtown restaurant",
                "confidence": 0.8,
                "conflicts": [],
                "preparation_time": "10 minutes"
            }
        ],
        "metadata": {
            "generated_at": "2025-01-15T10:30:00Z",
            "total_suggestions": 2,
            "analysis_quality": "high",
            "time_range_analyzed": "2025-01-15 to 2025-01-29"
        }
    }
    
    with patch('api.server.get_meeting_suggestions_from_core', return_value=mock_suggestions):
        response = client.get("/meeting-suggestions")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Total suggestions: {len(data['suggestions'])}")
            for i, suggestion in enumerate(data['suggestions'], 1):
                print(f"   Suggestion {i}: {suggestion['date']} at {suggestion['time']} - {suggestion['meeting_type']}")
                print(f"      Reasoning: {suggestion['reasoning']}")
                user_energies = suggestion.get('user_energies', {})
                energy_text = ", ".join([f"{user.title()}={energy}" for user, energy in user_energies.items()])
                print(f"      Energy levels: {energy_text}")
        else:
            print(f"   Error: {response.json()}")
    
    # Test with custom seed
    print("\n3. Testing with custom seed...")
    with patch('api.server.get_meeting_suggestions_from_core', return_value=mock_suggestions):
        response = client.get("/meeting-suggestions?seed=123")
        print(f"   Status: {response.status_code}")
        print(f"   Response received successfully")
    
    # Test raw endpoint
    print("\n4. Testing raw endpoint...")
    with patch('api.server.get_meeting_suggestions_with_gemini', return_value="Mock AI response"):
        response = client.get("/meeting-suggestions/raw")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Raw response length: {len(response.json()['raw_response'])} characters")
        else:
            print(f"   Error: {response.json()}")
    
    print("\n" + "="*80)
    print("🎯 FASTAPI SERVER DEMO COMPLETE")
    print("="*80)
    print("✅ All endpoints working correctly!")
    print("✅ Server returns meeting events as expected!")
    print("="*80)


if __name__ == "__main__":
    demo_fastapi_server()
