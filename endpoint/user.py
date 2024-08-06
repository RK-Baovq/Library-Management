from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from security import security
from crud import crud_user
from schemas.user import (
    AdminIn,
    SuperAdminIn,
    UserLogin,
    PasswordChangeRequest,
)
from constants import target


router = APIRouter(prefix="/user", tags=[target.USER])


@router.get("")
def read(
    db: Session = Depends(security.get_db),
    token: str = Depends(crud_user.check_authorization),
    page: int = 1,
    page_size: int = 10,
):
    return crud_user.read(db, token, page, page_size)


@router.post("/login")
def login(request: UserLogin, db: Session = Depends(security.get_db)):
    db_user = crud_user.login(db, request)
    return {"access_token": db_user}


@router.post("/admin")
def admin_create(
    request: AdminIn,
    db: Session = Depends(security.get_db),
    token: str = Depends(crud_user.check_authorization),
):
    return crud_user.admin_create(db, request, token)


@router.post("/superadmin")
def super_admin_create(
    request: SuperAdminIn,
    db: Session = Depends(security.get_db),
    token: str = Depends(crud_user.check_authorization),
):
    return crud_user.super_admin_create(db, request, token)


@router.put("/password")
def change_password(
    passwordChange: PasswordChangeRequest,
    db: Session = Depends(security.get_db),
    token: str = Depends(crud_user.check_authorization),
):
    return crud_user.change_password(passwordChange, db, token)


@router.delete("")
def delete(
    user_id: int,
    db: Session = Depends(security.get_db),
    token: str = Depends(crud_user.check_authorization),
):
    return crud_user.delete(user_id, db, token)
