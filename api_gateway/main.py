from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx

app = FastAPI(
    title="API Gateway",
    description="Central entry point for the Movie Streaming Microservices",
    version="1.0.0"
)

# --- INTERNAL MICROSERVICE URLs ---
CONTENT_API_URL = "http://localhost:5001"
WATCHLIST_API_URL = "http://localhost:5002"

# --- DATA MODELS ---
# Model for the Content API (Creating/Updating Movies)
class Movie(BaseModel):
    id: int
    title: str
    genre: str
    year: int

# Model for the Watchlist API (Adding a movie to a list)
class MovieAddRequest(BaseModel):
    movie_id: int


# ==========================================
#          CONTENT API ROUTES
# ==========================================

@app.get("/api/movies", summary="Route to Content API: Get all movies")
async def get_movies_via_gateway():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{CONTENT_API_URL}/api/movies")
            response.raise_for_status() 
            return response.json()
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Content API is currently unavailable.")

@app.post("/api/movies", summary="Route to Content API: Add a new movie")
async def create_movie_via_gateway(movie: Movie):
    async with httpx.AsyncClient() as client:
        try:
            # Forward the JSON body to the Content API
            response = await client.post(f"{CONTENT_API_URL}/api/movies", json=movie.model_dump())
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            # If the Content API throws a specific error (like "ID already exists"), pass it to the user
            raise HTTPException(status_code=e.response.status_code, detail=e.response.json().get("detail", "Error"))
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Content API is currently unavailable.")

@app.put("/api/movies/{movie_id}", summary="Route to Content API: Update a movie")
async def update_movie_via_gateway(movie_id: int, movie: Movie):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(f"{CONTENT_API_URL}/api/movies/{movie_id}", json=movie.model_dump())
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.json().get("detail", "Error"))
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Content API is currently unavailable.")

@app.delete("/api/movies/{movie_id}", summary="Route to Content API: Delete a movie")
async def delete_movie_via_gateway(movie_id: int):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(f"{CONTENT_API_URL}/api/movies/{movie_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.json().get("detail", "Error"))
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Content API is currently unavailable.")


# ==========================================
#          WATCHLIST API ROUTES
# ==========================================

@app.get("/api/watchlist/{user_id}", summary="Route to Watchlist API: Get a user's watchlist")
async def get_watchlist_via_gateway(user_id: int):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{WATCHLIST_API_URL}/api/watchlist/{user_id}")
            response.raise_for_status()
            return response.json()
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Watchlist API is currently unavailable.")

@app.post("/api/watchlist/{user_id}", summary="Route to Watchlist API: Add movie")
async def add_to_watchlist_via_gateway(user_id: int, request: MovieAddRequest):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{WATCHLIST_API_URL}/api/watchlist/{user_id}", 
                json=request.model_dump()
            )
            response.raise_for_status()
            return response.json()
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Watchlist API is currently unavailable.")

@app.delete("/api/watchlist/{user_id}/{movie_id}", summary="Route to Watchlist API: Remove movie")
async def remove_from_watchlist_via_gateway(user_id: int, movie_id: int):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(f"{WATCHLIST_API_URL}/api/watchlist/{user_id}/{movie_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.json().get("detail", "Error"))
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Watchlist API is currently unavailable.")