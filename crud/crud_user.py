from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_
from models.user import User
from security.security import (
    hash_password,
    verify_password,
    get_token,
    load_token,
    Authorization,
    get_db,
)
from constants import target
from fastapi import Depends
from typing import Optional, Dict


def check_authorization(
    authorization: Optional[str] = Depends(Authorization), db: Session = Depends(get_db)
) -> Optional[Dict]:
    if authorization is None:
        return None
    try:
        payload = load_token(authorization)
        check_account = get_user_by_id(db, payload["id"])
        if check_account:
            if (
                payload["username"] == check_account.username
                and payload["email"] == check_account.email
                and payload["role"] == check_account.role
            ):
                return payload
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Token bearer không chính xác",
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Tài khoản không tồn tại"
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token không hợp lệ"
        )


def read(db: Session, token, page, page_size):
    if token["role"] == target.ADMIN or token["role"] == target.SUPERADMIN:
        db_accounts = db.query(User).all()
        list_account = []
        for db_account in db_accounts:
            if token["role"] == target.ADMIN:
                start = (page - 1) * page_size
                if db_account.role == target.USER:
                    list_account.append(
                        {
                            "id": db_account.id,
                            "username": db_account.username,
                            "email": db_account.email,
                        }
                    )
            else:
                start = (page - 1) * page_size + 1
                list_account.append(
                    {
                        "id": db_account.id,
                        "username": db_account.username,
                        "email": db_account.email,
                        "role": db_account.role,
                    }
                )
        end = start + page_size
        if list_account[start:end] == []:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không có tồn tại tài khoản",
            )
        return list_account[start:end]
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="bạn không có quyền xem danh sách tài khoản",
        )


def login(db: Session, request):
    db_account = db.query(User).filter(User.username == request.username).first()
    if db_account:
        if not verify_password(request.password, db_account.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Mật khẩu sai"
            )
        return get_token(db_account)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Tài khoản không tồn tại"
        )


def admin_create(db: Session, request, token):
    if token["role"] == target.ADMIN:
        db_account = (
            db.query(User)
            .filter(
                or_(User.username == request.username, (User.email == request.email))
            )
            .first()
        )
        if db_account:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tài khoản hoặc email đã tồn tại",
            )
        if not request.password == request.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2 mật khẩu không giống nhau",
            )

        password_hash = hash_password(request.password)
        data_db = User(
            username=request.username,
            password=password_hash,
            email=request.email,
        )
        db.add(data_db)
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "message": "Bạn tạo tài khoản thành công",
                "username": request.username,
                "email": request.email,
                "role": target.USER,
            },
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền tạo tài khoản",
        )


def super_admin_create(db: Session, request, token):
    if token["role"] == target.SUPERADMIN:
        db_account = (
            db.query(User)
            .filter(
                or_(User.username == request.username, (User.email == request.email))
            )
            .first()
        )
        if db_account:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tài khoản hoặc email đã tồn tại",
            )
        if not request.password == request.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2 mật khẩu không giống nhau",
            )
        if request.role != target.USER and request.role != target.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Role không hợp lệ"
            )

        password_hash = hash_password(request.password)
        data_db = User(
            username=request.username,
            password=password_hash,
            email=request.email,
            role=request.role,
        )
        db.add(data_db)
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "message": "Bạn tạo tài khoản thành công",
                "username": request.username,
                "email": request.email,
                "role": request.role,
            },
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền tạo tài khoản",
        )


def check_password(change, password):
    if not verify_password(change.password, password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu cũ không chính xác",
        )
    if change.new_password == change.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu mới trùng với mật khẩu cũ",
        )
    if change.new_password != change.confirm_new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Mật khẩu mới không khớp"
        )


def change_password(change, db: Session, token):
    db_account = get_user_by_id(db, token["id"])
    check_password(change, db_account.password)
    new_password_hashed = hash_password(change.new_password)
    db_account.password = new_password_hashed
    db.merge(db_account)
    db.commit()
    return {"message": "Bạn đã đổi mật khẩu thành công"}


def delete(user_id, db: Session, token):
    db_account = get_user_by_id(db, token["id"])
    if db_account.role == target.SUPERADMIN:
        db_account_user = get_user_by_id(db, user_id)
        if db_account_user:
            if db_account_user.role == target.SUPERADMIN:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Bạn không thể xóa chính mình",
                )
            else:
                db.delete(db_account_user)
                db.commit()
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="tài khoản không tồn tại",
            )
    elif db_account.role == target.ADMIN:
        db_account_user = get_user_by_id(db, user_id)
        if (
            db_account_user.role == target.ADMIN
            or db_account_user.role == target.SUPERADMIN
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền xóa tài khoản này",
            )
        else:
            if db_account_user:
                db.delete(db_account_user)
                db.commit()
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="tài khoản không tồn tại",
                )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền xóa tài khoản",
        )
    return {"message": "Bạn xóa tài khoản của bạn thành công"}


def get_user_by_id(db: Session, request):
    return db.query(User).filter(User.id == request).first()
