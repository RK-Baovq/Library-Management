from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from security import security
from crud import crud_borrow, crud_user
from schemas.borrow import BorrowIn
from constants import target


router = APIRouter(prefix="/borrow", tags=[target.BORROW])


@router.get("")
def read(
    db: Session = Depends(security.get_db),
    token: str = Depends(crud_user.check_authorization),
    page: int = 1,
    page_size: int = 10,
):
    return crud_borrow.read(db, token, page, page_size)


@router.post("")
def create(
    book_id: int,
    request: BorrowIn,
    db: Session = Depends(security.get_db),
    token: str = Depends(crud_user.check_authorization),
):
    return crud_borrow.create(book_id, request, db, token)


# @router.put("/change_status")
# def change_status(borrow_id: int, borrow_status: str, db: Session = Depends(security.get_db), token: str = Depends(crud_user.check_authorization),):
#     return crud_borrow.change_status(borrow_id, borrow_status, db, token)
