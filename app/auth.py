from fastapi import APIRouter, HTTPException
from passlib.context import CryptContext
from models import UserSignup, UserLogin
from db import db

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

@router.post("/signup")
def signup(user: UserSignup):
    if db.userInfo.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_dict = {
        "username": user.username,
        "email": user.email,
        "password": hash_password(user.password)
    }
    db.userInfo.insert_one(user_dict)
    return {"message": "User created successfully"}

@router.post("/login")
def login(user: UserLogin):
    db_user = db.userInfo.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Convert ObjectId to string for JSON serialization
    user_data = {
        "user_id": str(db_user["_id"]),
        "username": db_user["username"],
        "email": db_user["email"]
    }
    
    return {"message": "Login successful", "user_data": user_data}

@router.get("/chat-history/{user_id}")
def get_chat_history(user_id: str):
    """Fetch chat history for a specific user"""
    try:
        # Find all chat entries for the specific user
        chat_history = list(db.chat_history.find({"user_id": user_id}))
        
        # Convert ObjectIds to strings for JSON serialization
        for chat in chat_history:
            chat["_id"] = str(chat["_id"])
            if "document_id" in chat:
                chat["document_id"] = str(chat["document_id"])
        
        return {"chat_history": chat_history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching chat history: {str(e)}")
