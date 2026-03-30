from pydantic import BaseModel
from typing import Optional

class News(BaseModel):
    id: Optional[int] = None
    title: str
    description: str
    type: str
    date: str
