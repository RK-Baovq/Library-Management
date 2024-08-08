from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from models.borrow import Borrow
from constants import target
from crud import crud_book
from datetime import date
from sqlalchemy import and_, or_


def read(db: Session, token, page, page_size):
    skip = (page - 1) * page_size
    if token["role"] == target.USER:
        db_borrow = (
            db.query(Borrow)
            .filter(Borrow.user_id == token["id"])
            .offset(skip)
            .limit(page_size)
            .all()
        )
    else:
        db_borrow = db.query(Borrow).offset(skip).limit(page_size).all()

    if db_borrow:
        return db_borrow
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Không có yêu cầu mượn sách"
        )


def create(book_id, request, db: Session, token):
    db_book = crud_book.get_book_by_id(db, book_id)
    if db_book:
        if request.borrow_date < date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Yêu cầu không hợp lệ"
            )
        if request.borrow_date > request.expected_payment_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ngày trả dự kiến không thể xảy ra trước ngày mượn",
            )

        db_borrows = (
            db.query(Borrow)
            .filter(
                and_(
                    Borrow.book_id == book_id,
                    or_(
                        Borrow.status == target.WAITING,
                        Borrow.status == target.BORROWING,
                    ),
                )
            )
            .all()
        )
        count = 0
        for db_borrow in db_borrows:
            if (
                db_borrow.borrow_date > request.expected_payment_date
                or db_borrow.expected_payment_date < request.borrow_date
            ):
                count += 1
        if db_book.available_quantity - len(db_borrows) + count > 0:
            data = Borrow(
                user_id=token["id"],
                book_id=book_id,
                borrow_date=request.borrow_date,
                expected_payment_date=request.expected_payment_date,
            )
            db.add(data)
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={
                    "message": "Bạn tạo yêu cầu mượn sách thành công",
                    "aaaa": "aaaa",
                },
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không thể có sách có sẵn để tạo yêu cầu",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tồn tại quyển sách cần tìm",
        )


# def change_status(borrow_id, borrow_status, db: Session, token):
#     db_borrow = get_borrow_by_id(db, borrow_id)
#     if db_borrow:
#         if token["role"] == target.USER:
#             if borrow_status == target.CANCEL:
#                 db_borrow.status = borrow_status
#                 db.merge(db_borrow)
#                 db.commit()
#                 return {"message": "Bạn hủy yêu cầu mượn sách thành công"}
#             else:
#                 raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bạn không có quyền thay đổi trạng thái yêu cầu")
#         else:
#             if borrow_status == target.BORROWING or borrow_status == target.RETURNED or borrow_status == target.WAITING or borrow_status == target.CANCEL:
#                 db_borrow.status = borrow_status
#                 db.merge(db_borrow)
#                 db.commit()
#             else:
#                 raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Trạng thái yêu câu không phù hợp")
#     else:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tồn tại yêu cầu mượn sách cần tìm")


def get_borrow_by_id(db: Session, request):
    return db.query(Borrow).filter(Borrow.id == request).first()
