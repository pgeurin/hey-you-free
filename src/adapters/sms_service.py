#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SMS service for Twilio integration
Handles SMS sending, receiving, and webhook processing
"""
import os
import json
from typing import Optional, Dict, Any, List
from datetime import datetime

try:
    from twilio.rest import Client
    from twilio.request_validator import RequestValidator
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False


class SMSService:
    """Service for handling SMS operations with Twilio"""
    
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.phone_number = os.getenv('TWILIO_PHONE_NUMBER')
        self.webhook_url = os.getenv('TWILIO_WEBHOOK_URL', 'http://localhost:8000/webhooks/sms')
        
        # Initialize Twilio client if credentials are available
        if self.is_configured():
            self.client = Client(self.account_sid, self.auth_token)
        else:
            self.client = None
    
    def is_configured(self) -> bool:
        """Check if SMS service is properly configured"""
        return (
            TWILIO_AVAILABLE and 
            self.account_sid and 
            self.auth_token and 
            self.phone_number
        )
    
    def send_sms(self, to_phone: str, message: str, from_phone: Optional[str] = None) -> Dict[str, Any]:
        """Send SMS message"""
        if not self.is_configured():
            return {
                'success': False,
                'error': 'SMS service not configured',
                'message': 'Twilio credentials not available'
            }
        
        try:
            from_number = from_phone or self.phone_number
            
            # Send the message
            message_obj = self.client.messages.create(
                body=message,
                from_=from_number,
                to=to_phone
            )
            
            return {
                'success': True,
                'message_id': message_obj.sid,
                'status': message_obj.status,
                'to': message_obj.to,
                'from': message_obj.from_,
                'body': message_obj.body,
                'created_at': message_obj.date_created.isoformat() if message_obj.date_created else None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to send SMS'
            }
    
    def validate_webhook_request(self, request_data: Dict[str, Any], signature: str, url: str) -> bool:
        """Validate Twilio webhook request signature"""
        if not self.is_configured():
            return False
        
        try:
            validator = RequestValidator(self.auth_token)
            return validator.validate(url, request_data, signature)
        except Exception:
            return False
    
    def parse_incoming_message(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse incoming SMS webhook data"""
        return {
            'message_id': webhook_data.get('MessageSid'),
            'from_phone': webhook_data.get('From'),
            'to_phone': webhook_data.get('To'),
            'message_body': webhook_data.get('Body', ''),
            'message_status': webhook_data.get('MessageStatus'),
            'num_media': int(webhook_data.get('NumMedia', 0)),
            'media_urls': webhook_data.get('MediaUrl0'),  # Simplified for single media
            'received_at': datetime.utcnow().isoformat()
        }
    
    def get_message_status(self, message_id: str) -> Dict[str, Any]:
        """Get status of a sent message"""
        if not self.is_configured():
            return {
                'success': False,
                'error': 'SMS service not configured'
            }
        
        try:
            message = self.client.messages(message_id).fetch()
            return {
                'success': True,
                'message_id': message.sid,
                'status': message.status,
                'error_code': message.error_code,
                'error_message': message.error_message,
                'price': message.price,
                'price_unit': message.price_unit,
                'date_created': message.date_created.isoformat() if message.date_created else None,
                'date_sent': message.date_sent.isoformat() if message.date_sent else None,
                'date_updated': message.date_updated.isoformat() if message.date_updated else None
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get Twilio account information"""
        if not self.is_configured():
            return {
                'success': False,
                'error': 'SMS service not configured'
            }
        
        try:
            account = self.client.api.accounts(self.account_sid).fetch()
            return {
                'success': True,
                'account_sid': account.sid,
                'friendly_name': account.friendly_name,
                'status': account.status,
                'type': account.type
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


# Global SMS service instance
sms_service = SMSService()


def get_sms_service() -> SMSService:
    """Get SMS service instance"""
    return sms_service


def is_sms_available() -> bool:
    """Check if SMS service is available and configured"""
    return TWILIO_AVAILABLE and sms_service.is_configured()


if __name__ == "__main__":
    # Test SMS configuration
    print("🔍 Testing SMS configuration...")
    
    if not TWILIO_AVAILABLE:
        print("❌ Twilio dependencies not installed")
        print("💡 Run: mamba install twilio")
    else:
        print("✅ Twilio dependencies available")
    
    if sms_service.is_configured():
        print("✅ SMS service is configured")
        try:
            account_info = sms_service.get_account_info()
            if account_info['success']:
                print(f"📱 Account: {account_info['friendly_name']}")
                print(f"📞 Phone: {sms_service.phone_number}")
            else:
                print(f"❌ Error getting account info: {account_info['error']}")
        except Exception as e:
            print(f"❌ Error testing SMS service: {e}")
    else:
        print("❌ SMS service not configured")
        print("💡 Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER environment variables")
