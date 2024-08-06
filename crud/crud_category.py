from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from models.category import Category
from constants import target


def read(db: Session, token, page, page_size):
    if (
        token["role"] == target.USER
        or token["role"] == target.ADMIN
        or token["role"] == target.SUPERADMIN
    ):
        skip = (page - 1) * page_size
        db_category = db.query(Category).offset(skip).limit(page_size).all()
        if db_category:
            return db_category
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hiện tại không có danh mục nào",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Bạn không có quyền truy cập"
        )


def create(request, db: Session, token):
    if token["role"] == target.USER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền tạo danh mục mới",
        )
    else:
        request.name = request.name.lower()
        db_category = db.query(Category).filter(Category.name == request.name).first()
        if db_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Danh mục đã tồn tại"
            )
        else:
            data = Category(name=request.name)
            db.add(data)
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={"message": "Bạn tạo danh mục mới thành công"},
            )


def update(category_id, request, db: Session, token):
    if token["role"] == target.USER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền sửa danh mục",
        )
    else:
        db_category = get_category_by_id(db, category_id)
        request.name = request.name.lower()
        if db_category:
            if db_category.name == request.name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="danh mục mới trùng với danh mục cũ",
                )
            else:
                db_category.name = request.name
                db.merge(db_category)
                db.commit()
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không tồn tại danh mục muốn chỉnh sửa",
            )
    return {"message": "Bạn đã thay đổi danh mục thành công"}


def delete(category_id, db: Session, token):
    if token["role"] == target.USER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền xóa danh mục",
        )
    else:
        db_category = get_category_by_id(db, category_id)
        if db_category:
            db.delete(db_category)
            db.commit()
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không tồn tại danh mục muốn xóa",
            )
    return {"message": "Bạn xóa danh mục thành công"}


def get_category_by_id(db: Session, request):
    return db.query(Category).filter(Category.id == request).first()
