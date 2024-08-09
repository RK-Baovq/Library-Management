from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from models.borrow import Borrow
from constants import target
from crud import crud_book
from datetime import date
from sqlalchemy import and_


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
    requests = {
        "borrow_date": request.borrow_date,
        "expected_payment_date": request.expected_payment_date,
    }
    count, available_book = check_book(book_id, requests, db)
    if available_book - count > 0:
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
                "user_id": token["id"],
                "book_id": book_id,
                "borrow_date": str(request.borrow_date),
                "expected_payment_date": str(request.expected_payment_date),
                "status": target.WAITING,
            },
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không thể có sách có sẵn để tạo yêu cầu",
        )


def user_update(borrow_id, borrow_update, db: Session, token):
    db_borrow = get_borrow_by_id(db, borrow_id)
    if db_borrow:
        if token["id"] == db_borrow.user_id:
            if borrow_update.status == target.CANCEL:
                db_borrow.status = borrow_update.status
                db.merge(db_borrow)
                db.commit()
                return {"message": "Bạn hủy yêu cầu mượn sách thành công"}
            else:
                if borrow_update.status == target.WAITING:
                    request = {
                        "borrow_date": borrow_update.borrow_date,
                        "expected_payment_date": borrow_update.expected_payment_date,
                    }
                    count, available_book = check_book(
                        borrow_update.book_id, request, db
                    )
                    if available_book - count > 0:
                        db_borrow.book_id = borrow_update.book_id
                        db_borrow.borrow_date = borrow_update.borrow_date
                        db_borrow.expected_payment_date = (
                            borrow_update.expected_payment_date
                        )
                        db.merge(db_borrow)
                        db.commit()
                        return {"message": "Bạn thay đổi thông tin yêu cầu thành công"}
                    else:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail="Không thể có sách có sẵn để tạo yêu cầu",
                        )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Trạng thái thay đổi không phù hợp",
                    )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không thể sửa yêu cầu của người khác",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tồn tại yêu cầu mượn sách cần tìm",
        )


def admin_update(borrow_id, borrow_status, db: Session, token):
    if token["role"] == target.USER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền thay đổi trạng thái",
        )
    else:
        db_borrow = get_borrow_by_id(db, borrow_id)
        if db_borrow:
            if borrow_status == target.BORROWING or borrow_status == target.CANCEL:
                if borrow_status == target.BORROWING:
                    request = {
                        "borrow_date": db_borrow.borrow_date,
                        "expected_payment_date": db_borrow.expected_payment_date,
                    }
                    count, available_book = check_book(db_borrow.book_id, request, db)
                    if available_book - count > 0:
                        db_borrow.status = borrow_status
                    else:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail="Không thể có sách có sẵn để tạo yêu cầu",
                        )
                else:
                    db_borrow.status = borrow_status
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Trạng thái thay đổi không phù hợp",
                )
            db.merge(db_borrow)
            db.commit()
            return {"message": "Bạn thay đổi thông tin yêu cầu thành công"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Không tồn tại yêu cầu"
            )


def check_book(book_id, request, db: Session):
    db_book = crud_book.get_book_by_id(db, book_id)
    if db_book:
        if request["borrow_date"] < date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Yêu cầu không hợp lệ"
            )
        if request["borrow_date"] > request["expected_payment_date"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ngày trả dự kiến không thể xảy ra trước ngày mượn",
            )
        db_borrows = (
            db.query(Borrow)
            .filter(
                and_(
                    Borrow.book_id == book_id,
                    Borrow.status == target.BORROWING,
                )
            )
            .all()
        )
        count = 0
        for db_borrow in db_borrows:
            if (
                db_borrow.borrow_date > request["expected_payment_date"]
                or db_borrow.expected_payment_date < request["borrow_date"]
            ):
                count += 1
        total = len(db_borrows)
        return total - count, db_book.available_quantity
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tồn tại quyển sách cần tìm",
        )


def get_borrow_by_id(db: Session, request):
    return db.query(Borrow).filter(Borrow.id == request).first()
