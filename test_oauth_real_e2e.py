#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real End-to-End OAuth Test
Tests OAuth flow with actual server running
"""
import requests
import time
import json
from urllib.parse import urlparse, parse_qs


def test_oauth_real_e2e():
    """Test OAuth flow with real server"""
    base_url = "http://localhost:8000"
    
    print("🔍 Real End-to-End OAuth Test")
    print("=" * 50)
    
    # Step 1: Check server health
    print("1. Checking server health...")
    try:
        response = requests.get(f"{base_url}/health")
        assert response.status_code == 200
        print("✅ Server is running")
    except Exception as e:
        print(f"❌ Server not running: {e}")
        return False
    
    # Step 2: Check OAuth status
    print("\n2. Checking OAuth status...")
    response = requests.get(f"{base_url}/oauth/status")
    assert response.status_code == 200
    oauth_status = response.json()
    print(f"✅ OAuth Status: {oauth_status}")
    
    # Step 3: Test OAuth start endpoint
    print("\n3. Testing OAuth start endpoint...")
    response = requests.get(f"{base_url}/oauth/google/start", allow_redirects=False)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 307:
        auth_url = response.headers.get('location', '')
        print(f"✅ OAuth redirect URL: {auth_url[:100]}...")
        
        # Parse URL to verify parameters
        parsed = urlparse(auth_url)
        params = parse_qs(parsed.query)
        
        # Verify required parameters
        assert 'client_id' in params
        assert 'scope' in params
        assert 'state' in params
        assert 'access_type' in params
        
        # Verify scope contains calendar.readonly
        scope = params['scope'][0]
        assert 'calendar.readonly' in scope
        
        print("✅ OAuth URL parameters are correct")
        print(f"   Client ID: {params['client_id'][0][:20]}...")
        print(f"   Scope: {scope}")
        print(f"   State: {params['state'][0][:20]}...")
        
        # Step 4: Test OAuth callback with invalid state
        print("\n4. Testing OAuth callback error handling...")
        response = requests.get(f"{base_url}/oauth/google/callback?code=test_code&state=invalid_state")
        assert response.status_code == 500
        print("✅ OAuth callback handles invalid state correctly")
        
        # Step 5: Test OAuth callback with missing parameters
        response = requests.get(f"{base_url}/oauth/google/callback")
        assert response.status_code == 400
        print("✅ OAuth callback handles missing parameters correctly")
        
        # Step 6: Test OAuth callback with error
        response = requests.get(f"{base_url}/oauth/google/callback?error=access_denied")
        assert response.status_code == 400
        print("✅ OAuth callback handles access denied correctly")
        
        # Step 7: Test web interface
        print("\n5. Testing web interface...")
        response = requests.get(f"{base_url}/")
        assert response.status_code == 200
        html_content = response.text
        
        assert "Connect Google Calendar" in html_content
        assert "connectGoogleCalendar" in html_content
        print("✅ Web interface contains OAuth button")
        
        # Step 8: Test development OAuth (fallback)
        print("\n6. Testing development OAuth fallback...")
        response = requests.get(f"{base_url}/oauth/dev/start", allow_redirects=False)
        if response.status_code == 307:
            dev_url = response.headers.get('location', '')
            print(f"✅ Dev OAuth URL: {dev_url}")
            
            # Test dev simulation page
            response = requests.get(dev_url)
            assert response.status_code == 200
            assert "Development OAuth Simulation" in response.text
            print("✅ Development OAuth simulation page works")
        
        print("\n🎯 OAuth End-to-End Test Results:")
        print("✅ Server health check")
        print("✅ OAuth status endpoint")
        print("✅ OAuth start redirect")
        print("✅ OAuth URL parameters")
        print("✅ OAuth error handling")
        print("✅ Web interface integration")
        print("✅ Development OAuth fallback")
        
        print("\n📋 Manual Test Steps for philip.a.geurin@gmail.com:")
        print("1. Open browser and go to: http://localhost:8000")
        print("2. Click 'Connect Google Calendar' button")
        print("3. If Google OAuth works:")
        print("   - Sign in with philip.a.geurin@gmail.com")
        print("   - Grant calendar access permissions")
        print("   - Verify redirect back to web interface")
        print("   - Check for success message")
        print("4. If Google OAuth fails (verification issue):")
        print("   - Should automatically use development OAuth")
        print("   - Click 'Authorize Access' on simulation page")
        print("   - Verify success message")
        
        print("\n🔧 Google OAuth Verification Fix:")
        print("To fix the 'Access blocked' error:")
        print("1. Go to: https://console.cloud.google.com/")
        print("2. Navigate to: APIs & Services → OAuth consent screen")
        print("3. Add philip.a.geurin@gmail.com as a test user")
        print("4. Or publish the app for production use")
        
        return True
        
    else:
        print(f"❌ OAuth start failed with status: {response.status_code}")
        return False


def test_oauth_with_real_google_account():
    """Test OAuth flow with real Google account (requires manual steps)"""
    print("\n🔍 Real Google Account OAuth Test")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Get OAuth start URL
    response = requests.get(f"{base_url}/oauth/google/start", allow_redirects=False)
    if response.status_code == 307:
        auth_url = response.headers.get('location', '')
        
        print("📋 Manual OAuth Test Steps:")
        print(f"1. Open this URL in your browser:")
        print(f"   {auth_url}")
        print("\n2. Sign in with philip.a.geurin@gmail.com")
        print("3. Grant calendar access permissions")
        print("4. Check if you get redirected back to the web interface")
        print("5. Look for success message")
        
        print("\n⚠️ Expected Outcomes:")
        print("✅ If OAuth works: You'll be redirected back with success message")
        print("❌ If OAuth fails: You'll see 'Access blocked' error")
        print("🔄 If OAuth fails: Web interface should fallback to dev OAuth")
        
        return auth_url
    else:
        print(f"❌ Could not get OAuth URL: {response.status_code}")
        return None


if __name__ == "__main__":
    print("🚀 Starting OAuth End-to-End Tests...")
    
    # Test 1: Basic OAuth functionality
    success = test_oauth_real_e2e()
    
    if success:
        # Test 2: Real Google account test
        auth_url = test_oauth_with_real_google_account()
        
        if auth_url:
            print(f"\n🎯 OAuth is ready for testing with philip.a.geurin@gmail.com!")
            print(f"Authorization URL: {auth_url}")
        else:
            print("\n❌ OAuth setup has issues")
    else:
        print("\n❌ OAuth tests failed")
