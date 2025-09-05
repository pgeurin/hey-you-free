#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Environment configuration and validation
Clean Architecture: Infrastructure layer for environment management
"""
import os
from typing import Dict, List, Tuple, Any, Optional
from dotenv import load_dotenv


def load_environment_config(load_dotenv_file: bool = True) -> Dict[str, Any]:
    """Load and parse environment configuration with defaults"""
    # Load .env file if it exists (but don't override existing env vars)
    if load_dotenv_file:
        load_dotenv(override=False)
    
    # Helper function to safely convert to int
    def safe_int(value: str, default: int) -> int:
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    config = {
        # Required variables
        'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY'),
        
        # Server configuration with defaults
        'SERVER_HOST': os.getenv('SERVER_HOST', '0.0.0.0'),
        'SERVER_PORT': safe_int(os.getenv('SERVER_PORT', '8000'), 8000),
        'DEBUG': os.getenv('DEBUG', 'false').lower() == 'true',
        
        # Logging configuration
        'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
        'LOG_FORMAT': os.getenv('LOG_FORMAT', 'text'),
        
        # Rate limiting
        'RATE_LIMIT_PER_MINUTE': safe_int(os.getenv('RATE_LIMIT_PER_MINUTE', '60'), 60),
        
        # Security
        'SECRET_KEY': os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production'),
        'ALLOWED_ORIGINS': os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:8080'),
        
        # Optional Google Calendar integration
        'GOOGLE_CALENDAR_CREDENTIALS_FILE': os.getenv('GOOGLE_CALENDAR_CREDENTIALS_FILE'),
        'GOOGLE_CALENDAR_TOKEN_FILE': os.getenv('GOOGLE_CALENDAR_TOKEN_FILE'),
        
        # Database (for future use)
        'DATABASE_URL': os.getenv('DATABASE_URL', 'sqlite:///./meeting_scheduler.db'),
    }
    
    return config


def get_required_env_vars() -> List[str]:
    """Get list of required environment variables"""
    return [
        'GOOGLE_API_KEY',
        'SERVER_HOST',
        'SERVER_PORT'
    ]


def validate_environment(load_dotenv_file: bool = True) -> Tuple[bool, List[str]]:
    """Validate environment configuration"""
    errors = []
    config = load_environment_config(load_dotenv_file)
    
    # Check required variables
    required_vars = get_required_env_vars()
    for var in required_vars:
        if not config.get(var):
            errors.append(f"Missing required environment variable: {var}")
    
    # Validate specific values
    if config.get('SERVER_PORT'):
        # Check if the original env var was invalid (not converted by safe_int)
        original_port = os.getenv('SERVER_PORT', '8000')
        try:
            port = int(original_port)
            if not (1 <= port <= 65535):
                errors.append(f"Invalid SERVER_PORT: {port}. Must be between 1 and 65535")
        except (ValueError, TypeError):
            errors.append(f"Invalid SERVER_PORT: {original_port}. Must be a valid integer")
    
    # Validate log level
    valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    if config.get('LOG_LEVEL') and config['LOG_LEVEL'] not in valid_log_levels:
        errors.append(f"Invalid LOG_LEVEL: {config['LOG_LEVEL']}. Must be one of {valid_log_levels}")
    
    # Validate rate limit
    if config.get('RATE_LIMIT_PER_MINUTE'):
        try:
            rate_limit = int(config['RATE_LIMIT_PER_MINUTE'])
            if rate_limit <= 0:
                errors.append(f"Invalid RATE_LIMIT_PER_MINUTE: {rate_limit}. Must be positive")
        except (ValueError, TypeError):
            errors.append(f"Invalid RATE_LIMIT_PER_MINUTE: {config['RATE_LIMIT_PER_MINUTE']}. Must be a valid integer")
    
    return len(errors) == 0, errors


def check_api_key_availability(load_dotenv_file: bool = True) -> bool:
    """Check if Google API key is available"""
    config = load_environment_config(load_dotenv_file)
    api_key = config.get('GOOGLE_API_KEY')
    return (api_key is not None and 
            api_key.strip() != '' and 
            api_key != 'your_gemini_api_key_here' and
            api_key != 'your_api_key_here')


def get_api_key_status(load_dotenv_file: bool = True) -> Dict[str, Any]:
    """Get detailed API key status information"""
    config = load_environment_config(load_dotenv_file)
    api_key = config.get('GOOGLE_API_KEY')
    
    if not api_key:
        return {
            'available': False,
            'status': 'missing',
            'message': 'GOOGLE_API_KEY not found in environment'
        }
    
    if api_key == 'your_gemini_api_key_here':
        return {
            'available': False,
            'status': 'template',
            'message': 'GOOGLE_API_KEY is still set to template value'
        }
    
    if len(api_key) < 10:
        return {
            'available': False,
            'status': 'invalid',
            'message': 'GOOGLE_API_KEY appears to be too short'
        }
    
    return {
        'available': True,
        'status': 'valid',
        'message': 'GOOGLE_API_KEY is configured',
        'key_length': len(api_key)
    }


def print_environment_status():
    """Print current environment status"""
    print("\n" + "="*60)
    print("🔧 ENVIRONMENT STATUS")
    print("="*60)
    
    # Validate environment
    is_valid, errors = validate_environment()
    print(f"Environment valid: {'✅ YES' if is_valid else '❌ NO'}")
    
    if errors:
        print("\n❌ Errors found:")
        for error in errors:
            print(f"   • {error}")
    
    # Check API key status
    api_status = get_api_key_status()
    print(f"\n🔑 API Key status: {api_status['status'].upper()}")
    print(f"   {api_status['message']}")
    
    if api_status['available']:
        print(f"   Key length: {api_status['key_length']} characters")
    
    # Show configuration
    config = load_environment_config()
    print(f"\n⚙️  Configuration:")
    print(f"   Server: {config['SERVER_HOST']}:{config['SERVER_PORT']}")
    print(f"   Debug: {config['DEBUG']}")
    print(f"   Log level: {config['LOG_LEVEL']}")
    print(f"   Rate limit: {config['RATE_LIMIT_PER_MINUTE']} req/min")
    
    print("="*60)
    
    return is_valid and api_status['available']
