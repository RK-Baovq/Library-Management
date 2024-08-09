from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from security import security
from crud import crud_borrow, crud_user
from schemas.borrow import BorrowIn, UserUpdate
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


@router.put("/user_update")
def user_update(
    borrow_id: int,
    borrow_update: UserUpdate,
    db: Session = Depends(security.get_db),
    token: str = Depends(crud_user.check_authorization),
):
    return crud_borrow.user_update(borrow_id, borrow_update, db, token)


@router.put("/admin_update")
def admin_update(
    borrow_id: int,
    borrow_status: str = target.WAITING,
    db: Session = Depends(security.get_db),
    token: str = Depends(crud_user.check_authorization),
):
    return crud_borrow.admin_update(borrow_id, borrow_status, db, token)
