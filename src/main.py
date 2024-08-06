from fastapi import FastAPI
from endpoint.user import router as user_router
from endpoint.category import router as category_router
from endpoint.book import router as book_router

app = FastAPI()

app.include_router(user_router)
app.include_router(category_router)
app.include_router(book_router)
