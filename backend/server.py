from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone, date

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
class MoodEntry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    mood: int  # 1-5 scale
    mood_emoji: str
    notes: Optional[str] = ""
    date: str  # Store as ISO date string
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MoodEntryCreate(BaseModel):
    mood: int
    mood_emoji: str
    notes: Optional[str] = ""
    date: str

class MoodEntryResponse(BaseModel):
    id: str
    mood: int
    mood_emoji: str
    notes: str
    date: str
    timestamp: datetime

# Helper function to prepare data for MongoDB
def prepare_for_mongo(data):
    if isinstance(data.get('timestamp'), datetime):
        data['timestamp'] = data['timestamp'].isoformat()
    return data

def parse_from_mongo(item):
    if isinstance(item.get('timestamp'), str):
        item['timestamp'] = datetime.fromisoformat(item['timestamp'])
    return item

# Routes
@api_router.get("/")
async def root():
    return {"message": "Mood Tracker API"}

@api_router.post("/moods", response_model=MoodEntryResponse)
async def create_mood_entry(mood_data: MoodEntryCreate):
    try:
        mood_dict = mood_data.dict()
        mood_obj = MoodEntry(**mood_dict)
        
        # Prepare data for MongoDB
        mood_dict = prepare_for_mongo(mood_obj.dict())
        
        # Insert into database
        result = await db.mood_entries.insert_one(mood_dict)
        
        if result.inserted_id:
            return MoodEntryResponse(**mood_obj.dict())
        else:
            raise HTTPException(status_code=500, detail="Failed to create mood entry")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/moods", response_model=List[MoodEntryResponse])
async def get_mood_entries():
    try:
        # Get all mood entries, sorted by date descending
        moods = await db.mood_entries.find().sort("timestamp", -1).to_list(length=None)
        
        # Parse from MongoDB and return
        parsed_moods = [parse_from_mongo(mood) for mood in moods]
        return [MoodEntryResponse(**mood) for mood in parsed_moods]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/moods/{date}")
async def get_mood_by_date(date: str):
    try:
        mood = await db.mood_entries.find_one({"date": date})
        if mood:
            parsed_mood = parse_from_mongo(mood)
            return MoodEntryResponse(**parsed_mood)
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/moods/{mood_id}", response_model=MoodEntryResponse)
async def update_mood_entry(mood_id: str, mood_data: MoodEntryCreate):
    try:
        mood_dict = mood_data.dict()
        mood_dict['timestamp'] = datetime.now(timezone.utc).isoformat()
        
        result = await db.mood_entries.update_one(
            {"id": mood_id},
            {"$set": mood_dict}
        )
        
        if result.modified_count == 1:
            updated_mood = await db.mood_entries.find_one({"id": mood_id})
            if updated_mood:
                parsed_mood = parse_from_mongo(updated_mood)
                return MoodEntryResponse(**parsed_mood)
        
        raise HTTPException(status_code=404, detail="Mood entry not found")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/moods/{mood_id}")
async def delete_mood_entry(mood_id: str):
    try:
        result = await db.mood_entries.delete_one({"id": mood_id})
        if result.deleted_count == 1:
            return {"message": "Mood entry deleted successfully"}
        raise HTTPException(status_code=404, detail="Mood entry not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/moods/export/csv")
async def export_moods_csv():
    try:
        moods = await db.mood_entries.find().sort("date", 1).to_list(length=None)
        
        # Create CSV content
        csv_content = "Date,Mood,Emoji,Notes,Timestamp\n"
        for mood in moods:
            notes = mood.get('notes', '').replace('"', '""')  # Escape quotes
            csv_content += f'"{mood["date"]}",{mood["mood"]},"{mood["mood_emoji"]}","{notes}","{mood["timestamp"]}"\n'
        
        return {
            "content": csv_content,
            "filename": f"mood_data_{datetime.now(timezone.utc).strftime('%Y%m%d')}.csv"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()