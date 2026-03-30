from typing import List, Optional
from models.news import News

# In-memory storage and sample data
news_db: List[News] = [
    News(id=1, title="New Outer Banks Season", description="The latest season is now streaming!", type="release", date="2023-10-01"),
    News(id=2, title="Top 10 Trending Action Movies", description="Check out the top action movies this week.", type="trending", date="2023-10-02"),
    News(id=3, title="Service Maintenance", description="Scheduled maintenance at 3 AM.", type="announcement", date="2023-10-03"),
    News(id=4, title="Avengers: Secret Wars Announced", description="Marvel Studios just announced the next big Avengers movie.", type="announcement", date="2023-10-04"),
    News(id=5, title="The Batman 2 Release Date", description="The highly anticipated sequel is coming next year.", type="release", date="2023-10-05"),
    News(id=6, title="Stranger Things Finale", description="The finale is trending #1 worldwide today.", type="trending", date="2023-10-06"),
    News(id=7, title="Server Upgrade", description="We are moving to faster servers tomorrow.", type="announcement", date="2023-10-07")
]
current_id = 7

class NewsService:
    @staticmethod
    def get_all_news() -> List[News]:
        return news_db

    @staticmethod
    def get_news_by_id(news_id: int) -> Optional[News]:
        for news in news_db:
            if news.id == news_id:
                return news
        return None

    @staticmethod
    def create_news(news: News) -> News:
        global current_id
        if news.id is None:
            current_id += 1
            news.id = current_id
        elif news.id > current_id:
            current_id = news.id
        news_db.append(news)
        return news

    @staticmethod
    def update_news(news_id: int, updated_news: News) -> Optional[News]:
        for index, news in enumerate(news_db):
            if news.id == news_id:
                updated_news.id = news_id
                news_db[index] = updated_news
                return updated_news
        return None

    @staticmethod
    def delete_news(news_id: int) -> bool:
        global news_db
        initial_length = len(news_db)
        news_db = [news for news in news_db if news.id != news_id]
        return len(news_db) < initial_length
