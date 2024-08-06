from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class BookIn(BaseModel):
    name: str
    author: str
    category_id: int
    publishing_company: str
    publication_date: datetime
    available_quantity: int
    describe: str = None


class UpdateBook(BaseModel):
    name: Optional[str] = None
    author: Optional[str] = None
    category_id: Optional[int] = None
    publishing_company: Optional[str] = None
    publication_date: Optional[datetime] = None
    available_quantity: Optional[int] = None
    describe: Optional[str] = None


class SearchIn(BaseModel):
    name: Optional[str] = None
    author: Optional[str] = None
    category_id: Optional[int] = None
