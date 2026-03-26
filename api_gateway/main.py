from fastapi import FastAPI, HTTPException
import httpx

app = FastAPI(
    title="API Gateway",
    description="Central entry point for the Movie Streaming Microservices",
    version="1.0.0"
)

# Define the internal URL for your Content API
CONTENT_API_URL = "http://localhost:5001"

@app.get("/api/movies", summary="Route to Content API: Get all movies")
async def get_movies_via_gateway():
    """
    This endpoint intercepts the request and forwards it to the Content API running on Port 5001.
    """
    # httpx acts as the "messenger" that talks to your other microservices
    async with httpx.AsyncClient() as client:
        try:
            # 1. The Gateway asks the Content API for the data
            response = await client.get(f"{CONTENT_API_URL}/api/movies")
            
            # 2. If the Content API throws an error, the Gateway catches it
            response.raise_for_status() 
            
            # 3. The Gateway returns the raw data back to the final user
            return response.json()
        
        except httpx.RequestError:
            # If the Content API is turned off or crashed, return a clean error message
            raise HTTPException(status_code=503, detail="Content API is currently unavailable.")