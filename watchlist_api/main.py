from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load the hidden variables from the .env file
load_dotenv()

app = FastAPI(
    title="Watchlist Microservice API",
    description="Manages user movie watchlists",
    version="1.0.0"
)

# --- DATABASE SETUP ---
MONGO_DETAILS = os.getenv("MONGO_URL")
if not MONGO_DETAILS:
    raise ValueError("No MONGO_URL found in environment variables!")

client = AsyncIOMotorClient(MONGO_DETAILS)
# Notice we are creating a specific database name for this service
database = client.watchlist_db
watchlist_collection = database.get_collection("user_watchlists")

# --- DATA MODELS ---
# The frontend only needs to send us the movie ID they clicked "Save" on
class MovieAddRequest(BaseModel):
    movie_id: int

# --- ROUTES ---

@app.get("/", summary="Root Welcome Message")
def root():
    return {"message": "Watchlist API is running! Go to /docs for Swagger UI."}

# 1. READ: Get a user's entire watchlist
@app.get("/api/watchlist/{user_id}", summary="Get a user's watchlist")
async def get_watchlist(user_id: int):
    user_list = await watchlist_collection.find_one({"user_id": user_id}, {"_id": 0})
    
    # If the user has no watchlist yet, return an empty list instead of an error
    if not user_list:
        return {"user_id": user_id, "saved_movie_ids": []}
    
    return user_list

# 2. CREATE/UPDATE: Add a movie to a user's watchlist
@app.post("/api/watchlist/{user_id}", summary="Add a movie to watchlist")
async def add_to_watchlist(user_id: int, request: MovieAddRequest):
    # upsert=True means: "If this user doesn't exist yet, create them. If they do, update them."
    # $addToSet adds the movie_id to the array, but prevents duplicates!
    result = await watchlist_collection.update_one(
        {"user_id": user_id},
        {"$addToSet": {"saved_movie_ids": request.movie_id}},
        upsert=True 
    )
    return {"message": f"Movie {request.movie_id} added to user {user_id}'s watchlist"}

# 3. DELETE: Remove a movie from a user's watchlist
@app.delete("/api/watchlist/{user_id}/{movie_id}", summary="Remove a movie from watchlist")
async def remove_from_watchlist(user_id: int, movie_id: int):
    # $pull removes a specific item from an array
    result = await watchlist_collection.update_one(
        {"user_id": user_id},
        {"$pull": {"saved_movie_ids": movie_id}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Movie not found in user's watchlist")
        
    return {"message": f"Movie {movie_id} removed from user {user_id}'s watchlist"}