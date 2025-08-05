import sys
import os
from datetime import datetime

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def view_database_contents():
    """View all collections and their contents in the database"""
    try:
        from db import db
        
        print("🗄️  DATABASE CONTENTS VIEWER")
        print("=" * 50)
        
        # List all collections
        collections = db.list_collection_names()
        print(f"📁 Found {len(collections)} collections: {collections}")
        print()
        
        # View userInfo collection
        print("👥 USER INFO COLLECTION")
        print("-" * 30)
        users = list(db.userInfo.find())
        if users:
            print(f"Found {len(users)} users:")
            for i, user in enumerate(users, 1):
                print(f"\n{i}. User Details:")
                print(f"   - ID: {user.get('_id')}")
                print(f"   - Username: {user.get('username')}")
                print(f"   - Email: {user.get('email')}")
                print(f"   - Password Hash: {user.get('password')[:30]}...")
        else:
            print("No users found in database.")
        print()
        
        # View chat_history collection
        print("💬 CHAT HISTORY COLLECTION")
        print("-" * 30)
        chats = list(db.chat_history.find())
        if chats:
            print(f"Found {len(chats)} chat entries:")
            for i, chat in enumerate(chats, 1):
                print(f"\n{i}. Chat Entry:")
                print(f"   - ID: {chat.get('_id')}")
                print(f"   - User ID: {chat.get('user_id')}")
                print(f"   - Document ID: {chat.get('document_id')}")
                print(f"   - Question: {chat.get('question')}")
                print(f"   - Answer: {chat.get('answer')}")
                print(f"   - Timestamp: {chat.get('timestamp')}")
        else:
            print("No chat history found in database.")
        print()
        
        # View documents collection
        print("📄 DOCUMENTS COLLECTION")
        print("-" * 30)
        documents = list(db.documents.find())
        if documents:
            print(f"Found {len(documents)} documents:")
            for i, doc in enumerate(documents, 1):
                print(f"\n{i}. Document:")
                print(f"   - ID: {doc.get('_id')}")
                print(f"   - User ID: {doc.get('user_id')}")
                print(f"   - Filename: {doc.get('filename')}")
                print(f"   - Content Length: {len(doc.get('content', ''))} characters")
                print(f"   - Upload Time: {doc.get('upload_time')}")
        else:
            print("No documents found in database.")
        print()
        
    except Exception as e:
        print(f"❌ Error accessing database: {e}")
        print("Make sure:")
        print("1. MongoDB is running and accessible")
        print("2. .env file is configured with correct MONGO_URI")
        print("3. Backend is running")

def search_user_by_email(email):
    """Search for a specific user by email"""
    try:
        from db import db
        
        user = db.userInfo.find_one({"email": email})
        if user:
            print(f"\n✅ User found: {email}")
            print(f"   - Username: {user.get('username')}")
            print(f"   - User ID: {user.get('_id')}")
            print(f"   - Password Hash: {user.get('password')[:30]}...")
        else:
            print(f"\n❌ User not found: {email}")
            
    except Exception as e:
        print(f"❌ Error searching user: {e}")

def search_chat_by_user_id(user_id):
    """Search for chat history by user ID"""
    try:
        from db import db
        
        chats = list(db.chat_history.find({"user_id": user_id}))
        if chats:
            print(f"\n✅ Found {len(chats)} chat entries for user: {user_id}")
            for i, chat in enumerate(chats, 1):
                print(f"\n{i}. Chat Entry:")
                print(f"   - Question: {chat.get('question')}")
                print(f"   - Answer: {chat.get('answer')}")
                print(f"   - Timestamp: {chat.get('timestamp')}")
        else:
            print(f"\n❌ No chat history found for user: {user_id}")
            
    except Exception as e:
        print(f"❌ Error searching chat history: {e}")

def main():
    print("🔍 DATABASE VIEWER")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. View all database contents")
        print("2. Search user by email")
        print("3. Search chat history by user ID")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            view_database_contents()
        elif choice == "2":
            email = input("Enter email to search: ").strip()
            search_user_by_email(email)
        elif choice == "3":
            user_id = input("Enter user ID to search: ").strip()
            search_chat_by_user_id(user_id)
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main() 