from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)

try:
    
    client.admin.command('ping')
    print("✅ Database connected")
except ConnectionFailure as e:
    print("❌ Database connection failed:", e)

db = client["myDatabase"]  
