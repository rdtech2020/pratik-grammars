#!/usr/bin/env python3
"""
Comprehensive Test Suite

This script tests ALL routes from the new modular structure:
- System Routes
- Grammar Routes
- User Routes
- Database Routes
- Analytics Routes
- Swagger Documentation
"""

import json
import time
from datetime import datetime

import requests

# API Base URL
BASE_URL = "http://localhost:8000"


def test_system_routes():
    """Test system routes"""
    print("🔧 Testing System Routes...")
    print("-" * 30)

    # Test root endpoint
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Root endpoint: {data.get('message', 'N/A')}")
            print(f"   Developer: {data.get('developer', 'N/A')}")
            print(f"   Status: {data.get('status', 'N/A')}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")

    # Test health endpoint
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health endpoint: {data.get('status', 'N/A')}")
            print(f"   Model loaded: {data.get('model_loaded', 'N/A')}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")


def test_grammar_routes():
    """Test grammar correction routes"""
    print("\n🤖 Testing Grammar Routes...")
    print("-" * 30)

    # Test grammar correction with various cases
    test_texts = [
        "how is you?",
        "I goes to the store",
        "She don't like it",
        "They was happy",
        "hello my name ram",
    ]

    success_count = 0
    for i, text in enumerate(test_texts, 1):
        try:
            response = requests.post(
                f"{BASE_URL}/correct",
                json={"text": text},
                headers={"Content-Type": "application/json"},
            )
            if response.status_code == 200:
                data = response.json()
                original = data.get("original", "")
                corrected = data.get("corrected", "")

                if corrected != original:
                    print(f"✅ Test {i}: '{text}' → '{corrected}'")
                    success_count += 1
                else:
                    print(f"⚠️  Test {i}: '{text}' (no change)")
            else:
                print(f"❌ Test {i} failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Test {i} error: {e}")

    print(f"📊 Grammar tests: {success_count}/{len(test_texts)} passed")


def test_user_routes():
    """Test user management routes"""
    print("\n👤 Testing User Routes...")
    print("-" * 30)

    # Create unique test user
    timestamp = int(time.time())
    test_user = {
        "email": f"testuser_{timestamp}@example.com",
        "password": "testpass123",
        "full_name": "Test User",
    }

    user_id = None

    # Test user registration
    try:
        response = requests.post(
            f"{BASE_URL}/users/register",
            json=test_user,
            headers={"Content-Type": "application/json"},
        )
        if response.status_code == 201:
            data = response.json()
            user_id = data.get("id")
            print(f"✅ User registration: {data.get('email', 'N/A')} (ID: {user_id})")
        else:
            print(f"❌ User registration failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ User registration error: {e}")
        return

    # Test user login
    try:
        login_data = {"email": test_user["email"], "password": test_user["password"]}
        response = requests.post(
            f"{BASE_URL}/users/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
        )
        if response.status_code == 200:
            login_data = response.json()
            print(f"✅ User login: {login_data.get('user', {}).get('email', 'N/A')}")
        else:
            print(f"❌ User login failed: {response.status_code}")
    except Exception as e:
        print(f"❌ User login error: {e}")

    # Test get user by ID
    if user_id:
        try:
            response = requests.get(f"{BASE_URL}/users/{user_id}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Get user by ID: {data.get('email', 'N/A')}")
            else:
                print(f"❌ Get user by ID failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Get user by ID error: {e}")

    # Test list users
    try:
        response = requests.get(f"{BASE_URL}/users?page=1&per_page=5")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ List users: {data.get('total', 0)} total users")
        else:
            print(f"❌ List users failed: {response.status_code}")
    except Exception as e:
        print(f"❌ List users error: {e}")


def test_database_routes():
    """Test database operation routes"""
    print("\n📊 Testing Database Routes...")
    print("-" * 30)

    # Test list corrections
    try:
        response = requests.get(f"{BASE_URL}/corrections?page=1&per_page=5")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ List corrections: {data.get('total', 0)} total corrections")
        else:
            print(f"❌ List corrections failed: {response.status_code}")
    except Exception as e:
        print(f"❌ List corrections error: {e}")

    # Test recent corrections
    try:
        response = requests.get(f"{BASE_URL}/corrections/recent?limit=3")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Recent corrections: {len(data)} corrections")
        else:
            print(f"❌ Recent corrections failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Recent corrections error: {e}")

    # Test search corrections
    try:
        response = requests.get(
            f"{BASE_URL}/corrections/search?query=store&page=1&per_page=5"
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search corrections: {len(data)} results for 'store'")
        else:
            print(f"❌ Search corrections failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Search corrections error: {e}")

    # Test date range corrections
    today = datetime.now().strftime("%Y-%m-%d")
    try:
        response = requests.get(
            f"{BASE_URL}/corrections/date-range?start_date={today}&end_date={today}"
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Date range corrections: {len(data)} corrections for today")
        else:
            print(f"❌ Date range corrections failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Date range corrections error: {e}")

    # Test get specific correction (using ID 1 as example)
    try:
        response = requests.get(f"{BASE_URL}/corrections/1")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Get correction by ID: {data.get('id', 'N/A')}")
        else:
            print(f"❌ Get correction by ID failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Get correction by ID error: {e}")


def test_analytics_routes():
    """Test analytics routes"""
    print("\n📈 Testing Analytics Routes...")
    print("-" * 30)

    # Test database stats
    try:
        response = requests.get(f"{BASE_URL}/analytics/stats")
        if response.status_code == 200:
            data = response.json()
            print(
                f"✅ Database stats: {data.get('total_corrections', 0)} corrections, {data.get('total_users', 0)} users"
            )
        else:
            print(f"❌ Database stats failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Database stats error: {e}")

    # Test user corrections (using user ID 1 as example)
    try:
        response = requests.get(f"{BASE_URL}/analytics/users/1/corrections?limit=5")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ User corrections: {len(data)} corrections for user 1")
        else:
            print(f"❌ User corrections failed: {response.status_code}")
    except Exception as e:
        print(f"❌ User corrections error: {e}")

    # Test user correction count
    try:
        response = requests.get(f"{BASE_URL}/analytics/users/1/correction-count")
        if response.status_code == 200:
            data = response.json()
            print(
                f"✅ User correction count: {data.get('total_corrections', 0)} for user 1"
            )
        else:
            print(f"❌ User correction count failed: {response.status_code}")
    except Exception as e:
        print(f"❌ User correction count error: {e}")


def test_swagger_documentation():
    """Test Swagger documentation"""
    print("\n📚 Testing Swagger Documentation...")
    print("-" * 30)

    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ Swagger documentation accessible")
        else:
            print(f"❌ Swagger documentation failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Swagger documentation error: {e}")

    try:
        response = requests.get(f"{BASE_URL}/openapi.json")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ OpenAPI schema: {data.get('info', {}).get('title', 'N/A')}")
        else:
            print(f"❌ OpenAPI schema failed: {response.status_code}")
    except Exception as e:
        print(f"❌ OpenAPI schema error: {e}")


def test_error_scenarios():
    """Test various error scenarios"""
    print("\n🚨 Testing Error Scenarios...")
    print("-" * 30)

    # Test invalid user ID
    try:
        response = requests.get(f"{BASE_URL}/users/99999")
        if response.status_code == 404:
            print("✅ 404 error handling: User not found")
        else:
            print(f"⚠️  Unexpected status for invalid user: {response.status_code}")
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")

    # Test invalid correction ID
    try:
        response = requests.get(f"{BASE_URL}/corrections/99999")
        if response.status_code == 404:
            print("✅ 404 error handling: Correction not found")
        else:
            print(
                f"⚠️  Unexpected status for invalid correction: {response.status_code}"
            )
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")

    # Test invalid date format
    try:
        response = requests.get(
            f"{BASE_URL}/corrections/date-range?start_date=invalid&end_date=invalid"
        )
        if response.status_code == 400:
            print("✅ 400 error handling: Invalid date format")
        else:
            print(f"⚠️  Unexpected status for invalid date: {response.status_code}")
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")


def main():
    """Main test function"""
    print("🚀 Comprehensive Route Structure Testing")
    print("=" * 60)
    print("Testing ALL routes from the new modular structure:")
    print("✅ System Routes (src/grammar_app/routes/system.py)")
    print("✅ Grammar Routes (src/grammar_app/routes/grammar.py)")
    print("✅ User Routes (src/grammar_app/routes/users.py)")
    print("✅ Database Routes (src/grammar_app/routes/database.py)")
    print("✅ Analytics Routes (src/grammar_app/routes/analytics.py)")
    print("=" * 60)

    # Test all route categories
    test_system_routes()
    test_grammar_routes()
    test_user_routes()
    test_database_routes()
    test_analytics_routes()
    test_swagger_documentation()
    test_error_scenarios()

    print("\n" + "=" * 60)
    print("✅ COMPREHENSIVE TESTING COMPLETE!")
    print("\n📋 New Route Structure Summary:")
    print("   🏗️  Main App: main.py (clean and organized)")
    print("   🔧 Grammar: src/grammar_app/routes/grammar.py")
    print("   👤 Users: src/grammar_app/routes/users.py")
    print("   📊 Database: src/grammar_app/routes/database.py")
    print("   📈 Analytics: src/grammar_app/routes/analytics.py")
    print("   🖥️  System: src/grammar_app/routes/system.py")
    print("   📦 Package: src/grammar_app/routes/__init__.py")
    print("\n🎯 Benefits of New Structure:")
    print("   ✅ Better organization and maintainability")
    print("   ✅ Easier to add new endpoints")
    print("   ✅ Cleaner main.py file")
    print("   ✅ Better separation of concerns")
    print("   ✅ Easier testing and debugging")


if __name__ == "__main__":
    main()
