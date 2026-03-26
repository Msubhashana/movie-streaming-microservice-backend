from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load the hidden variables from the .env file
load_dotenv()

app = FastAPI(
    title="Content Microservice API",
    description="Manages movie metadata with full CRUD and MongoDB Atlas",
    version="1.1.0"
)

# --- DATABASE SETUP ---
# Securely fetch the URL from the .env file
MONGO_DETAILS = os.getenv("MONGO_URL")

# If the .env file is missing or misspelled, this will catch the error early
if not MONGO_DETAILS:
    raise ValueError("No MONGO_URL found in environment variables!")

client = AsyncIOMotorClient(MONGO_DETAILS)
database = client.movie_streaming
movie_collection = database.get_collection("movies")

# --- DATA MODEL ---
class Movie(BaseModel):
    id: int
    title: str
    genre: str
    year: int


# --- ROUTES (CRUD OPERATIONS) ---

# 1. READ: Get all movies
@app.get("/api/movies", response_model=List[Movie], summary="Get all movies")
async def get_movies():
    movies = []
    # Fetch all documents from MongoDB, excluding the internal Mongo _id
    async for movie in movie_collection.find({}, {"_id": 0}):
        movies.append(movie)
    return movies

# 2. CREATE: Add a new movie
@app.post("/api/movies", response_model=Movie, summary="Add a new movie")
async def create_movie(movie: Movie):
    # Check if a movie with this ID already exists
    existing = await movie_collection.find_one({"id": movie.id})
    if existing:
        raise HTTPException(status_code=400, detail="Movie ID already exists")
    
    # Insert the data into MongoDB
    await movie_collection.insert_one(movie.model_dump())
    return movie

# 3. UPDATE: Modify an existing movie
@app.put("/api/movies/{movie_id}", response_model=Movie, summary="Update a movie")
async def update_movie(movie_id: int, updated_data: Movie):
    result = await movie_collection.update_one(
        {"id": movie_id}, 
        {"$set": updated_data.model_dump()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    return updated_data

# 4. DELETE: Remove a movie
@app.delete("/api/movies/{movie_id}", summary="Delete a movie")
async def delete_movie(movie_id: int):
    result = await movie_collection.delete_one({"id": movie_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    return {"message": f"Movie {movie_id} deleted successfully"}