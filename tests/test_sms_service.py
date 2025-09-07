#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test SMS service functionality
Tests Twilio integration, webhook handling, and message processing
"""
import pytest
import os
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add src to path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from adapters.sms_service import SMSService, get_sms_service, is_sms_available


class TestSMSService:
    """Test SMS service functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.sms_service = SMSService()
    
    def test_sms_service_initialization(self):
        """Test SMS service initializes correctly"""
        assert isinstance(self.sms_service, SMSService)
        assert hasattr(self.sms_service, 'account_sid')
        assert hasattr(self.sms_service, 'auth_token')
        assert hasattr(self.sms_service, 'phone_number')
        assert hasattr(self.sms_service, 'webhook_url')
    
    def test_is_configured_without_credentials(self):
        """Test is_configured returns False without credentials"""
        with patch.dict(os.environ, {}, clear=True):
            sms_service = SMSService()
            assert not sms_service.is_configured()
    
    def test_is_configured_with_credentials(self):
        """Test is_configured returns True with credentials"""
        with patch.dict(os.environ, {
            'TWILIO_ACCOUNT_SID': 'test_sid',
            'TWILIO_AUTH_TOKEN': 'test_token',
            'TWILIO_PHONE_NUMBER': '+1234567890'
        }):
            with patch('adapters.sms_service.TWILIO_AVAILABLE', True):
                sms_service = SMSService()
                assert sms_service.is_configured()
    
    def test_send_sms_not_configured(self):
        """Test send_sms returns error when not configured"""
        with patch.dict(os.environ, {}, clear=True):
            sms_service = SMSService()
            result = sms_service.send_sms('+1234567890', 'Test message')
            
            assert not result['success']
            assert 'SMS service not configured' in result['error']
    
    @patch('adapters.sms_service.TWILIO_AVAILABLE', True)
    def test_send_sms_success(self):
        """Test successful SMS sending"""
        with patch.dict(os.environ, {
            'TWILIO_ACCOUNT_SID': 'test_sid',
            'TWILIO_AUTH_TOKEN': 'test_token',
            'TWILIO_PHONE_NUMBER': '+1234567890'
        }):
            # Mock Twilio client and message
            mock_message = Mock()
            mock_message.sid = 'test_message_id'
            mock_message.status = 'sent'
            mock_message.to = '+1234567890'
            mock_message.from_ = '+1234567890'
            mock_message.body = 'Test message'
            mock_message.date_created = datetime.utcnow()
            
            mock_client = Mock()
            mock_client.messages.create.return_value = mock_message
            
            sms_service = SMSService()
            sms_service.client = mock_client
            
            result = sms_service.send_sms('+1234567890', 'Test message')
            
            assert result['success']
            assert result['message_id'] == 'test_message_id'
            assert result['status'] == 'sent'
            assert result['to'] == '+1234567890'
            assert result['from'] == '+1234567890'
            assert result['body'] == 'Test message'
    
    @patch('adapters.sms_service.TWILIO_AVAILABLE', True)
    def test_send_sms_failure(self):
        """Test SMS sending failure"""
        with patch.dict(os.environ, {
            'TWILIO_ACCOUNT_SID': 'test_sid',
            'TWILIO_AUTH_TOKEN': 'test_token',
            'TWILIO_PHONE_NUMBER': '+1234567890'
        }):
            # Mock Twilio client to raise exception
            mock_client = Mock()
            mock_client.messages.create.side_effect = Exception('Twilio error')
            
            sms_service = SMSService()
            sms_service.client = mock_client
            
            result = sms_service.send_sms('+1234567890', 'Test message')
            
            assert not result['success']
            assert 'Twilio error' in result['error']
    
    def test_parse_incoming_message(self):
        """Test parsing incoming SMS webhook data"""
        webhook_data = {
            'MessageSid': 'test_message_id',
            'From': '+1234567890',
            'To': '+0987654321',
            'Body': 'Hello world',
            'MessageStatus': 'received',
            'NumMedia': '0'
        }
        
        result = self.sms_service.parse_incoming_message(webhook_data)
        
        assert result['message_id'] == 'test_message_id'
        assert result['from_phone'] == '+1234567890'
        assert result['to_phone'] == '+0987654321'
        assert result['message_body'] == 'Hello world'
        assert result['message_status'] == 'received'
        assert result['num_media'] == 0
        assert 'received_at' in result
    
    def test_validate_webhook_request_not_configured(self):
        """Test webhook validation when not configured"""
        with patch.dict(os.environ, {}, clear=True):
            sms_service = SMSService()
            result = sms_service.validate_webhook_request({}, 'signature', 'url')
            assert not result
    
    @patch('adapters.sms_service.TWILIO_AVAILABLE', True)
    def test_validate_webhook_request_configured(self):
        """Test webhook validation when configured"""
        with patch.dict(os.environ, {
            'TWILIO_ACCOUNT_SID': 'test_sid',
            'TWILIO_AUTH_TOKEN': 'test_token',
            'TWILIO_PHONE_NUMBER': '+1234567890'
        }):
            with patch('adapters.sms_service.RequestValidator') as mock_validator:
                mock_validator_instance = Mock()
                mock_validator_instance.validate.return_value = True
                mock_validator.return_value = mock_validator_instance
                
                sms_service = SMSService()
                result = sms_service.validate_webhook_request({}, 'signature', 'url')
                
                assert result
                mock_validator_instance.validate.assert_called_once()
    
    @patch('adapters.sms_service.TWILIO_AVAILABLE', True)
    def test_get_message_status_success(self):
        """Test getting message status successfully"""
        with patch.dict(os.environ, {
            'TWILIO_ACCOUNT_SID': 'test_sid',
            'TWILIO_AUTH_TOKEN': 'test_token',
            'TWILIO_PHONE_NUMBER': '+1234567890'
        }):
            # Mock Twilio message
            mock_message = Mock()
            mock_message.sid = 'test_message_id'
            mock_message.status = 'delivered'
            mock_message.error_code = None
            mock_message.error_message = None
            mock_message.price = '0.01'
            mock_message.price_unit = 'USD'
            mock_message.date_created = datetime.utcnow()
            mock_message.date_sent = datetime.utcnow()
            mock_message.date_updated = datetime.utcnow()
            
            mock_client = Mock()
            mock_client.messages.return_value.fetch.return_value = mock_message
            
            sms_service = SMSService()
            sms_service.client = mock_client
            
            result = sms_service.get_message_status('test_message_id')
            
            assert result['success']
            assert result['message_id'] == 'test_message_id'
            assert result['status'] == 'delivered'
            assert result['price'] == '0.01'
    
    @patch('adapters.sms_service.TWILIO_AVAILABLE', True)
    def test_get_message_status_failure(self):
        """Test getting message status failure"""
        with patch.dict(os.environ, {
            'TWILIO_ACCOUNT_SID': 'test_sid',
            'TWILIO_AUTH_TOKEN': 'test_token',
            'TWILIO_PHONE_NUMBER': '+1234567890'
        }):
            # Mock Twilio client to raise exception
            mock_client = Mock()
            mock_client.messages.return_value.fetch.side_effect = Exception('Message not found')
            
            sms_service = SMSService()
            sms_service.client = mock_client
            
            result = sms_service.get_message_status('invalid_id')
            
            assert not result['success']
            assert 'Message not found' in result['error']
    
    @patch('adapters.sms_service.TWILIO_AVAILABLE', True)
    def test_get_account_info_success(self):
        """Test getting account info successfully"""
        with patch.dict(os.environ, {
            'TWILIO_ACCOUNT_SID': 'test_sid',
            'TWILIO_AUTH_TOKEN': 'test_token',
            'TWILIO_PHONE_NUMBER': '+1234567890'
        }):
            # Mock Twilio account
            mock_account = Mock()
            mock_account.sid = 'test_sid'
            mock_account.friendly_name = 'Test Account'
            mock_account.status = 'active'
            mock_account.type = 'Full'
            
            mock_client = Mock()
            mock_client.api.accounts.return_value.fetch.return_value = mock_account
            
            sms_service = SMSService()
            sms_service.client = mock_client
            
            result = sms_service.get_account_info()
            
            assert result['success']
            assert result['account_sid'] == 'test_sid'
            assert result['friendly_name'] == 'Test Account'
            assert result['status'] == 'active'
    
    def test_get_sms_service_singleton(self):
        """Test get_sms_service returns singleton instance"""
        service1 = get_sms_service()
        service2 = get_sms_service()
        assert service1 is service2
    
    def test_is_sms_available(self):
        """Test is_sms_available function"""
        # This will depend on environment and Twilio availability
        result = is_sms_available()
        assert isinstance(result, bool)


class TestSMSIntegration:
    """Test SMS integration with the API"""
    
    def test_sms_service_import(self):
        """Test SMS service can be imported"""
        from adapters.sms_service import SMSService, get_sms_service, is_sms_available
        assert SMSService is not None
        assert get_sms_service is not None
        assert is_sms_available is not None
    
    def test_sms_service_webhook_url_default(self):
        """Test default webhook URL is set correctly"""
        with patch.dict(os.environ, {}, clear=True):
            sms_service = SMSService()
            assert sms_service.webhook_url == 'http://localhost:8000/webhooks/sms'
    
    def test_sms_service_webhook_url_custom(self):
        """Test custom webhook URL is set correctly"""
        custom_url = 'https://example.com/webhooks/sms'
        with patch.dict(os.environ, {
            'TWILIO_WEBHOOK_URL': custom_url
        }):
            sms_service = SMSService()
            assert sms_service.webhook_url == custom_url


if __name__ == "__main__":
    # Run tests when executed directly
    pytest.main([__file__, "-v"])
