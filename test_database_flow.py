import requests
import json
import sys
import os
from datetime import datetime

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_backend_connection():
    """Test if the backend is running and accessible"""
    try:
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            print("✅ Backend is running successfully!")
            return True
        else:
            print(f"❌ Backend returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Make sure it's running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error testing backend: {e}")
        return False

def test_signup_to_database():
    """Test signup and verify data is saved to database"""
    print("\n🔍 Testing Signup Database Flow...")
    
    # Generate unique test data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_user = {
        "username": f"testuser_{timestamp}",
        "email": f"test_{timestamp}@example.com",
        "password": "testpassword123"
    }
    
    try:
        # Step 1: Signup request
        print(f"📝 Attempting to signup user: {test_user['email']}")
        response = requests.post(
            "http://localhost:8000/auth/signup",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Signup request successful!")
            
            # Step 2: Verify user exists in database
            print("🔍 Verifying user data in database...")
            from db import db
            
            # Check if user exists in userInfo collection
            db_user = db.userInfo.find_one({"email": test_user["email"]})
            
            if db_user:
                print("✅ User found in database!")
                print(f"   - Username: {db_user.get('username')}")
                print(f"   - Email: {db_user.get('email')}")
                print(f"   - Hashed Password: {db_user.get('password')[:20]}...")
                print(f"   - User ID: {db_user.get('_id')}")
                return True
            else:
                print("❌ User not found in database after signup!")
                return False
                
        else:
            print(f"❌ Signup failed with status: {response.status_code}")
            print(f"Response: {response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ Error during signup test: {e}")
        return False

def test_login_verification():
    """Test login with the created user and verify authentication"""
    print("\n🔍 Testing Login Verification...")
    
    # Generate unique test data (same as signup test)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_user = {
        "username": f"testuser_{timestamp}",
        "email": f"test_{timestamp}@example.com",
        "password": "testpassword123"
    }
    
    try:
        # Step 1: First signup the user
        print(f"📝 Creating test user: {test_user['email']}")
        signup_response = requests.post(
            "http://localhost:8000/auth/signup",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        
        if signup_response.status_code != 200:
            print("❌ Failed to create test user for login test")
            return False
        
        # Step 2: Attempt login
        print("🔐 Attempting login...")
        login_response = requests.post(
            "http://localhost:8000/auth/login",
            json={
                "email": test_user["email"],
                "password": test_user["password"]
            },
            headers={"Content-Type": "application/json"}
        )
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            print("✅ Login successful!")
            print(f"   - User ID: {login_data['user_data']['user_id']}")
            print(f"   - Username: {login_data['user_data']['username']}")
            print(f"   - Email: {login_data['user_data']['email']}")
            return True
        else:
            print(f"❌ Login failed with status: {login_response.status_code}")
            print(f"Response: {login_response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ Error during login test: {e}")
        return False

def test_chat_history_save():
    """Test saving chat messages to database"""
    print("\n🔍 Testing Chat History Save...")
    
    # Generate unique test data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_user = {
        "username": f"testuser_{timestamp}",
        "email": f"test_{timestamp}@example.com",
        "password": "testpassword123"
    }
    
    try:
        # Step 1: Create user
        signup_response = requests.post(
            "http://localhost:8000/auth/signup",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        
        if signup_response.status_code != 200:
            print("❌ Failed to create test user for chat test")
            return False
        
        # Step 2: Login to get user_id
        login_response = requests.post(
            "http://localhost:8000/auth/login",
            json={
                "email": test_user["email"],
                "password": test_user["password"]
            },
            headers={"Content-Type": "application/json"}
        )
        
        if login_response.status_code != 200:
            print("❌ Failed to login for chat test")
            return False
        
        user_id = login_response.json()['user_data']['user_id']
        
        # Step 3: Save a chat message
        print("💬 Saving test chat message...")
        chat_data = {
            'document_id': 'test_doc_123',
            'question': 'What is this test about?',
            'answer': 'This is a test message to verify database storage.',
            'user_id': user_id
        }
        
        chat_response = requests.post(
            "http://localhost:8000/chat/",
            data=chat_data
        )
        
        if chat_response.status_code == 200:
            print("✅ Chat message saved successfully!")
            
            # Step 4: Verify chat history in database
            print("🔍 Verifying chat history in database...")
            from db import db
            
            chat_history = list(db.chat_history.find({"user_id": user_id}))
            
            if chat_history:
                print(f"✅ Found {len(chat_history)} chat entries in database!")
                for chat in chat_history:
                    print(f"   - Question: {chat.get('question')}")
                    print(f"   - Answer: {chat.get('answer')}")
                    print(f"   - Document ID: {chat.get('document_id')}")
                    print(f"   - Timestamp: {chat.get('timestamp')}")
                return True
            else:
                print("❌ No chat history found in database!")
                return False
        else:
            print(f"❌ Failed to save chat message: {chat_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error during chat test: {e}")
        return False

def cleanup_test_data():
    """Clean up test data from database"""
    print("\n🧹 Cleaning up test data...")
    try:
        from db import db
        
        # Remove test users (emails containing 'test_')
        result = db.userInfo.delete_many({"email": {"$regex": "test_.*@example.com"}})
        print(f"✅ Removed {result.deleted_count} test users")
        
        # Remove test chat history (questions containing 'test')
        result = db.chat_history.delete_many({"question": {"$regex": "test"}})
        print(f"✅ Removed {result.deleted_count} test chat entries")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")

def main():
    print("🚀 Starting Database Flow Tests...")
    print("=" * 50)
    
    # Test backend connection
    if not test_backend_connection():
        print("\n❌ Backend not available. Please start the backend first.")
        return
    
    # Run all tests
    tests = [
        ("Signup Database Flow", test_signup_to_database),
        ("Login Verification", test_login_verification),
        ("Chat History Save", test_chat_history_save)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print(f"\n{'='*50}")
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Database flow is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the backend and database configuration.")
    
    # Cleanup
    cleanup_test_data()

if __name__ == "__main__":
    main() 