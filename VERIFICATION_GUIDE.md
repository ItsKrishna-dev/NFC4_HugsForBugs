# 🔍 Database Flow Verification Guide

This guide will help you verify that signup and login data is properly being saved to the database.

## Prerequisites
1. ✅ MongoDB Atlas account set up
2. ✅ `.env` file configured with MONGO_URI
3. ✅ Backend running on `http://localhost:8000`
4. ✅ Dependencies installed

## Step 1: Quick Connection Test
```bash
python test_connection.py
```
**Expected Output:**
```
✅ Backend is running successfully!
✅ Signup endpoint working!
```

## Step 2: Comprehensive Database Test
```bash
python test_database_flow.py
```
**Expected Output:**
```
🚀 Starting Database Flow Tests...
==================================================

==================== Signup Database Flow ====================
🔍 Testing Signup Database Flow...
📝 Attempting to signup user: test_20241201_143022@example.com
✅ Signup request successful!
🔍 Verifying user data in database...
✅ User found in database!
   - Username: testuser_20241201_143022
   - Email: test_20241201_143022@example.com
   - Hashed Password: $2b$12$abcdefghijklmnop...
   - User ID: 507f1f77bcf86cd799439011

==================== Login Verification ====================
✅ Login successful!
   - User ID: 507f1f77bcf86cd799439011
   - Username: testuser_20241201_143022
   - Email: test_20241201_143022@example.com

==================== Chat History Save ====================
✅ Chat message saved successfully!
✅ Found 1 chat entries in database!

==================================================
📊 TEST SUMMARY
==================================================
Signup Database Flow: ✅ PASSED
Login Verification: ✅ PASSED
Chat History Save: ✅ PASSED

Overall: 3/3 tests passed
🎉 All tests passed! Database flow is working correctly.
```

## Step 3: Manual Database Inspection
```bash
python view_database.py
```
**Choose option 1** to view all database contents.

**Expected Output:**
```
🗄️  DATABASE CONTENTS VIEWER
==================================================
📁 Found 3 collections: ['userInfo', 'chat_history', 'documents']

👥 USER INFO COLLECTION
------------------------------
Found 1 users:

1. User Details:
   - ID: 507f1f77bcf86cd799439011
   - Username: testuser_20241201_143022
   - Email: test_20241201_143022@example.com
   - Password Hash: $2b$12$abcdefghijklmnop...

💬 CHAT HISTORY COLLECTION
------------------------------
Found 1 chat entries:

1. Chat Entry:
   - ID: 507f1f77bcf86cd799439012
   - User ID: 507f1f77bcf86cd799439011
   - Document ID: test_doc_123
   - Question: What is this test about?
   - Answer: This is a test message to verify database storage.
   - Timestamp: 2024-12-01T14:30:22.123Z
```

## Step 4: Frontend Testing

1. **Open the frontend** in your browser
2. **Navigate to** `frontend/Signup.html`
3. **Create a new account** with:
   - Username: `testuser`
   - Email: `test@example.com`
   - Password: `testpassword123`
4. **Check the browser console** for any errors
5. **Verify the signup** redirects to login page
6. **Login with the same credentials**
7. **Verify login** redirects to chat page
8. **Send a test message** in the chat
9. **Check database** using the viewer to confirm data is saved

## Step 5: Troubleshooting

### If Backend Won't Start:
```bash
# Check if MongoDB connection is working
python -c "from app.db import db; print('Database connected!')"
```

### If Database Connection Fails:
1. Check your `.env` file exists in `app/` directory
2. Verify MONGO_URI is correct
3. Ensure MongoDB Atlas is accessible
4. Check network connectivity

### If Tests Fail:
1. Make sure backend is running on port 8000
2. Check MongoDB connection
3. Verify all dependencies are installed
4. Check console for error messages

### If Frontend Can't Connect:
1. Ensure backend is running
2. Check CORS configuration
3. Verify frontend is making requests to `http://localhost:8000`
4. Check browser console for CORS errors

## Expected Database Schema

### userInfo Collection
```json
{
  "_id": "ObjectId",
  "username": "string",
  "email": "string",
  "password": "hashed_string"
}
```

### chat_history Collection
```json
{
  "_id": "ObjectId",
  "user_id": "string",
  "document_id": "string",
  "question": "string",
  "answer": "string",
  "timestamp": "datetime"
}
```

### documents Collection
```json
{
  "_id": "ObjectId",
  "user_id": "string",
  "filename": "string",
  "content": "string",
  "upload_time": "datetime"
}
```

## Success Indicators

✅ **Database Flow Working When:**
- Signup creates user in `userInfo` collection
- Login retrieves user data correctly
- Chat messages save to `chat_history` collection
- User-specific data isolation works
- Password hashing is implemented
- CORS allows frontend-backend communication

❌ **Issues to Watch For:**
- Database connection errors
- Missing .env file
- Incorrect MongoDB URI
- CORS errors in browser console
- Password stored as plain text
- User data not being saved
- Chat history not persisting

---

**Need Help?** Check the console output and error messages for specific issues! 