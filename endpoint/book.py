from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from security import security
from crud import crud_book, crud_user
from schemas.book import BookIn, UpdateBook, SearchIn
from constants import target

router = APIRouter(prefix="/book", tags=[target.BOOK])


@router.post("/search")
def read(
    request: SearchIn,
    db: Session = Depends(security.get_db),
    token: str = Depends(crud_user.check_authorization),
    page: int = 1,
    page_size: int = 10,
):
    return crud_book.read(request, db, token, page, page_size)


@router.post("/create")
def create(
    request: BookIn,
    db: Session = Depends(security.get_db),
    token: str = Depends(crud_user.check_authorization),
):
    return crud_book.create(request, db, token)


@router.put("")
def update(
    book_id: int,
    request: UpdateBook,
    db: Session = Depends(security.get_db),
    token: str = Depends(crud_user.check_authorization),
):
    return crud_book.update(book_id, request, db, token)


@router.delete("")
def delete(
    book_id: int,
    db: Session = Depends(security.get_db),
    token: str = Depends(crud_user.check_authorization),
):
    return crud_book.delete(book_id, db, token)
