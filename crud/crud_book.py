from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from models.book import Book
from sqlalchemy import and_
from constants import target
from crud import crud_category


def read(request, db: Session, token, page, page_size):
    if (
        token["role"] == target.USER
        or token["role"] == target.ADMIN
        or token["role"] == target.SUPERADMIN
    ):
        skip = (page - 1) * page_size
        filters = []
        if request.name:
            filters.append(Book.name.ilike(f"%{request.name}%"))
        if request.author:
            filters.append(Book.author.ilike(f"%{request.author}%"))
        if request.category_id:
            db_category = crud_category.get_category_by_id(db, request.category_id)
            if db_category:
                filters.append(Book.category == request.category_id)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="danh mục không tồn tại",
                )
        if filters:
            books = (
                db.query(Book)
                .filter(and_(*filters))
                .offset(skip)
                .limit(page_size)
                .all()
            )
        else:
            books = db.query(Book).offset(skip).limit(page_size).all()
        if books:
            return [
                {
                    "id": book.id,
                    "name": book.name,
                    "author": book.author,
                    "category_id": book.category,
                }
                for book in books
            ]
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không có sách theo tên tìm kiếm",
            )


def create(request, db: Session, token):
    if token["role"] == target.ADMIN or token["role"] == target.SUPERADMIN:
        db_book = db.query(Book).filter(Book.name == request.name).first()
        if db_book:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Quyển sách đã tồn tại"
            )
        else:
            db_category = crud_category.get_category_by_id(db, request.category_id)
            if not db_category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Không có id danh mục phù hợp",
                )
            if request.available_quantity < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Số lượng không phù hợp",
                )
            data = Book(
                name=request.name,
                author=request.author,
                category=request.category_id,
                publishing_company=request.publishing_company,
                publication_date=request.publication_date,
                available_quantity=request.available_quantity,
                describe=request.describe,
            )
            db.add(data)
            db.commit()
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "message": "Bạn tạo quyển sách mới thành công",
                "name": request.name,
                "author": request.author,
                "category": request.category_id,
                "publishing_company": request.publishing_company,
                "publication_date": str(request.publication_date),
                "available_quantity": request.available_quantity,
                "describe": request.describe,
            },
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền tạo quyển sách mới",
        )


def update(book_id, request, db: Session, token):
    if token["role"] == target.ADMIN or token["role"] == target.SUPERADMIN:
        db_book = get_book_by_id(db, book_id)
        if db_book:
            if request.name is not None and request.name != "":
                db_book.name = request.name
            if request.author is not None and request.author != "":
                db_book.author = request.author
            if request.category_id is not None:
                db_category = crud_category.get_category_by_id(db, request.category_id)
                if db_category:
                    db_book.category_id = request.category_id
            if (
                request.publishing_company is not None
                and request.publishing_company != ""
            ):
                db_book.publishing_company = request.publishing_company
            if request.publication_date is not None:
                db_book.publication_date = request.publication_date
            if request.available_quantity is not None:
                if request.available_quantity < 0:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Số lượng không phù hợp",
                    )
                else:
                    db_book.available_quantity = request.available_quantity
            if request.describe is not None and request.describe != "":
                db_book.describe = request.describe

            db.merge(db_book)
            db.commit()
            return {"message": "Bạn thay đổi thông tin quyển sách thành công"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tồn tại id quyển sách cần tìm",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền sửa thông tin quyển sách",
        )


def delete(book_id, db: Session, token):
    if token["role"] == target.ADMIN or token["role"] == target.SUPERADMIN:
        db_book = get_book_by_id(db, book_id)
        if db_book:
            db.delete(db_book)
            db.commit()
            return {"message": "Bạn xóa quyển sách thành công"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tồn tại id quyển sách cần tìm",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền xóa quyển sách",
        )


def get_book_by_id(db: Session, request):
    return db.query(Book).filter(Book.id == request).first()
