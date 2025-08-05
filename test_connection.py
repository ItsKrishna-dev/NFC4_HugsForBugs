import requests
import json

def test_backend_connection():
    """Test if the backend is running and accessible"""
    try:
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            print("✅ Backend is running successfully!")
            print(f"Response: {response.json()}")
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

def test_signup_endpoint():
    """Test the signup endpoint"""
    try:
        test_user = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        response = requests.post(
            "http://localhost:8000/auth/signup",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Signup endpoint working!")
            return True
        else:
            print(f"❌ Signup failed with status: {response.status_code}")
            print(f"Response: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Error testing signup: {e}")
        return False

if __name__ == "__main__":
    print("Testing backend connection...")
    if test_backend_connection():
        print("\nTesting signup endpoint...")
        test_signup_endpoint()
    else:
        print("\nSkipping signup test due to connection failure.") 