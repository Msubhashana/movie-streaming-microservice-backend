from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from routes.news_routes import router as news_router

app = FastAPI(
    title="News Alert Service",
    description="Microservice for a movie discovery and streaming application that manages news alerts.",
    version="1.0.0",
    docs_url="/docs"
)

# Add CORS middleware to allow frontend applications to fetch data
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=False, # Must be False if origins is '*'
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Connect with API Gateway at /news
app.include_router(news_router)

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/news")

@app.get("/health-check")
def health_check():
    return {"status": "ok", "service": "News Alert Service"}

if __name__ == "__main__":
    import uvicorn
    # uvicorn main:app --reload --port 5006
    uvicorn.run("main:app", host="0.0.0.0", port=5006, reload=True)
