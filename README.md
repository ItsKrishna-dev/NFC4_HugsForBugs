# HugsForBugs
 ## Document Summarizer with Contextual Q&A

### Problem Statement:

Legal professionals, researchers, and executives frequently deal with extensive documents like contracts, research papers, project reports, or policy briefs. Reading and understanding such documents consumes significant time, and locating key information (like deadlines, obligations, or risks) often requires manual scanning. 

Even tools that summarize documents fail to retain the context or support follow-up questions. An intelligent AI assistant that not only summarizes but also answers specific queries contextually from within the document can revolutionize document handling in legal, academic, and corporate sectors.

This project aims to create a **web-based AI tool** that enables:
- 📄 Document upload
- 🧠 Automatic summarization
- 💬 Contextual Q&A
- 🔍 Interactive exploration with semantic accuracy

---

## 🚀 Key Features

- ✅ Upload support for **DOCX**, **PDF**, and **TXT** formats
- 📚 **LLM-powered summarization** with section-wise breakdowns
- 💬 **Chat-based interface** for context-aware Q&A
- 🧩 **Chunking and embedding** for long document processing
- ✨ **Highlighted answer referencing** within the document
- 🧵 Retention of **question-answer memory** through threaded conversations
- 📑 Support for **multi-document upload** and **comparison mode**
- 📥 **Downloadable report** with summary and Q&A (optional)
- 🤖 **Retrieval-Augmented Generation (RAG)** for context-based response generation (mandatory)


## 🚀 How to Run the Application

### Prerequisites
- Python 3.8 or higher
- MongoDB Atlas account (for database)

### Backend Setup
1. Navigate to the project directory:
   ```bash
   cd NFC4_HugsForBugs
   ```

2. Install dependencies:
   ```bash
   pip install -r app/requirements.txt
   ```

3. Set up your MongoDB connection:
   - Create a `.env` file in the `app` directory
   - Add your MongoDB Atlas connection string:
     ```
     MONGO_URI=mongodb+srv://your_username:your_password@your_cluster.mongodb.net/your_database?retryWrites=true&w=majority
     ```

4. Start the FastAPI backend:
   ```bash
   python start_backend.py
   ```
   The backend will run on `http://localhost:8000`

### Frontend Setup
1. Open the `frontend` folder in your browser or serve it using a local server
2. Start with `Signup.html` to create an account
3. Login with your credentials
4. Access the chat interface to interact with your documents

### Testing Database Flow
To verify that signup and login data is being saved to the database:

1. **Run the comprehensive database test**:
   ```bash
   python test_database_flow.py
   ```
   This will test:
   - ✅ Signup data saving to database
   - ✅ Login verification
   - ✅ Chat history saving
   - ✅ Data retrieval from database

2. **View database contents manually**:
   ```bash
   python view_database.py
   ```
   This provides an interactive interface to:
   - View all users in the database
   - View all chat history
   - Search for specific users or chat entries

### Features
- ✅ User registration and authentication
- ✅ Secure password hashing with bcrypt
- ✅ Chat history persistence
- ✅ Real-time chat interface
- ✅ Document upload and processing
- ✅ User-specific data isolation

### API Endpoints
- `POST /auth/signup` - User registration
- `POST /auth/login` - User authentication
- `GET /auth/chat-history/{user_id}` - Fetch user's chat history
- `POST /chat/` - Save chat messages
- `POST /upload/` - Upload documents

### Security Features
- CORS enabled for frontend-backend communication
- Password hashing with bcrypt
- User session management with localStorage
- Input validation and sanitization

### Database Collections
- `userInfo` - Stores user registration data
- `chat_history` - Stores user chat messages
- `documents` - Stores uploaded documents

---