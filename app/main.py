from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from db import db
import datetime
from auth import router as auth_router

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include auth router
app.include_router(auth_router, prefix="/auth", tags=["authentication"])

@app.get("/")
def root():
    return {"message": "FastAPI + MongoDB Atlas is working!"}

@app.post("/upload/")
async def upload_document(file: UploadFile, user_id: str = Form(...)):
   
    contents = await file.read()

    doc = {
        "user_id": user_id,
        "filename": file.filename,
        "content": contents.decode(errors="ignore"),
        "upload_time": datetime.datetime.utcnow()
    }
    result = db.documents.insert_one(doc)
    return {"message": "Document uploaded", "document_id": str(result.inserted_id)}

@app.post("/chat/")
async def add_chat(document_id: str = Form(...), question: str = Form(...), answer: str = Form(...), user_id: str = Form(...)):
    chat_entry = {
        "user_id": user_id,
        "document_id": document_id,
        "question": question,
        "answer": answer,
        "timestamp": datetime.datetime.utcnow()
    }
    db.chat_history.insert_one(chat_entry)
    return {"message": "Chat entry saved"}
