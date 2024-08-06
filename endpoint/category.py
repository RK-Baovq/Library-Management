from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from crud import crud_category, crud_user
from schemas.category import CategoryIn
from security import security
from constants import target


router = APIRouter(prefix="/category", tags=[target.CATEGORY])


@router.get("")
def read(
    db: Session = Depends(security.get_db),
    token: str = Depends(crud_user.check_authorization),
    page: int = 1,
    page_size: int = 10,
):
    return crud_category.read(db, token, page, page_size)


@router.post("")
def create(
    request: CategoryIn,
    db: Session = Depends(security.get_db),
    token: str = Depends(crud_user.check_authorization),
):
    return crud_category.create(request, db, token)


@router.put("")
def update(
    category_id: int,
    request: CategoryIn,
    db: Session = Depends(security.get_db),
    token: str = Depends(crud_user.check_authorization),
):
    return crud_category.update(category_id, request, db, token)


@router.delete("")
def delete(
    category_id: int,
    db: Session = Depends(security.get_db),
    token: str = Depends(crud_user.check_authorization),
):
    return crud_category.delete(category_id, db, token)
