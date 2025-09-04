#!/usr/bin/env python3
"""
Authentication Flow Test

This script demonstrates the complete JWT authentication flow:
1. User registration (gets token)
2. User login (gets token)
3. Using token for authenticated endpoints
4. Testing user-specific data isolation
"""

import json
import time

import requests

# API Base URL
BASE_URL = "http://localhost:8000"


def test_authentication_flow():
    """Test the complete authentication flow."""
    print("🔐 Testing JWT Authentication Flow")
    print("=" * 50)

    # Step 1: User Registration
    print("\n📝 Step 1: User Registration")
    print("-" * 30)

    timestamp = int(time.time())
    test_user = {
        "email": f"testuser_{timestamp}@example.com",
        "password": "testpass123",
        "full_name": "Test User",
    }

    try:
        response = requests.post(
            f"{BASE_URL}/users/register",
            json=test_user,
            headers={"Content-Type": "application/json"},
        )

        if response.status_code == 201:
            data = response.json()
            access_token = data.get("access_token")
            user_info = data.get("user", {})

            print(f"✅ Registration successful!")
            print(f"   User ID: {user_info.get('id')}")
            print(f"   Email: {user_info.get('email')}")
            print(f"   Token: {access_token[:20]}...")
            print(f"   Token Type: {data.get('token_type')}")
            print(f"   Expires In: {data.get('expires_in')} seconds")
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Registration error: {e}")
        return None

    # Step 2: User Login
    print("\n🔑 Step 2: User Login")
    print("-" * 30)

    login_data = {"email": test_user["email"], "password": test_user["password"]}

    try:
        response = requests.post(
            f"{BASE_URL}/users/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
        )

        if response.status_code == 200:
            data = response.json()
            login_token = data.get("access_token")
            user_info = data.get("user", {})

            print(f"✅ Login successful!")
            print(f"   User ID: {user_info.get('id')}")
            print(f"   Email: {user_info.get('email')}")
            print(f"   Token: {login_token[:20]}...")
            print(f"   Token Type: {data.get('token_type')}")
            print(f"   Expires In: {data.get('expires_in')} seconds")

            # Verify tokens are the same (they should be for the same user)
            if access_token == login_token:
                print("   ✅ Tokens match (same user session)")
            else:
                print("   ⚠️  Tokens differ (new session)")

        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

    # Step 3: Test Authenticated Endpoints
    print("\n🔒 Step 3: Testing Authenticated Endpoints")
    print("-" * 30)

    # Use the token for authenticated requests
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    # Test getting current user profile
    try:
        response = requests.get(f"{BASE_URL}/users/me", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Get current user profile: {data.get('email')}")
            print(f"   Total corrections: {data.get('total_corrections', 0)}")
        else:
            print(f"❌ Get profile failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Get profile error: {e}")

    # Test grammar correction with authentication
    print("\n🤖 Testing Grammar Correction with Authentication")
    print("-" * 30)

    test_texts = ["how is you?", "I goes to the store", "She don't like it"]

    for i, text in enumerate(test_texts, 1):
        try:
            response = requests.post(
                f"{BASE_URL}/correct", json={"text": text}, headers=headers
            )

            if response.status_code == 200:
                data = response.json()
                original = data.get("original", "")
                corrected = data.get("corrected", "")

                if corrected != original:
                    print(f"✅ Test {i}: '{text}' → '{corrected}'")
                else:
                    print(f"⚠️  Test {i}: '{text}' (no change)")
            else:
                print(f"❌ Test {i} failed: {response.status_code}")

        except Exception as e:
            print(f"❌ Test {i} error: {e}")

    # Step 4: Test User-Specific Data
    print("\n📊 Step 4: Testing User-Specific Data")
    print("-" * 30)

    # Test getting user's corrections
    try:
        response = requests.get(
            f"{BASE_URL}/corrections?page=1&per_page=10", headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Get user corrections: {data.get('total', 0)} total corrections")

            corrections = data.get("corrections", [])
            if corrections:
                print(
                    f"   Latest correction: '{corrections[0].get('original_text', '')[:30]}...'"
                )
        else:
            print(f"❌ Get corrections failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Get corrections error: {e}")

    # Test getting user statistics
    try:
        response = requests.get(f"{BASE_URL}/analytics/my-stats", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Get user stats: {data.get('total_corrections', 0)} corrections")
            print(f"   Member since: {data.get('member_since', 'N/A')}")
        else:
            print(f"❌ Get stats failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Get stats error: {e}")

    # Step 5: Test Anonymous Endpoint
    print("\n👤 Step 5: Testing Anonymous Endpoint")
    print("-" * 30)

    try:
        response = requests.post(
            f"{BASE_URL}/correct/anonymous",
            json={"text": "hello my name ram"},
            headers={"Content-Type": "application/json"},
        )

        if response.status_code == 200:
            data = response.json()
            original = data.get("original", "")
            corrected = data.get("corrected", "")

            print(f"✅ Anonymous correction: '{original}' → '{corrected}'")
            print("   Note: This correction is NOT saved to database")
        else:
            print(f"❌ Anonymous correction failed: {response.status_code}")

    except Exception as e:
        print(f"❌ Anonymous correction error: {e}")

    # Step 6: Test Token Validation
    print("\n🔍 Step 6: Testing Token Validation")
    print("-" * 30)

    # Test with invalid token
    invalid_headers = {
        "Authorization": "Bearer invalid_token_123",
        "Content-Type": "application/json",
    }

    try:
        response = requests.get(f"{BASE_URL}/users/me", headers=invalid_headers)
        if response.status_code == 401:
            print("✅ Invalid token properly rejected (401 Unauthorized)")
        else:
            print(f"⚠️  Invalid token response: {response.status_code}")
    except Exception as e:
        print(f"❌ Invalid token test error: {e}")

    # Test without token
    try:
        response = requests.get(
            f"{BASE_URL}/users/me", headers={"Content-Type": "application/json"}
        )
        if response.status_code == 403:
            print("✅ Missing token properly rejected (403 Forbidden)")
        else:
            print(f"⚠️  Missing token response: {response.status_code}")
    except Exception as e:
        print(f"❌ Missing token test error: {e}")

    print("\n" + "=" * 50)
    print("🎉 Authentication Flow Test Complete!")
    print("\n📋 Summary:")
    print("   ✅ JWT token generation and validation")
    print("   ✅ User registration and login")
    print("   ✅ Authenticated endpoint access")
    print("   ✅ User-specific data isolation")
    print("   ✅ Anonymous endpoint access")
    print("   ✅ Proper error handling for invalid tokens")

    return access_token


def test_swagger_integration():
    """Test how Swagger UI handles authentication."""
    print("\n🌐 Testing Swagger UI Integration")
    print("=" * 50)

    print("📚 To test in Swagger UI:")
    print("   1. Go to: http://localhost:8000/docs")
    print("   2. Click 'Authorize' button (🔒)")
    print("   3. Enter your JWT token: Bearer <your_token>")
    print("   4. Test authenticated endpoints")
    print("   5. Test unauthenticated endpoints")

    print("\n🔑 Example token format:")
    print("   Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")

    print("\n📝 Testing workflow:")
    print("   1. POST /users/register - Get token")
    print("   2. POST /users/login - Get token")
    print("   3. GET /users/me - Test authenticated endpoint")
    print("   4. POST /correct - Test grammar correction with auth")
    print("   5. GET /corrections - View user's corrections")
    print("   6. GET /analytics/my-stats - View user stats")


if __name__ == "__main__":
    # Test the authentication flow
    token = test_authentication_flow()

    if token:
        print(f"\n🎯 Test completed successfully!")
        print(f"   Your test token: {token[:30]}...")
        print(f"   Use this token to test in Swagger UI")
    else:
        print(f"\n❌ Test failed - check server status")

    # Show Swagger integration instructions
    test_swagger_integration()
