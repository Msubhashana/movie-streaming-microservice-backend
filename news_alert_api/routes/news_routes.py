from fastapi import APIRouter, HTTPException, status
from typing import List
from models.news import News
from services.news_service import NewsService

router = APIRouter(
    tags=["News"]
)

@router.get("/news", response_model=List[News], summary="Get all news alerts")
def get_all_news():
    """
    Get all news alerts.
    """
    return NewsService.get_all_news()

@router.get("/news/{news_id}", response_model=News, summary="Get a news alert by ID")
def get_single_news(news_id: int):
    """
    Get a single news alert by its ID.
    """
    news = NewsService.get_news_by_id(news_id)
    if not news:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"News alert with id {news_id} not found")
    return news

@router.post("/news", response_model=News, status_code=status.HTTP_201_CREATED, summary="Create a new news alert")
def create_news(news: News):
    """
    Create a new news alert.
    """
    if news.type not in ["release", "trending", "announcement"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid news type. Must be 'release', 'trending', or 'announcement'."
        )
    return NewsService.create_news(news)

@router.put("/news/{news_id}", response_model=News, summary="Update an existing news alert")
def update_news(news_id: int, news: News):
    """
    Update an existing news alert.
    """
    if news.type not in ["release", "trending", "announcement"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid news type. Must be 'release', 'trending', or 'announcement'."
        )
    updated = NewsService.update_news(news_id, news)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"News alert with id {news_id} not found")
    return updated

@router.delete("/news/{news_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a news alert by ID")
def delete_news(news_id: int):
    """
    Delete a news alert by its ID.
    """
    success = NewsService.delete_news(news_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"News alert with id {news_id} not found")
