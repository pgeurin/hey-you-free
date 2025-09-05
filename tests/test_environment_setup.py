#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for environment setup and validation
"""
import pytest
import os
from unittest.mock import patch
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.infrastructure.environment import (
    validate_environment,
    load_environment_config,
    get_required_env_vars,
    check_api_key_availability
)


class TestEnvironmentSetup:
    """Test environment setup and validation"""
    
    def test_validate_environment_with_all_vars(self):
        """Test environment validation with all required variables"""
        with patch.dict(os.environ, {
            'GOOGLE_API_KEY': 'test_api_key_123',
            'SERVER_HOST': '0.0.0.0',
            'SERVER_PORT': '8000',
            'LOG_LEVEL': 'INFO'
        }):
            is_valid, errors = validate_environment()
            assert is_valid is True
            assert len(errors) == 0
    
    def test_validate_environment_missing_api_key(self):
        """Test environment validation with missing API key"""
        with patch.dict(os.environ, {
            'SERVER_HOST': '0.0.0.0',
            'SERVER_PORT': '8000'
        }, clear=True):
            is_valid, errors = validate_environment(load_dotenv_file=False)
            assert is_valid is False
            assert 'GOOGLE_API_KEY' in errors[0]
    
    def test_validate_environment_invalid_port(self):
        """Test environment validation with invalid port"""
        with patch.dict(os.environ, {
            'GOOGLE_API_KEY': 'test_api_key_123',
            'SERVER_PORT': 'invalid_port'
        }):
            is_valid, errors = validate_environment(load_dotenv_file=False)
            assert is_valid is False
            assert 'SERVER_PORT' in errors[0]
    
    def test_load_environment_config(self):
        """Test loading environment configuration"""
        with patch.dict(os.environ, {
            'GOOGLE_API_KEY': 'test_api_key_123',
            'SERVER_HOST': '127.0.0.1',
            'SERVER_PORT': '9000',
            'LOG_LEVEL': 'DEBUG'
        }):
            config = load_environment_config()
            assert config['GOOGLE_API_KEY'] == 'test_api_key_123'
            assert config['SERVER_HOST'] == '127.0.0.1'
            assert config['SERVER_PORT'] == 9000
            assert config['LOG_LEVEL'] == 'DEBUG'
    
    def test_get_required_env_vars(self):
        """Test getting list of required environment variables"""
        required_vars = get_required_env_vars()
        assert 'GOOGLE_API_KEY' in required_vars
        assert 'SERVER_HOST' in required_vars
        assert 'SERVER_PORT' in required_vars
        assert len(required_vars) >= 3
    
    def test_check_api_key_availability(self):
        """Test API key availability check"""
        with patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key'}):
            is_available = check_api_key_availability(load_dotenv_file=False)
            assert is_available is True
        
        with patch.dict(os.environ, {}, clear=True):
            is_available = check_api_key_availability(load_dotenv_file=False)
            assert is_available is False
    
    def test_environment_defaults(self):
        """Test environment configuration defaults"""
        with patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key'}, clear=True):
            config = load_environment_config(load_dotenv_file=False)
            assert config['SERVER_HOST'] == '0.0.0.0'  # default
            assert config['SERVER_PORT'] == 8000  # default
            assert config['LOG_LEVEL'] == 'INFO'  # default
            assert config['DEBUG'] is False  # default


def test_run_environment_test_suite():
    """Run the complete environment test suite"""
    print("\n" + "="*80)
    print("🚀 RUNNING ENVIRONMENT SETUP TEST SUITE")
    print("="*80)
    
    test_instance = TestEnvironmentSetup()
    
    try:
        test_instance.test_validate_environment_with_all_vars()
        print("✅ Environment validation with all vars test passed")
        
        test_instance.test_validate_environment_missing_api_key()
        print("✅ Environment validation missing API key test passed")
        
        test_instance.test_validate_environment_invalid_port()
        print("✅ Environment validation invalid port test passed")
        
        test_instance.test_load_environment_config()
        print("✅ Load environment config test passed")
        
        test_instance.test_get_required_env_vars()
        print("✅ Get required env vars test passed")
        
        test_instance.test_check_api_key_availability()
        print("✅ Check API key availability test passed")
        
        test_instance.test_environment_defaults()
        print("✅ Environment defaults test passed")
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        raise
    
    print("\n" + "="*80)
    print("🎯 ENVIRONMENT SETUP TEST SUITE COMPLETE")
    print("="*80)


if __name__ == "__main__":
    test_run_environment_test_suite()
