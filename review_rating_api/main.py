from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Review and Rating API",
    description="Manages user reviews and ratings for movies",
    version="1.0.0"
)

# --- DATABASE SETUP ---
MONGO_DETAILS = os.getenv("MONGO_URL")
if not MONGO_DETAILS:
    raise ValueError("No MONGO_URL found in environment variables!")

client = AsyncIOMotorClient(MONGO_DETAILS)
# Creating a dedicated database for reviews
database = client.review_db
review_collection = database.get_collection("movie_reviews")


# --- DATA MODELS ---
class Review(BaseModel):
    review_id: int
    movie_id: int
    user_id: int
    # Enforces a rating between 1 and 5 stars
    rating: int = Field(..., ge=1, le=5, description="Star rating from 1 to 5")
    comment: str


# --- ROUTES ---

@app.get("/", summary="Root Welcome Message")
def root():
    return {"message": "Review API is running! Go to /docs for Swagger UI."}

# 1. READ: Get all reviews for a SPECIFIC movie
@app.get("/api/reviews/movie/{movie_id}", response_model=List[Review], summary="Get reviews for a movie")
async def get_movie_reviews(movie_id: int):
    reviews = []
    # Search the database for any review attached to this specific movie_id
    async for review in review_collection.find({"movie_id": movie_id}, {"_id": 0}):
        reviews.append(review)
    return reviews

# 2. CREATE: Add a new review
@app.post("/api/reviews", response_model=Review, summary="Submit a new review")
async def add_review(review: Review):
    existing = await review_collection.find_one({"review_id": review.review_id})
    if existing:
        raise HTTPException(status_code=400, detail="Review ID already exists")
    
    await review_collection.insert_one(review.model_dump())
    return review

# 3. DELETE: Remove a review (usually only allowed by the user who wrote it or an admin)
@app.delete("/api/reviews/{review_id}", summary="Delete a review")
async def delete_review(review_id: int):
    result = await review_collection.delete_one({"review_id": review_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Review not found")
        
    return {"message": f"Review {review_id} deleted successfully"}