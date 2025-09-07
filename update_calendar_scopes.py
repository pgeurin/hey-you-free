#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Update Google Calendar scopes to include event creation
"""
import json
from pathlib import Path


def update_token_scopes():
    """Update token.json to include calendar.events scope"""
    print("🔧 Updating Google Calendar scopes for event creation...")
    
    token_path = Path("token.json")
    if not token_path.exists():
        print("❌ token.json not found")
        return False
    
    # Read current token
    with open(token_path, 'r') as f:
        token_data = json.load(f)
    
    print(f"📋 Current scopes: {token_data.get('scopes', [])}")
    
    # Add calendar.events scope if not present
    current_scopes = token_data.get('scopes', [])
    if 'https://www.googleapis.com/auth/calendar.events' not in current_scopes:
        current_scopes.append('https://www.googleapis.com/auth/calendar.events')
        token_data['scopes'] = current_scopes
        
        # Write updated token
        with open(token_path, 'w') as f:
            json.dump(token_data, f, indent=2)
        
        print("✅ Added calendar.events scope to token.json")
        print(f"📋 Updated scopes: {current_scopes}")
        return True
    else:
        print("✅ calendar.events scope already present")
        return True


def main():
    """Update scopes and test"""
    print("🎯 Google Calendar Scopes Update")
    print("=" * 40)
    
    success = update_token_scopes()
    
    if success:
        print("\n✅ Scopes updated successfully!")
        print("📝 Note: You may need to re-authorize the application")
        print("   for the new scopes to take effect")
    else:
        print("\n❌ Failed to update scopes")


if __name__ == "__main__":
    main()
