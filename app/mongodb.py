from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("db_url2")
DB_NAME = "mydb2"

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]
collection = db["users"] 
products_collection = db["products"] 
purchases_collection = db["purchases"]
