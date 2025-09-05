#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Environment setup script for Meeting Scheduler
Helps users configure their environment properly
"""
import os
import sys
import shutil
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.infrastructure.environment import (
    validate_environment,
    print_environment_status,
    get_api_key_status
)


def setup_environment():
    """Interactive environment setup"""
    print("\n" + "="*80)
    print("🚀 MEETING SCHEDULER ENVIRONMENT SETUP")
    print("="*80)
    
    # Check if .env file exists
    env_file = Path('.env')
    template_file = Path('env.template')
    
    if not env_file.exists():
        print("\n📄 Creating .env file from template...")
        if template_file.exists():
            shutil.copy(template_file, env_file)
            print(f"✅ Created .env file from {template_file}")
        else:
            print("❌ Template file not found. Creating basic .env file...")
            create_basic_env_file()
    else:
        print(f"✅ .env file already exists")
    
    # Check current environment status
    print("\n🔍 Checking current environment status...")
    is_ready = print_environment_status()
    
    if not is_ready:
        print("\n⚠️  Environment setup incomplete!")
        print("\n📝 Next steps:")
        
        api_status = get_api_key_status()
        if not api_status['available']:
            print("1. Get your Google Gemini API key from: https://makersuite.google.com/app/apikey")
            print("2. Add it to your .env file: GOOGLE_API_KEY=your_actual_api_key")
        
        print("3. Run this script again to verify setup")
        print("4. Start the server with: python -m uvicorn src.api.server:app --reload")
        
        return False
    else:
        print("\n🎉 Environment setup complete!")
        print("✅ Ready to start the server!")
        return True


def create_basic_env_file():
    """Create a basic .env file with required variables"""
    env_content = """# Meeting Scheduler Environment Configuration
# Fill in your actual values

# Google Gemini AI API Key (Required)
# Get your API key from: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=your_gemini_api_key_here

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=false

# Logging
LOG_LEVEL=INFO
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created basic .env file")


def check_environment_quick():
    """Quick environment check without interactive setup"""
    print("\n🔍 Quick Environment Check")
    print("-" * 40)
    
    is_valid, errors = validate_environment()
    api_status = get_api_key_status()
    
    print(f"Environment valid: {'✅ YES' if is_valid else '❌ NO'}")
    print(f"API key available: {'✅ YES' if api_status['available'] else '❌ NO'}")
    
    if errors:
        print("\n❌ Issues found:")
        for error in errors:
            print(f"   • {error}")
    
    if not api_status['available']:
        print(f"\n⚠️  API Key: {api_status['message']}")
    
    return is_valid and api_status['available']


def main():
    """Main setup function"""
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        # Quick check mode
        is_ready = check_environment_quick()
        sys.exit(0 if is_ready else 1)
    else:
        # Interactive setup mode
        is_ready = setup_environment()
        sys.exit(0 if is_ready else 1)


if __name__ == "__main__":
    main()
